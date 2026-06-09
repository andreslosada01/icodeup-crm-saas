from __future__ import annotations


def test_agent_sheet_rows_are_filtered_and_limited(client, agent_headers):
    response = client.get(
        "/api/excel-web/sheet-rows?page=1&page_size=200&status=Seguimiento",
        headers=agent_headers,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["page_size"] <= 20
    assert len(payload["items"]) <= 20
    assert all(item["status"] == "Seguimiento" for item in payload["items"])


def test_admin_excel_web_export_returns_csv(client, admin_headers):
    response = client.post(
        "/api/excel-web/export",
        headers=admin_headers,
        json={
            "source": "customers",
            "filters": {},
            "columns": ["id", "name", "document", "assigned_user_id"],
            "page": 1,
            "page_size": 20,
        },
    )
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/csv")
    assert "Content-Disposition" in response.headers
    assert "id,name,document,assigned_user_id" in response.text.splitlines()[0]


def test_agent_excel_web_export_is_blocked(client, agent_headers):
    response = client.post(
        "/api/excel-web/export",
        headers=agent_headers,
        json={"source": "customers", "filters": {}, "columns": ["id", "name"], "page": 1, "page_size": 20},
    )
    assert response.status_code == 403
