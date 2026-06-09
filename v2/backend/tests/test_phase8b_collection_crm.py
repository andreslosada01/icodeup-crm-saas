from __future__ import annotations


def test_agent_can_create_management_activity(client, agent_headers):
    customers = client.get("/api/crm/customers?page_size=1", headers=agent_headers)
    assert customers.status_code == 200, customers.text
    items = customers.json()["items"]
    assert items
    customer_id = items[0]["id"]
    response = client.post(
        f"/api/crm/customers/{customer_id}/activities",
        headers=agent_headers,
        json={"channel": "phone", "result": "Contactado", "note": "Gestion demo test automatizado."},
    )
    assert response.status_code == 201, response.text
    history = client.get(f"/api/crm/customers/{customer_id}/activities", headers=agent_headers)
    assert history.status_code == 200, history.text
    assert any(item["note"] == "Gestion demo test automatizado." for item in history.json())


def test_admin_can_read_typification_trees(client, admin_headers):
    response = client.get("/api/typifications/trees", headers=admin_headers)
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_admin_can_read_collection_operational_modules(client, admin_headers):
    for path in [
        "/api/recordings",
        "/api/uploads/batches",
        "/api/uploads/demographics",
        "/api/excel-web/sources",
        "/api/integrations/providers",
        "/api/integrations/channels",
    ]:
        response = client.get(path, headers=admin_headers)
        assert response.status_code == 200, f"{path}: {response.status_code} {response.text}"


def test_excel_web_query_is_safe_and_tenant_scoped(client, admin_headers):
    response = client.post("/api/excel-web/query", headers=admin_headers, json={"source": "customers", "page": 1, "page_size": 5, "filters": {}, "columns": ["name", "document", "risk"]})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["source"] == "customers"
    assert payload["page_size"] == 5
    assert set(payload["columns"]) <= {"name", "document", "risk"}


def test_agent_cannot_export_excel_web(client, agent_headers):
    response = client.post("/api/excel-web/export", headers=agent_headers, json={"source": "customers", "page": 1, "page_size": 5, "filters": {}, "columns": ["name"]})
    assert response.status_code == 403, response.text
