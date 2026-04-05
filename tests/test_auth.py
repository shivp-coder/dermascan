"""Tests for auth and plan management."""


def _signup(client, email="alice@example.com", password="password123", name="Alice"):
    return client.post("/api/auth/signup", json={
        "email": email, "password": password, "name": name,
    })


class TestSignup:
    def test_signup_creates_user(self, client):
        resp = _signup(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["user"]["email"] == "alice@example.com"
        assert data["user"]["plan"] == "free"
        assert data["user"]["scans_used"] == 0

    def test_signup_short_password(self, client):
        resp = client.post("/api/auth/signup", json={
            "email": "a@b.com", "password": "short", "name": "A",
        })
        assert resp.status_code == 400

    def test_signup_invalid_email(self, client):
        resp = client.post("/api/auth/signup", json={
            "email": "notanemail", "password": "password123", "name": "A",
        })
        assert resp.status_code == 400

    def test_duplicate_email(self, client):
        _signup(client)
        resp = _signup(client)
        assert resp.status_code == 409


class TestLogin:
    def test_login_success(self, client):
        _signup(client)
        resp = client.post("/api/auth/login", json={
            "email": "alice@example.com", "password": "password123",
        })
        assert resp.status_code == 200
        assert resp.get_json()["user"]["email"] == "alice@example.com"

    def test_login_wrong_password(self, client):
        _signup(client)
        resp = client.post("/api/auth/login", json={
            "email": "alice@example.com", "password": "wrongpass",
        })
        assert resp.status_code == 401

    def test_login_unknown_user(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "ghost@example.com", "password": "password123",
        })
        assert resp.status_code == 401


class TestSession:
    def test_me_unauth(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        assert resp.get_json()["user"] is None

    def test_me_after_signup(self, client):
        _signup(client)
        resp = client.get("/api/auth/me")
        assert resp.get_json()["user"]["email"] == "alice@example.com"

    def test_logout(self, client):
        _signup(client)
        client.post("/api/auth/logout")
        resp = client.get("/api/auth/me")
        assert resp.get_json()["user"] is None


class TestPlanChange:
    def test_upgrade_to_pro(self, client):
        _signup(client)
        resp = client.post("/api/auth/plan", json={"plan": "pro"})
        assert resp.status_code == 200
        assert resp.get_json()["user"]["plan"] == "pro"

    def test_upgrade_to_expert_enables_chat(self, client):
        _signup(client)
        resp = client.post("/api/auth/plan", json={"plan": "expert"})
        assert resp.get_json()["user"]["expert_chat_enabled"] is True

    def test_invalid_plan(self, client):
        _signup(client)
        resp = client.post("/api/auth/plan", json={"plan": "ultra"})
        assert resp.status_code == 400

    def test_plan_change_requires_auth(self, client):
        resp = client.post("/api/auth/plan", json={"plan": "pro"})
        assert resp.status_code == 401
