"""Pytest fixtures shared across tests."""

import os
import tempfile

import pytest

# Use an in-memory-ish temp DB for tests
_tmpdir = tempfile.mkdtemp(prefix="dermascan_test_")
os.environ.setdefault("DATABASE_PATH", os.path.join(_tmpdir, "test.db"))
os.environ.setdefault("SECRET_KEY", "test-secret")

from src import config  # noqa: E402
from src.api.routes import create_app  # noqa: E402
from src.db import init_db  # noqa: E402


@pytest.fixture
def app():
    # Fresh DB per test
    if os.path.exists(config.DATABASE_PATH):
        os.remove(config.DATABASE_PATH)
    init_db()
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
