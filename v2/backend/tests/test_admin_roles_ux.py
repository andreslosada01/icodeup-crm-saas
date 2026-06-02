from __future__ import annotations

import pytest


def _first_user_id(client, headers, tenant_id: int | None = None) -> int:
    suffix = f"?tenant_id={tenant_id}" if tenant_id else ""
    response = client.get(f"/api/governance/users{suffix}", headers=headers)
    assert response.status_code == 200, response.text
    users = response.json()
    if not users:
        pytest.skip("No users available for effective-access checks.")
    return int(users[0]["id"])


def test_platform_admin_can_consult_effective_access_for_tenant_user(client, platform_headers, admin_tenant_id):
    user_id = _first_user_id(client, platform_headers, admin_tenant_id)
    response = client.get(f"/api/governance/users/{user_id}/effective-access", headers=platform_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["user"]["id"] == user_id
    assert "legacy_role" in payload
    assert "specialized_role" in payload
    assert "permissions" in payload
    assert "modules" in payload


def test_tenant_admin_can_consult_own_tenant_effective_access(client, admin_headers):
    user_id = _first_user_id(client, admin_headers)
    response = client.get(f"/api/governance/users/{user_id}/effective-access", headers=admin_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["tenant"]["id"]
    assert isinstance(payload["restrictions"], list)
    assert isinstance(payload["risk_flags"], list)


def test_tenant_admin_cannot_consult_other_tenant_effective_access(client, platform_headers, admin_headers, other_tenant_id):
    user_id = _first_user_id(client, platform_headers, other_tenant_id)
    response = client.get(f"/api/governance/users/{user_id}/effective-access", headers=admin_headers)
    assert response.status_code == 403


def test_operational_user_cannot_consult_effective_access(client, agent_headers, admin_headers):
    user_id = _first_user_id(client, admin_headers)
    response = client.get(f"/api/governance/users/{user_id}/effective-access", headers=agent_headers)
    assert response.status_code == 403


def test_security_insights_are_admin_only(client, platform_headers, admin_headers, agent_headers):
    assert client.get("/api/governance/security-insights", headers=platform_headers).status_code == 200
    assert client.get("/api/governance/security-insights", headers=admin_headers).status_code == 200
    assert client.get("/api/governance/security-insights", headers=agent_headers).status_code == 403


def test_reserved_permissions_are_not_exposed_to_tenant_admin(client, admin_headers):
    response = client.get("/api/governance/permissions", headers=admin_headers)
    assert response.status_code == 200, response.text
    codes = {item["code"] for item in response.json()}
    assert not any(code.startswith("platform.") for code in codes)
    assert "modules.configure" not in codes
    assert "health.view" not in codes


def test_specialized_roles_are_visible_in_user_list(client, admin_headers):
    response = client.get("/api/governance/users", headers=admin_headers)
    assert response.status_code == 200, response.text
    users = response.json()
    by_email = {item["email"]: item for item in users}
    lawyer = by_email.get("abogado.andina@demo.icodeup.local")
    sales = by_email.get("comercial.andina@demo.icodeup.local")
    if not lawyer or not sales:
        pytest.skip("Phase 5 demo users not available.")
    assert lawyer["specialized_role_code"] == "lawyer"
    assert sales["specialized_role_code"] == "sales_advisor"
