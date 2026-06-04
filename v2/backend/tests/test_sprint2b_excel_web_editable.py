from __future__ import annotations


def test_agent_creates_and_updates_editable_sheet_row(client, agent_headers):
    create = client.post(
        "/api/excel-web/sheet-rows",
        headers=agent_headers,
        json={
            "date": "2026-06-03",
            "portfolio": "Sprint 2B cartera",
            "customer_name": "Cliente Sprint 2B",
            "document": "SPRINT2B-001",
            "obligation_number": "OBL-SPRINT2B-001",
            "management_note": "Gestion creada desde grilla editable.",
            "commitment": "Confirmar compromiso desde celda.",
            "amount": 210000,
            "status": "Seguimiento",
            "next_action_at": "2026-06-07T00:00:00Z",
        },
    )
    assert create.status_code == 201, create.text
    row_id = create.json()["id"]

    update = client.patch(
        f"/api/excel-web/sheet-rows/{row_id}",
        headers=agent_headers,
        json={"amount": 250000, "status": "Gestionado", "commitment": "Cambio guardado desde celda."},
    )
    assert update.status_code == 200, update.text
    payload = update.json()
    assert payload["amount"] == 250000
    assert payload["status"] == "Gestionado"
    assert payload["commitment"] == "Cambio guardado desde celda."


def test_agent_cannot_update_admin_sheet_row(client, admin_headers, agent_headers):
    create = client.post(
        "/api/excel-web/sheet-rows",
        headers=admin_headers,
        json={
            "date": "2026-06-03",
            "portfolio": "Fila admin tenant",
            "customer_name": "Cliente Admin No Asignado",
            "document": "SPRINT2B-ADMIN-001",
            "management_note": "Fila creada por admin.",
            "commitment": "No editable por gestor.",
            "amount": 100000,
            "status": "Pendiente",
        },
    )
    assert create.status_code == 201, create.text
    row_id = create.json()["id"]

    update = client.patch(
        f"/api/excel-web/sheet-rows/{row_id}",
        headers=agent_headers,
        json={"status": "Gestionado"},
    )
    assert update.status_code in {403, 404}


def test_sheet_rows_keep_page_size_limit_and_filters(client, agent_headers):
    response = client.get(
        "/api/excel-web/sheet-rows?page=1&page_size=200&status=Gestionado",
        headers=agent_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["page_size"] <= 20
    assert len(payload["items"]) <= 20
    assert all(item["status"] == "Gestionado" for item in payload["items"])
