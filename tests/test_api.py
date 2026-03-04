"""Tests for the Flask API."""

import io

import pytest
from PIL import Image

from src.api.routes import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def _make_test_image_bytes(fmt="PNG"):
    img = Image.new("RGB", (100, 100), color=(128, 100, 80))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "dermascan"


class TestAnalyzeEndpoint:
    def test_no_file_returns_400(self, client):
        resp = client.post("/api/analyze")
        assert resp.status_code == 400

    def test_empty_filename_returns_400(self, client):
        resp = client.post(
            "/api/analyze",
            data={"image": (io.BytesIO(b""), "")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400

    def test_invalid_extension_returns_400(self, client):
        resp = client.post(
            "/api/analyze",
            data={"image": (io.BytesIO(b"data"), "file.pdf")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400

    def test_valid_image_returns_200(self, client):
        img_buf = _make_test_image_bytes()
        resp = client.post(
            "/api/analyze",
            data={"image": (img_buf, "test.png")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "top_conditions" in data
        assert "severity_score" in data
        assert "disclaimer" in data

    def test_result_has_3_conditions(self, client):
        img_buf = _make_test_image_bytes()
        resp = client.post(
            "/api/analyze",
            data={"image": (img_buf, "test.jpg")},
            content_type="multipart/form-data",
        )
        data = resp.get_json()
        assert len(data["top_conditions"]) == 3

    def test_severity_score_in_range(self, client):
        img_buf = _make_test_image_bytes()
        resp = client.post(
            "/api/analyze",
            data={"image": (img_buf, "test.png")},
            content_type="multipart/form-data",
        )
        data = resp.get_json()
        assert 1 <= data["severity_score"] <= 5


class TestIndexPage:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"DermScan" in resp.data
