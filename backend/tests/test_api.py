"""
FailSafe — Backend Tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def client():
    with patch("app.models.database.create_tables"), \
         patch("app.services.ml_service.ml_service.load"):
        from main import app
        return TestClient(app)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_register_and_login(client):
    # Register
    res = client.post("/api/auth/register", json={
        "email": "test@test.com",
        "password": "test1234",
        "full_name": "Test User",
        "role": "faculty",
    })
    assert res.status_code in (201, 400)  # 400 if already exists

    # Login
    res = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "test1234",
    })
    if res.status_code == 200:
        assert "access_token" in res.json()


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", json={
        "email": "nobody@test.com",
        "password": "wrong",
    })
    assert res.status_code == 401


def test_predict_requires_auth(client):
    res = client.post("/api/predict/", json={"students": []})
    assert res.status_code == 401


def test_dashboard_requires_auth(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 401
