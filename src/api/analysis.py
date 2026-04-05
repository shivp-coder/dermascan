"""Analysis API — multi-turn vision triage backed by Claude."""

import base64
import json
import sqlite3
import time

from flask import Blueprint, g, jsonify, request

from src import config
from src.auth import login_required
from src.db import get_db
from src.engine.claude_client import ClaudeEngineError, analyze_with_claude

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/analysis")


ALLOWED_MIME = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "bmp": "image/bmp",
    "tiff": "image/tiff",
}


def _check_quota(user: dict) -> tuple[bool, str]:
    plan = config.PLANS.get(user["plan"], config.PLANS["free"])
    limit = plan["monthly_scans"]
    if limit == -1:
        return True, ""
    if user["scans_used"] >= limit:
        return False, (
            f"You've reached your {plan['name']} plan limit of {limit} "
            "scans this period. Upgrade for more."
        )
    return True, ""


def _bump_scan_count(user_id: int) -> None:
    db = get_db()
    db.execute("UPDATE users SET scans_used = scans_used + 1 WHERE id = ?", (user_id,))
    db.commit()


def _load_history(conversation_id: int, user_id: int) -> list[dict]:
    """Load prior conversation as Anthropic-format messages.

    Image bytes are not replayed (they're stored but would blow up tokens);
    we preserve the user's text turns and assistant JSON replies for context.
    """
    db = get_db()
    conv = db.execute(
        "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
        (conversation_id, user_id),
    ).fetchone()
    if conv is None:
        return []
    rows = db.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id ASC",
        (conversation_id,),
    ).fetchall()
    history = []
    for row in rows:
        history.append({"role": row["role"], "content": row["content"]})
    return history


def _save_message(
    conversation_id: int,
    role: str,
    content: str,
    image_data: str | None = None,
) -> None:
    db = get_db()
    db.execute(
        "INSERT INTO messages (conversation_id, role, content, image_data) "
        "VALUES (?, ?, ?, ?)",
        (conversation_id, role, content, image_data),
    )
    db.execute(
        "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (conversation_id,),
    )
    db.commit()


@analysis_bp.get("/conversations")
@login_required
def list_conversations():
    rows = get_db().execute(
        "SELECT id, title, severity_score, status, created_at, updated_at "
        "FROM conversations WHERE user_id = ? ORDER BY updated_at DESC",
        (g.user["id"],),
    ).fetchall()
    return jsonify({"conversations": [dict(r) for r in rows]})


@analysis_bp.get("/conversations/<int:conv_id>")
@login_required
def get_conversation(conv_id: int):
    db = get_db()
    conv = db.execute(
        "SELECT * FROM conversations WHERE id = ? AND user_id = ?",
        (conv_id, g.user["id"]),
    ).fetchone()
    if conv is None:
        return jsonify({"error": "Not found"}), 404
    msgs = db.execute(
        "SELECT id, role, content, image_data, created_at FROM messages "
        "WHERE conversation_id = ? ORDER BY id ASC",
        (conv_id,),
    ).fetchall()
    return jsonify({
        "conversation": dict(conv),
        "messages": [dict(m) for m in msgs],
    })


@analysis_bp.post("/conversations/<int:conv_id>")
@login_required
def delete_conversation(conv_id: int):
    # Only allow delete via a POST with _method=delete for simplicity
    if request.args.get("_method") != "delete":
        return jsonify({"error": "Invalid"}), 400
    db = get_db()
    db.execute(
        "DELETE FROM conversations WHERE id = ? AND user_id = ?",
        (conv_id, g.user["id"]),
    )
    db.commit()
    return jsonify({"ok": True})


@analysis_bp.post("/start")
@login_required
def start_analysis():
    """Start a new analysis conversation with an image upload."""
    ok, reason = _check_quota(g.user)
    if not ok:
        return jsonify({"error": reason, "code": "quota_exceeded"}), 402

    if "image" not in request.files:
        return jsonify({"error": "Image file required"}), 400

    file = request.files["image"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_MIME:
        return jsonify({
            "error": f"Unsupported format. Accepted: {', '.join(ALLOWED_MIME)}"
        }), 400

    image_bytes = file.read()
    if len(image_bytes) > config.MAX_IMAGE_SIZE:
        return jsonify({"error": "Image too large (max 10MB)"}), 400

    user_text = (request.form.get("text") or "").strip()
    if not user_text:
        user_text = (
            "Please analyze this skin image and let me know what you see."
        )

    try:
        result = analyze_with_claude(
            history=[], user_text=user_text,
            image_bytes=image_bytes, image_media_type=ALLOWED_MIME[ext],
        )
    except ClaudeEngineError as e:
        return jsonify({"error": str(e), "code": "engine_error"}), 503

    db = get_db()
    severity = result.get("analysis", {}).get("severity_score", 1)
    conditions = result.get("analysis", {}).get("top_conditions", [])
    title = conditions[0]["name"] if conditions else "Skin analysis"

    cursor = db.execute(
        "INSERT INTO conversations (user_id, title, severity_score) VALUES (?, ?, ?)",
        (g.user["id"], title[:80], severity),
    )
    conv_id = cursor.lastrowid
    db.commit()

    image_b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    _save_message(
        conv_id, "user", user_text,
        image_data=f"data:{ALLOWED_MIME[ext]};base64,{image_b64}",
    )
    _save_message(conv_id, "assistant", json.dumps(result))
    _bump_scan_count(g.user["id"])

    return jsonify({
        "conversation_id": conv_id,
        "result": result,
    })


@analysis_bp.post("/conversations/<int:conv_id>/message")
@login_required
def follow_up(conv_id: int):
    """Continue the conversation with a follow-up message (optionally with an image)."""
    db = get_db()
    conv = db.execute(
        "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
        (conv_id, g.user["id"]),
    ).fetchone()
    if conv is None:
        return jsonify({"error": "Conversation not found"}), 404

    user_text = ""
    image_bytes = None
    media_type = "image/png"

    if request.content_type and request.content_type.startswith("multipart/"):
        user_text = (request.form.get("text") or "").strip()
        file = request.files.get("image")
        if file and file.filename:
            ext = file.filename.rsplit(".", 1)[-1].lower()
            if ext not in ALLOWED_MIME:
                return jsonify({"error": "Unsupported format"}), 400
            image_bytes = file.read()
            media_type = ALLOWED_MIME[ext]
    else:
        data = request.get_json(silent=True) or {}
        user_text = (data.get("text") or "").strip()

    if not user_text and image_bytes is None:
        return jsonify({"error": "Message text or image required"}), 400

    history = _load_history(conv_id, g.user["id"])

    try:
        result = analyze_with_claude(
            history=history, user_text=user_text or "Here's more detail.",
            image_bytes=image_bytes, image_media_type=media_type,
        )
    except ClaudeEngineError as e:
        return jsonify({"error": str(e), "code": "engine_error"}), 503

    image_data = None
    if image_bytes is not None:
        b64 = base64.standard_b64encode(image_bytes).decode("ascii")
        image_data = f"data:{media_type};base64,{b64}"

    _save_message(conv_id, "user", user_text, image_data=image_data)
    _save_message(conv_id, "assistant", json.dumps(result))

    # Update severity if escalated
    new_sev = result.get("analysis", {}).get("severity_score")
    if new_sev is not None:
        db.execute(
            "UPDATE conversations SET severity_score = ? WHERE id = ?",
            (new_sev, conv_id),
        )
        db.commit()

    return jsonify({"result": result})
