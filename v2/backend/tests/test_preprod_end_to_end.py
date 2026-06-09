from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .conftest import menu_ids


def _first(items: list[dict[str, Any]], message: str) -> dict[str, Any]:
    assert items, message
    return items[0]


def test_preprod_login_menu_and_core_dashboards_by_role(
    client: Any,
    platform_headers: dict[str, str],
    admin_headers: dict[str, str],
    leader_headers: dict[str, str],
    agent_headers: dict[str, str],
    lawyer_headers: dict[str, str],
    sales_headers: dict[str, str],
) -> None:
    expectations = [
        (platform_headers, {"governance"}, {"queue"}),
        (admin_headers, {"dashboard", "tenant-settings", "roles-permissions"}, {"governance"}),
        (leader_headers, {"dashboard", "queue", "customers", "teams"}, {"governance"}),
        (agent_headers, {"dashboard", "queue", "customers", "promises", "payments", "agreements"}, {"governance", "tenant-settings", "teams"}),
        (lawyer_headers, {"dashboard", "customers", "legal", "documents"}, {"governance", "sales", "queue"}),
        (sales_headers, {"dashboard", "customers", "sales"}, {"governance", "legal", "documents", "queue"}),
    ]
    for headers, required, forbidden in expectations:
        sections = menu_ids(client, headers)
        assert required.issubset(sections)
        assert forbidden.isdisjoint(sections)
        dashboard = client.get("/api/dashboard/me", headers=headers)
        assert dashboard.status_code == 200, dashboard.text


def test_preprod_gestor_operational_flow(client: Any, agent_headers: dict[str, str]) -> None:
    customers = client.get("/api/crm/customers?page_size=1", headers=agent_headers)
    assert customers.status_code == 200, customers.text
    customer = _first(customers.json()["items"], "Expected an assigned customer for gestor demo.")

    obligations = client.get(f"/api/crm/customers/{customer['id']}/obligations", headers=agent_headers)
    assert obligations.status_code == 200, obligations.text
    obligation = obligations.json()[0] if obligations.json() else None

    payload = {
        "channel": "QA preproductivo",
        "typification": "Contacto",
        "subtypification": "Seguimiento",
        "final_qualification": "Validacion",
        "result": "Contactado",
        "note": f"Smoke preprod {datetime.now(timezone.utc).isoformat()}",
        "obligation_id": obligation["id"] if obligation else None,
    }
    activity = client.post(f"/api/crm/customers/{customer['id']}/activities", json=payload, headers=agent_headers)
    assert activity.status_code == 201, activity.text

    recent = client.get(f"/api/crm/customers/{customer['id']}/activities", headers=agent_headers)
    assert recent.status_code == 200, recent.text
    assert any(item["id"] == activity.json()["id"] for item in recent.json())


def test_preprod_admin_leader_and_operational_surfaces(client: Any, admin_headers: dict[str, str], leader_headers: dict[str, str]) -> None:
    admin_checks = [
        "/api/teams/projects",
        "/api/teams/agents",
        "/api/uploads/templates/clientes",
        "/api/uploads/batches?page_size=20",
        "/api/governance/audit-logs?limit=20",
        "/api/configuration/catalogs",
    ]
    for endpoint in admin_checks:
        response = client.get(endpoint, headers=admin_headers)
        assert response.status_code == 200, f"{endpoint}: {response.status_code} {response.text}"

    leader_checks = [
        "/api/teams/dashboard",
        "/api/teams/projects",
        "/api/crm/customers?page_size=20",
        "/api/crm/obligations?limit=20",
        "/api/crm/promises?limit=20",
        "/api/crm/payments?limit=20",
        "/api/crm/agreements?limit=20",
    ]
    for endpoint in leader_checks:
        response = client.get(endpoint, headers=leader_headers)
        assert response.status_code == 200, f"{endpoint}: {response.status_code} {response.text}"


def test_preprod_excel_web_and_upload_preview_stay_available_for_admin(client: Any, admin_headers: dict[str, str]) -> None:
    excel = client.post(
        "/api/excel-web/query",
        json={"source": "customers", "page": 1, "page_size": 20, "filters": {}, "columns": []},
        headers=admin_headers,
    )
    assert excel.status_code == 200, excel.text
    assert excel.json()["page_size"] == 20

    preview = client.post(
        "/api/uploads/preview",
        json={
            "upload_type": "clientes",
            "file_name": "preprod_preview.csv",
            "csv_text": "documento,cliente,telefono\n909999991,Cliente Preview Preprod,3000000991",
            "mapping": {},
            "create_records": False,
        },
        headers=admin_headers,
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["total_rows"] == 1
