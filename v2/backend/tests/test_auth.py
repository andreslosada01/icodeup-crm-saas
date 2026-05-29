from __future__ import annotations

from .conftest import AGENT_EMAIL, PLATFORM_EMAIL, PLATFORM_PASSWORD, TENANT_ADMIN_EMAIL, TENANT_PASSWORD


def test_login_success_platform_admin(client):
    response = client.post("/api/auth/login", json={"email": PLATFORM_EMAIL, "password": PLATFORM_PASSWORD})
    assert response.status_code == 200, response.text
    assert response.json()["user"]["is_platform_admin"] is True


def test_login_success_tenant_admin(client):
    response = client.post("/api/auth/login", json={"email": TENANT_ADMIN_EMAIL, "password": TENANT_PASSWORD})
    assert response.status_code == 200, response.text
    assert response.json()["user"]["is_company_admin"] is True


def test_login_success_agent(client):
    response = client.post("/api/auth/login", json={"email": AGENT_EMAIL, "password": TENANT_PASSWORD})
    assert response.status_code == 200, response.text
    assert response.json()["user"]["role"] == "agent"


def test_login_failed_wrong_password(client):
    response = client.post("/api/auth/login", json={"email": TENANT_ADMIN_EMAIL, "password": "wrong-password"})
    assert response.status_code == 401
