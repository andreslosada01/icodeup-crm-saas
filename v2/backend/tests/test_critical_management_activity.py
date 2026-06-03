from __future__ import annotations


def _first_customer(client, headers):
    response = client.get("/api/crm/customers?page=1&page_size=1", headers=headers)
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert items
    return items[0]


def test_agent_can_create_management_activity_for_assigned_customer(client, agent_headers):
    customer = _first_customer(client, agent_headers)
    response = client.post(
        f"/api/crm/customers/{customer['id']}/activities",
        headers=agent_headers,
        json={"channel": "phone", "result": "Contactado", "note": "Gestion critica test asignado."},
    )
    assert response.status_code == 201, response.text
    history = client.get(f"/api/crm/customers/{customer['id']}/activities", headers=agent_headers)
    assert history.status_code == 200, history.text
    assert any(item["note"] == "Gestion critica test asignado." for item in history.json())


def test_agent_cannot_create_management_activity_for_unassigned_customer(client, admin_headers, agent_headers, agent_session):
    response = client.get("/api/crm/customers?page=1&page_size=100", headers=admin_headers)
    assert response.status_code == 200, response.text
    agent_id = int(agent_session["user"]["id"])
    unassigned = next((item for item in response.json()["items"] if int(item.get("assigned_user_id") or 0) != agent_id), None)
    if unassigned is None:
        return
    response = client.post(
        f"/api/crm/customers/{unassigned['id']}/activities",
        headers=agent_headers,
        json={"channel": "phone", "result": "Contactado", "note": "Gestion no permitida."},
    )
    assert response.status_code == 403, response.text


def test_admin_can_create_management_activity_inside_tenant(client, admin_headers):
    customer = _first_customer(client, admin_headers)
    response = client.post(
        f"/api/crm/customers/{customer['id']}/activities",
        headers=admin_headers,
        json={"channel": "manual", "result": "Contactado", "note": "Gestion critica test admin."},
    )
    assert response.status_code == 201, response.text


def test_agent_role_has_operational_activity_permission(client, admin_headers):
    response = client.get("/api/governance/roles", headers=admin_headers)
    assert response.status_code == 200, response.text
    roles = response.json()
    collections_agent = next((role for role in roles if role.get("code") == "collections_agent"), None)
    assert collections_agent is not None
    permissions = set(collections_agent.get("permission_codes") or [])
    assert "crm.activities.create" in permissions
    assert "crm.clients.export" not in permissions
    assert "integrations.providers.manage" not in permissions
