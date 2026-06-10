from __future__ import annotations

from typing import Any

import pytest


def _rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("rows"), list):
        return payload["rows"]
    return []


def _assert_rows_do_not_leak(rows: list[dict[str, Any]], expected_tenant_id: int) -> None:
    for row in rows:
        if row.get("tenant_id") is not None:
            assert int(row["tenant_id"]) == expected_tenant_id


def _first_row_for_tenant(client: Any, headers: dict[str, str], endpoint: str, tenant_id: int) -> dict[str, Any] | None:
    response = client.get(endpoint, headers=headers)
    assert response.status_code == 200, response.text
    for row in _rows(response.json()):
        if row.get("tenant_id") is not None and int(row["tenant_id"]) == tenant_id:
            return row
    return None


def _first_customer_for_tenant(client: Any, headers: dict[str, str], tenant_id: int) -> dict[str, Any] | None:
    response = client.get(f"/api/crm/customers?tenant_id={tenant_id}&page_size=1", headers=headers)
    assert response.status_code == 200, response.text
    items = response.json().get("items", [])
    return items[0] if items else None


def test_deep_query_manipulation_does_not_leak_tenant_data(
    client: Any,
    platform_headers: dict[str, str],
    admin_headers: dict[str, str],
    admin_tenant_id: int,
    other_tenant_id: int,
) -> None:
    other_customer = _first_customer_for_tenant(client, platform_headers, other_tenant_id)
    endpoints = [
        f"/api/crm/customers?page_size=20&tenant_id={other_tenant_id}",
        f"/api/documents?limit=20&tenant_id={other_tenant_id}",
        f"/api/uploads/batches?tenant_id={other_tenant_id}",
        f"/api/legal/cases?limit=20&tenant_id={other_tenant_id}",
        f"/api/sales/leads?limit=20&tenant_id={other_tenant_id}",
        f"/api/sales/opportunities?limit=20&tenant_id={other_tenant_id}",
    ]
    if other_customer:
        endpoints.append(f"/api/crm/obligations?limit=20&customer_id={other_customer['id']}")

    for endpoint in endpoints:
        response = client.get(endpoint, headers=admin_headers)
        assert response.status_code == 200, f"{endpoint}: {response.status_code} {response.text}"
        _assert_rows_do_not_leak(_rows(response.json()), admin_tenant_id)

    projects_response = client.get(f"/api/teams/projects?tenant_id={other_tenant_id}", headers=platform_headers)
    assert projects_response.status_code == 200, projects_response.text
    other_projects = _rows(projects_response.json())
    if other_projects:
        excel_response = client.post(
            "/api/excel-web/query",
            headers=admin_headers,
            json={"source": "customers", "filters": {"project_id": other_projects[0]["id"]}, "columns": ["id", "name"], "page": 1, "page_size": 20},
        )
        assert excel_response.status_code == 200, excel_response.text
        assert excel_response.json()["total"] == 0


def test_deep_direct_id_access_to_foreign_tenant_records_is_denied(
    client: Any,
    platform_headers: dict[str, str],
    admin_headers: dict[str, str],
    other_tenant_id: int,
) -> None:
    probes: list[tuple[str, str, str, dict[str, Any] | None]] = []
    other_customer = _first_customer_for_tenant(client, platform_headers, other_tenant_id)
    if other_customer:
        probes.append(("get", f"/api/crm/customers/{other_customer['id']}/activities", "customer activities", None))

    other_obligation = _first_row_for_tenant(client, platform_headers, "/api/crm/obligations?limit=20", other_tenant_id)
    if other_obligation:
        probes.append(("patch", f"/api/crm/obligations/{other_obligation['id']}", "obligation", {}))

    for endpoint, label in [
        ("/api/documents?limit=20", "document"),
        ("/api/uploads/batches", "upload batch"),
        ("/api/legal/cases?limit=20", "legal case"),
    ]:
        row = _first_row_for_tenant(client, platform_headers, endpoint, other_tenant_id)
        if row:
            probes.append(("get", f"{endpoint.split('?')[0]}/{row['id']}", label, None))

    sheet_response = client.get("/api/excel-web/sheet-rows?page_size=20", headers=platform_headers)
    if sheet_response.status_code == 200:
        for row in _rows(sheet_response.json()):
            if row.get("tenant_id") is not None and int(row["tenant_id"]) == other_tenant_id:
                probes.append(("patch", f"/api/excel-web/sheet-rows/{row['id']}", "excel sheet row", {"status": row.get("status") or "Pendiente"}))
                break

    if not probes:
        pytest.skip("No foreign tenant records available for direct ID probes.")

    for method, path, label, payload in probes:
        response = client.patch(path, headers=admin_headers, json=payload) if method == "patch" else client.get(path, headers=admin_headers)
        assert response.status_code in {403, 404}, f"{label} should be denied: {response.status_code} {response.text}"


