"""User authentication: session-based with hashed passwords."""

from functools import wraps

from flask import Blueprint, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from src import config
from src.db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        user = _load_user(session["user_id"])
        if user is None:
            session.clear()
            return jsonify({"error": "Invalid session"}), 401
        g.user = user
        return f(*args, **kwargs)

    return wrapper


def _load_user(user_id: int):
    row = get_db().execute(
        "SELECT id, email, name, plan, scans_used, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


def _sanitize_user(user: dict) -> dict:
    plan_key = user.get("plan", "free")
    plan = config.PLANS.get(plan_key, config.PLANS["free"])
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "plan": plan_key,
        "plan_name": plan["name"],
        "scans_used": user["scans_used"],
        "scans_limit": plan["monthly_scans"],
        "expert_chat_enabled": plan["expert_chat"],
    }


@auth_bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()

    if not email or "@" not in email:
        return jsonify({"error": "Valid email required"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if not name:
        return jsonify({"error": "Name required"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        return jsonify({"error": "An account with that email already exists"}), 409

    password_hash = generate_password_hash(password)
    cursor = db.execute(
        "INSERT INTO users (email, password_hash, name, plan) VALUES (?, ?, ?, 'free')",
        (email, password_hash, name),
    )
    db.commit()
    user_id = cursor.lastrowid
    session["user_id"] = user_id
    return jsonify({"user": _sanitize_user(_load_user(user_id))}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    row = get_db().execute(
        "SELECT id, password_hash FROM users WHERE email = ?", (email,)
    ).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = row["id"]
    return jsonify({"user": _sanitize_user(_load_user(row["id"]))})


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@auth_bp.get("/me")
def me():
    if "user_id" not in session:
        return jsonify({"user": None})
    user = _load_user(session["user_id"])
    if user is None:
        session.clear()
        return jsonify({"user": None})
    return jsonify({"user": _sanitize_user(user)})


@auth_bp.post("/plan")
@login_required
def change_plan():
    data = request.get_json(silent=True) or {}
    new_plan = data.get("plan")
    if new_plan not in config.PLANS:
        return jsonify({"error": "Invalid plan"}), 400
    db = get_db()
    db.execute("UPDATE users SET plan = ? WHERE id = ?", (new_plan, g.user["id"]))
    db.commit()
    return jsonify({"user": _sanitize_user(_load_user(g.user["id"]))})
