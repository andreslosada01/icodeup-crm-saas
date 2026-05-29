from __future__ import annotations

from .conftest import menu_ids


def test_module_disabled_blocks_url_and_menu(client, platform_headers, admin_headers, admin_tenant_id):
    disable_payload = [{"module_code": "sales", "enabled": False, "configuration_json": None}]
    enable_payload = [{"module_code": "sales", "enabled": True, "configuration_json": None}]
    try:
        disabled = client.put(f"/api/governance/modules/{admin_tenant_id}", json=disable_payload, headers=platform_headers)
        assert disabled.status_code == 200, disabled.text
        response = client.get("/api/sales/leads", headers=admin_headers)
        assert response.status_code == 403
        assert "sales" not in menu_ids(client, admin_headers)
    finally:
        restored = client.put(f"/api/governance/modules/{admin_tenant_id}", json=enable_payload, headers=platform_headers)
        assert restored.status_code == 200, restored.text


def test_module_enabled_allows_access_when_permission_exists(client, admin_headers):
    response = client.get("/api/sales/leads", headers=admin_headers)
    assert response.status_code == 200, response.text
