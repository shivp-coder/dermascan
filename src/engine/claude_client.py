"""Claude vision-powered triage engine.

Uses Claude Opus 4.6 with vision to analyze skin images and hold a
multi-turn conversation with the user, building on prior context.
"""

from __future__ import annotations

import base64
import json
from typing import Any

import anthropic

from src import config
from src.engine.prompts import SYSTEM_PROMPT


class ClaudeEngineError(Exception):
    pass


def _get_client() -> anthropic.Anthropic:
    if not config.ANTHROPIC_API_KEY:
        raise ClaudeEngineError(
            "ANTHROPIC_API_KEY not configured. Set it in .env to enable AI analysis."
        )
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def build_image_block(image_bytes: bytes, media_type: str = "image/png") -> dict:
    """Build an image content block for the Messages API."""
    data = base64.standard_b64encode(image_bytes).decode("utf-8")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": data,
        },
    }


def _extract_json(text: str) -> dict:
    """Extract the first JSON object from the model's response."""
    text = text.strip()
    # If fenced, strip fences
    if text.startswith("```"):
        text = text.strip("`")
        # Drop possible language marker on first line
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    # Find first { to last }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ClaudeEngineError("Model returned no JSON payload")
    return json.loads(text[start : end + 1])


def analyze_with_claude(
    history: list[dict[str, Any]],
    user_text: str,
    image_bytes: bytes | None = None,
    image_media_type: str = "image/png",
) -> dict:
    """Run a triage turn with Claude vision.

    Args:
        history: Prior conversation as a list of {"role", "content"} dicts
                 in Anthropic format. Image bytes are NOT replayed — only
                 text from history is kept to save tokens.
        user_text: The current user message.
        image_bytes: Optional new image to analyze this turn.
        image_media_type: MIME type of the image.

    Returns:
        Parsed JSON dict matching the schema in SYSTEM_PROMPT.
    """
    client = _get_client()

    # Build the new user message content
    content: list[dict[str, Any]] = []
    if image_bytes is not None:
        content.append(build_image_block(image_bytes, image_media_type))
    content.append({
        "type": "text",
        "text": user_text or "Please analyze this image.",
    })

    messages = list(history) + [{"role": "user", "content": content}]

    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    text = next(
        (b.text for b in response.content if getattr(b, "type", None) == "text"),
        "",
    )
    if not text:
        raise ClaudeEngineError("Empty response from Claude")

    try:
        parsed = _extract_json(text)
    except (ValueError, json.JSONDecodeError) as e:
        raise ClaudeEngineError(f"Failed to parse model JSON: {e}") from e

    # Ensure required keys exist with safe defaults
    parsed.setdefault("message", "")
    parsed.setdefault(
        "analysis",
        {
            "top_conditions": [],
            "severity_score": 1,
            "severity_label": "Very Mild",
            "abcde": {},
            "next_steps": [],
            "doctor_recommendation": "",
            "needs_urgent_care": False,
        },
    )
    parsed.setdefault("follow_up_questions", [])
    parsed.setdefault("escalate_to_expert", False)
    parsed.setdefault(
        "disclaimer",
        "This analysis is for informational purposes only and does not "
        "constitute a medical diagnosis. Please consult a qualified "
        "healthcare professional.",
    )

    return parsed


def ask_condition_info(condition_name: str) -> str:
    """Ask Claude for a structured summary of a specific condition."""
    client = _get_client()
    prompt = f"""Give a concise, patient-friendly summary of the skin condition
"{condition_name}". Cover: what it is, typical appearance, common causes,
typical severity, basic self-care, and when to see a doctor. 180-260 words,
plain text, no markdown headers. Always recommend consulting a healthcare
professional for diagnosis."""
    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return next(
        (b.text for b in response.content if getattr(b, "type", None) == "text"),
        "",
    )
