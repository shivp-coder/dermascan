"""Tests for the Claude vision engine (without calling the real API)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.engine import claude_client
from src.engine.claude_client import (
    ClaudeEngineError,
    _extract_json,
    analyze_with_claude,
    build_image_block,
)


class TestExtractJson:
    def test_plain_json(self):
        data = _extract_json('{"message": "hi", "analysis": {}}')
        assert data["message"] == "hi"

    def test_fenced_json(self):
        text = '```json\n{"message": "ok", "a": 1}\n```'
        data = _extract_json(text)
        assert data["a"] == 1

    def test_json_with_surrounding_prose(self):
        text = 'Here is the result:\n{"x": 2}\nThanks!'
        data = _extract_json(text)
        assert data["x"] == 2

    def test_invalid_json_raises(self):
        with pytest.raises(ClaudeEngineError):
            _extract_json("no json here")


class TestBuildImageBlock:
    def test_produces_base64_block(self):
        block = build_image_block(b"hello", "image/png")
        assert block["type"] == "image"
        assert block["source"]["type"] == "base64"
        assert block["source"]["media_type"] == "image/png"
        assert block["source"]["data"]  # base64 encoded


class TestAnalyzeWithClaude:
    def _mock_response(self, json_text):
        block = MagicMock()
        block.type = "text"
        block.text = json_text
        resp = MagicMock()
        resp.content = [block]
        return resp

    def test_returns_parsed_dict(self, monkeypatch):
        monkeypatch.setattr(claude_client.config, "ANTHROPIC_API_KEY", "sk-test")
        mock_client = MagicMock()
        mock_client.messages.create.return_value = self._mock_response(json.dumps({
            "message": "Looks benign",
            "analysis": {
                "top_conditions": [
                    {"name": "Benign Nevus", "confidence_percent": 70, "why": "uniform"},
                ],
                "severity_score": 1,
                "severity_label": "Very Mild",
                "abcde": {},
                "next_steps": ["Monitor"],
                "doctor_recommendation": "Monitor; see doc if it changes.",
                "needs_urgent_care": False,
            },
            "follow_up_questions": ["How long?"],
            "escalate_to_expert": False,
            "disclaimer": "Not a diagnosis.",
        }))
        monkeypatch.setattr(
            claude_client, "_get_client", lambda: mock_client
        )

        result = analyze_with_claude(
            history=[], user_text="Look at this",
            image_bytes=b"fakeimage", image_media_type="image/png",
        )
        assert result["message"] == "Looks benign"
        assert result["analysis"]["severity_score"] == 1
        assert result["escalate_to_expert"] is False

    def test_missing_keys_get_defaults(self, monkeypatch):
        monkeypatch.setattr(claude_client.config, "ANTHROPIC_API_KEY", "sk-test")
        mock_client = MagicMock()
        mock_client.messages.create.return_value = self._mock_response('{"message": "ok"}')
        monkeypatch.setattr(claude_client, "_get_client", lambda: mock_client)

        result = analyze_with_claude(history=[], user_text="hi", image_bytes=None)
        assert "analysis" in result
        assert "follow_up_questions" in result
        assert "disclaimer" in result

    def test_missing_api_key_raises(self, monkeypatch):
        monkeypatch.setattr(claude_client.config, "ANTHROPIC_API_KEY", "")
        with pytest.raises(ClaudeEngineError):
            analyze_with_claude(history=[], user_text="hi")

    def test_empty_response_raises(self, monkeypatch):
        monkeypatch.setattr(claude_client.config, "ANTHROPIC_API_KEY", "sk-test")
        mock_client = MagicMock()
        empty_resp = MagicMock()
        empty_resp.content = []
        mock_client.messages.create.return_value = empty_resp
        monkeypatch.setattr(claude_client, "_get_client", lambda: mock_client)
        with pytest.raises(ClaudeEngineError):
            analyze_with_claude(history=[], user_text="hi")
