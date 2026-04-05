"""Tests for public API endpoints that don't require Claude."""

import io

from PIL import Image


def _signup(client, email="bob@example.com"):
    return client.post("/api/auth/signup", json={
        "email": email, "password": "password123", "name": "Bob",
    })


def _img_bytes():
    img = Image.new("RGB", (80, 80), (120, 80, 70))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


class TestHealth:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["service"] == "dermascan"


class TestPlans:
    def test_plans_returns_all_tiers(self, client):
        resp = client.get("/api/plans")
        assert resp.status_code == 200
        plans = resp.get_json()["plans"]
        assert "free" in plans
        assert "pro" in plans
        assert "expert" in plans


class TestConditionsAPI:
    def test_list_conditions(self, client):
        resp = client.get("/api/conditions")
        assert resp.status_code == 200
        conds = resp.get_json()["conditions"]
        assert len(conds) >= 10
        assert all("name" in c and "category" in c for c in conds)

    def test_get_specific_condition(self, client):
        resp = client.get("/api/conditions/melanoma")
        assert resp.status_code == 200
        cond = resp.get_json()["condition"]
        assert cond["name"] == "Melanoma"
        assert cond["severity"] == 5
        assert len(cond["causes"]) > 0

    def test_unknown_condition(self, client):
        resp = client.get("/api/conditions/notathing")
        assert resp.status_code == 404


class TestAnalysisQuotaAndAuth:
    def test_start_requires_auth(self, client):
        resp = client.post("/api/analysis/start", data={
            "image": (_img_bytes(), "test.png"),
        }, content_type="multipart/form-data")
        assert resp.status_code == 401

    def test_list_requires_auth(self, client):
        resp = client.get("/api/analysis/conversations")
        assert resp.status_code == 401


class TestExpertChatGating:
    def test_expert_chat_requires_upgraded_plan(self, client):
        _signup(client)
        resp = client.get("/api/expert/chats")
        assert resp.status_code == 402

    def test_expert_chat_works_on_expert_plan(self, client):
        _signup(client)
        client.post("/api/auth/plan", json={"plan": "expert"})
        resp = client.get("/api/expert/chats")
        assert resp.status_code == 200
        assert resp.get_json()["chats"] == []

    def test_create_expert_chat(self, client):
        _signup(client)
        client.post("/api/auth/plan", json={"plan": "expert"})
        resp = client.post("/api/expert/chats", json={
            "subject": "Changing mole", "urgency": "urgent",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert "chat_id" in data
        assert "assigned_expert" in data

    def test_expert_chat_message_flow(self, client):
        _signup(client)
        client.post("/api/auth/plan", json={"plan": "expert"})
        created = client.post("/api/expert/chats", json={
            "subject": "Rash", "urgency": "routine",
        }).get_json()
        chat_id = created["chat_id"]
        # Fetch — should have the welcome message
        resp = client.get(f"/api/expert/chats/{chat_id}")
        assert resp.status_code == 200
        assert len(resp.get_json()["messages"]) >= 1
        # Post a user message
        resp = client.post(f"/api/expert/chats/{chat_id}/message", json={
            "content": "It's been itching for a week",
        })
        assert resp.status_code == 200
        # Should now have user msg + ack
        msgs = client.get(f"/api/expert/chats/{chat_id}").get_json()["messages"]
        assert len(msgs) >= 3


class TestPages:
    def test_index_renders(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"DermScan" in resp.data

    def test_spa_routes_render_shell(self, client):
        for path in ["/login", "/signup", "/dashboard", "/conditions", "/pricing", "/experts"]:
            resp = client.get(path)
            assert resp.status_code == 200
            assert b"DermScan" in resp.data