def test_deep_agent_and_leader_scope_do_not_cross_assignment_boundaries(
    client: Any,
    platform_headers: dict[str, str],
    admin_headers: dict[str, str],
    agent_headers: dict[str, str],
    agent_session: dict[str, Any],
    leader_headers: dict[str, str],
    leader_session: dict[str, Any],
) -> None:
    agent_response = client.get("/api/crm/customers?page_size=20", headers=agent_headers)
    assert agent_response.status_code == 200, agent_response.text
    for customer in agent_response.json().get("items", []):
        if customer.get("assigned_user_id") is not None:
            assert int(customer["assigned_user_id"]) == int(agent_session["user"]["id"])

    admin_customers = client.get("/api/crm/customers?page_size=20", headers=admin_headers)
    assert admin_customers.status_code == 200, admin_customers.text
    foreign_to_agent = next(
        (item for item in admin_customers.json().get("items", []) if item.get("assigned_user_id") not in {None, agent_session["user"]["id"]}),
        None,
    )
    if foreign_to_agent:
        response = client.get(f"/api/crm/customers/{foreign_to_agent['id']}/activities", headers=agent_headers)
        assert response.status_code in {403, 404}

    leaders = client.get("/api/teams/leaders", headers=admin_headers)
    assert leaders.status_code == 200, leaders.text
    other_leader = next((item for item in leaders.json() if int(item["id"]) != int(leader_session["user"]["id"])), None)
    if other_leader:
        response = client.get(f"/api/teams/leaders/{other_leader['id']}/agents", headers=leader_headers)
        assert response.status_code in {403, 404}

    leader_visible = client.get("/api/crm/customers?page_size=20", headers=leader_headers)
    assert leader_visible.status_code == 200, leader_visible.text
    visible_ids = {item["id"] for item in leader_visible.json().get("items", [])}
    hidden_customer = next((item for item in admin_customers.json().get("items", []) if item["id"] not in visible_ids), None)
    if hidden_customer:
        response = client.get(f"/api/crm/customers/{hidden_customer['id']}/activities", headers=leader_headers)
        assert response.status_code in {403, 404}


def test_deep_upload_confirm_cannot_target_foreign_tenant(
    client: Any,
    admin_headers: dict[str, str],
    other_tenant_id: int,
) -> None:
    payload = {
        "tenant_id": other_tenant_id,
        "upload_type": "reparto_cartera",
        "file_name": "tenant_isolation_probe.csv",
        "csv_text": "documento,cliente\n990000001,Cliente Bloqueado",
        "mapping": {},
        "create_records": True,
    }
    response = client.post("/api/uploads/confirm", headers=admin_headers, json=payload)
    assert response.status_code == 403, response.text


def test_deep_exports_dashboards_and_governance_remain_scoped(
    client: Any,
    admin_headers: dict[str, str],
    agent_headers: dict[str, str],
    admin_tenant_id: int,
    other_tenant_id: int,
) -> None:
    customers = client.get("/api/crm/customers?page_size=10", headers=admin_headers)
    dashboard = client.get(f"/api/crm/dashboard?tenant_id={other_tenant_id}", headers=admin_headers)
    assert customers.status_code == 200, customers.text
    assert dashboard.status_code == 200, dashboard.text
    assert int(dashboard.json()["customers"]) == int(customers.json()["total"])

    customer_export = client.get(f"/api/crm/customers/export?tenant_id={other_tenant_id}", headers=admin_headers)
    assert customer_export.status_code == 200, customer_export.text
    assert f"\n{other_tenant_id}," not in customer_export.text
    assert f"\n{admin_tenant_id}," in customer_export.text or customers.json()["total"] == 0

    for path in ["/api/crm/customers/export", "/api/crm/payments/export", "/api/excel-web/export"]:
        if path == "/api/excel-web/export":
            response = client.post(path, headers=agent_headers, json={"source": "customers", "filters": {}, "columns": ["name"], "page": 1, "page_size": 20})
        else:
            response = client.get(path, headers=agent_headers)
        assert response.status_code == 403, f"{path}: {response.status_code} {response.text}"

    governance = client.get("/api/governance/subscriptions", headers=admin_headers)
    assert governance.status_code == 403
