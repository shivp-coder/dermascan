"""Expert chat API — for escalated / serious cases.

In production this would route to verified dermatologists. For now we
store the conversation threads and simulate expert acknowledgements so
the product surface is complete.
"""

from flask import Blueprint, g, jsonify, request

from src import config
from src.auth import login_required
from src.db import get_db

expert_bp = Blueprint("expert", __name__, url_prefix="/api/expert")


MOCK_EXPERTS = [
    "Dr. Priya Shah, MD (Dermatology)",
    "Dr. James Okafor, MD (Dermatology)",
    "Dr. Elena Rossi, MD (Dermato-oncology)",
    "Dr. Mei Tanaka, MD (Pediatric Derm)",
]


def _require_expert_tier():
    plan = config.PLANS.get(g.user["plan"], config.PLANS["free"])
    if not plan["expert_chat"]:
        return jsonify({
            "error": "Expert chat requires the Expert+ plan",
            "code": "upgrade_required",
        }), 402
    return None


@expert_bp.get("/chats")
@login_required
def list_chats():
    err = _require_expert_tier()
    if err:
        return err
    rows = get_db().execute(
        "SELECT id, subject, urgency, status, assigned_expert, created_at "
        "FROM expert_chats WHERE user_id = ? ORDER BY created_at DESC",
        (g.user["id"],),
    ).fetchall()
    return jsonify({"chats": [dict(r) for r in rows]})


@expert_bp.post("/chats")
@login_required
def create_chat():
    err = _require_expert_tier()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip() or "General consultation"
    urgency = data.get("urgency") or "routine"
    conversation_id = data.get("conversation_id")
    if urgency not in ("routine", "priority", "urgent"):
        urgency = "routine"

    # Deterministic expert rotation so the same user sees consistent names
    expert = MOCK_EXPERTS[g.user["id"] % len(MOCK_EXPERTS)]

    db = get_db()
    cursor = db.execute(
        "INSERT INTO expert_chats "
        "(user_id, conversation_id, subject, urgency, status, assigned_expert) "
        "VALUES (?, ?, ?, ?, 'active', ?)",
        (g.user["id"], conversation_id, subject[:200], urgency, expert),
    )
    chat_id = cursor.lastrowid

    # Seed with an auto-welcome from the assigned expert
    welcome_by_urgency = {
        "urgent": (
            f"Hi {g.user['name'].split()[0]}, this is {expert}. I see this was "
            "flagged urgent — I'm reviewing your case now. In the meantime, "
            "please avoid sun exposure to the area and don't attempt any "
            "self-treatment. Can you tell me how long you've noticed the "
            "lesion and whether it's changed recently?"
        ),
        "priority": (
            f"Hi, I'm {expert}. I've received your case and will review the "
            "images shortly. Could you share any additional symptoms, and "
            "let me know whether this is something new or has been present "
            "for a while?"
        ),
        "routine": (
            f"Hello, I'm {expert}. Thanks for reaching out. I'll look over "
            "your case and get back to you within 24 hours. Feel free to add "
            "any extra context or questions here."
        ),
    }
    db.execute(
        "INSERT INTO expert_messages (expert_chat_id, sender, content) "
        "VALUES (?, 'expert', ?)",
        (chat_id, welcome_by_urgency[urgency]),
    )
    db.commit()
    return jsonify({"chat_id": chat_id, "assigned_expert": expert}), 201


@expert_bp.get("/chats/<int:chat_id>")
@login_required
def get_chat(chat_id: int):
    err = _require_expert_tier()
    if err:
        return err
    db = get_db()
    chat = db.execute(
        "SELECT * FROM expert_chats WHERE id = ? AND user_id = ?",
        (chat_id, g.user["id"]),
    ).fetchone()
    if chat is None:
        return jsonify({"error": "Not found"}), 404
    msgs = db.execute(
        "SELECT id, sender, content, created_at FROM expert_messages "
        "WHERE expert_chat_id = ? ORDER BY id ASC",
        (chat_id,),
    ).fetchall()
    return jsonify({
        "chat": dict(chat),
        "messages": [dict(m) for m in msgs],
    })


@expert_bp.post("/chats/<int:chat_id>/message")
@login_required
def send_message(chat_id: int):
    err = _require_expert_tier()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Message required"}), 400

    db = get_db()
    chat = db.execute(
        "SELECT assigned_expert FROM expert_chats WHERE id = ? AND user_id = ?",
        (chat_id, g.user["id"]),
    ).fetchone()
    if chat is None:
        return jsonify({"error": "Not found"}), 404

    db.execute(
        "INSERT INTO expert_messages (expert_chat_id, sender, content) "
        "VALUES (?, 'user', ?)",
        (chat_id, content),
    )
    # Acknowledgement from the expert. In production this is a notification
    # to a real dermatologist; here we send an ack so the UX is complete.
    ack = (
        f"Thanks for the additional info. {chat['assigned_expert']} has been "
        "notified and will reply as soon as possible. For anything that feels "
        "truly urgent, please also contact your local healthcare provider or "
        "emergency services."
    )
    db.execute(
        "INSERT INTO expert_messages (expert_chat_id, sender, content) "
        "VALUES (?, 'system', ?)",
        (chat_id, ack),
    )
    db.commit()
    return jsonify({"ok": True})
