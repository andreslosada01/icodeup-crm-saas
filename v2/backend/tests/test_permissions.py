from __future__ import annotations


def test_user_without_permission_receives_403(client, agent_headers):
    response = client.get("/api/governance/roles", headers=agent_headers)
    assert response.status_code == 403


def test_agent_cannot_export_customers(client, agent_headers):
    response = client.get("/api/crm/customers/export", headers=agent_headers)
    assert response.status_code == 403


def test_agent_cannot_export_payments(client, agent_headers):
    response = client.get("/api/crm/payments/export", headers=agent_headers)
    assert response.status_code == 403


def test_tenant_admin_cannot_assign_reserved_permission(client, admin_headers):
    payload = {
        "name": "Reserved Permission Test",
        "code": "reserved_permission_test",
        "description": "Should be blocked for tenant admins.",
        "permission_codes": ["platform.governance.configure"],
    }
    response = client.post("/api/governance/roles", json=payload, headers=admin_headers)
    assert response.status_code == 403


def test_platform_admin_can_see_governance_global(client, platform_headers):
    response = client.get("/api/governance/subscriptions", headers=platform_headers)
    assert response.status_code == 200, response.text
