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
    assert "excel_web.view" in permissions
    assert "excel_web.query" in permissions
    assert "excel_web.views.manage" in permissions
    assert "excel_web.export" not in permissions
    assert "integrations.providers.manage" not in permissions


def test_agent_menu_hides_non_demo_operational_modules(client, agent_headers):
    response = client.get("/api/menu/me", headers=agent_headers)
    assert response.status_code == 200, response.text
    sections = {item["section"] for item in response.json().get("items", [])}
    assert "recordings" not in sections
    assert "excel-web" in sections
    assert "uploads" not in sections
    assert "integrations" not in sections
    assert "configuration" not in sections


def test_agent_can_access_scoped_excel_web_but_not_recordings(client, agent_headers):
    response = client.get("/api/excel-web/sources", headers=agent_headers)
    assert response.status_code == 200, response.text
    source_codes = {item["code"] for item in response.json()}
    assert "customers" in source_codes
    assert "obligations" in source_codes
    assert "recordings" not in source_codes
    response = client.post(
        "/api/excel-web/query",
        headers=agent_headers,
        json={"source": "customers", "filters": {}, "columns": ["id", "assigned_user_id", "name"], "page": 1, "page_size": 20},
    )
    assert response.status_code == 200, response.text
    rows = response.json()["rows"]
    assert rows
    agent_id = rows[0]["assigned_user_id"]
    assert all(row["assigned_user_id"] == agent_id for row in rows)
    response = client.get("/api/recordings", headers=agent_headers)
    assert response.status_code == 403, response.text


def test_excel_web_limits_page_size_and_persists_agent_sheet_rows(client, agent_headers):
    response = client.post(
        "/api/excel-web/query",
        headers=agent_headers,
        json={"source": "customers", "filters": {}, "columns": ["id", "assigned_user_id", "name"], "page": 1, "page_size": 20},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["page_size"] <= 20
    assert len(payload["rows"]) <= 20

    create = client.post(
        "/api/excel-web/sheet-rows",
        headers=agent_headers,
        json={
            "date": "2026-06-03",
            "portfolio": "Cartera demo test",
            "customer_name": "Cliente Demo Hoja Test",
            "document": "DEMO-SHEET-001",
            "obligation_number": "OBL-SHEET-001",
            "management_note": "Seguimiento operativo test.",
            "commitment": "Confirmar pago demo.",
            "amount": 150000,
            "status": "Seguimiento",
            "next_action_at": "2026-06-05T00:00:00Z",
        },
    )
    assert create.status_code == 201, create.text
    row_id = create.json()["id"]
    listing = client.get("/api/excel-web/sheet-rows?page_size=20", headers=agent_headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["page_size"] <= 20
    assert any(item["id"] == row_id for item in listing.json()["items"])
