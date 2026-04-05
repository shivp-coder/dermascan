"""Application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Claude API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-opus-4-6"

# Database
DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "dermascan.db"))

# Uploads
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff", "webp"}

# Plan tiers
PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "monthly_scans": 5,
        "expert_chat": False,
        "history_days": 7,
        "features": [
            "5 AI scans per month",
            "Basic condition info",
            "7-day history",
        ],
    },
    "pro": {
        "name": "Pro",
        "price": 19,
        "monthly_scans": 100,
        "expert_chat": False,
        "history_days": 365,
        "features": [
            "100 AI scans per month",
            "Full condition library",
            "Multi-turn analysis",
            "1-year history",
            "Priority response",
        ],
    },
    "expert": {
        "name": "Expert+",
        "price": 49,
        "monthly_scans": -1,  # unlimited
        "expert_chat": True,
        "history_days": -1,  # unlimited
        "features": [
            "Unlimited AI scans",
            "Chat with dermatologists",
            "Urgent case escalation",
            "Unlimited history",
            "Priority expert matching",
        ],
    },
}
