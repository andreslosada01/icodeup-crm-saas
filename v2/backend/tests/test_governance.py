from __future__ import annotations

from .conftest import menu_ids


def test_platform_admin_menu_shows_governance(client, platform_headers):
    ids = menu_ids(client, platform_headers)
    assert "governance" in ids
    assert "subscriptions" in ids


def test_tenant_admin_menu_hides_global_governance(client, admin_headers):
    ids = menu_ids(client, admin_headers)
    assert "governance" not in ids
    assert "subscriptions" not in ids
    assert "tenant-settings" in ids


def test_operational_user_menu_hides_administration(client, agent_headers):
    ids = menu_ids(client, agent_headers)
    assert "governance" not in ids
    assert "roles-permissions" not in ids
    assert "queue" in ids


def test_tenant_admin_cannot_see_global_subscription_inventory(client, admin_headers):
    response = client.get("/api/governance/subscriptions", headers=admin_headers)
    assert response.status_code == 403


def test_tenant_admin_can_see_own_settings(client, admin_headers):
    response = client.get("/api/governance/settings", headers=admin_headers)
    assert response.status_code == 200, response.text
