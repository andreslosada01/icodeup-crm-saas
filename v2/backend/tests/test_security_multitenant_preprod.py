from __future__ import annotations

from typing import Any


def _rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        if isinstance(payload.get("items"), list):
            return payload["items"]
        return []
    if isinstance(payload, list):
        return payload
    return []


def _assert_tenant_rows(rows: list[dict[str, Any]], tenant_id: int) -> None:
    assert len(rows) <= 20
    for row in rows:
        if row.get("tenant_id") is not None:
            assert int(row["tenant_id"]) == tenant_id


def _first_platform_row_for_tenant(client: Any, platform_headers: dict[str, str], endpoint: str, tenant_id: int) -> dict[str, Any] | None:
    separator = "&" if "?" in endpoint else "?"
    response = client.get(f"{endpoint}{separator}tenant_id={tenant_id}", headers=platform_headers)
    if response.status_code != 200:
        return None
    rows = _rows(response.json())
    for row in rows:
        if row.get("tenant_id") is not None and int(row["tenant_id"]) == tenant_id:
            return row
    return None


def test_preprod_scoped_lists_do_not_leak_when_tenant_id_is_manipulated(client: Any, admin_headers: dict[str, str], admin_tenant_id: int, other_tenant_id: int) -> None:
    endpoints = [
        f"/api/crm/customers?page_size=20&tenant_id={other_tenant_id}",
        f"/api/crm/obligations?limit=20&tenant_id={other_tenant_id}",
        f"/api/crm/promises?limit=20&tenant_id={other_tenant_id}",
        f"/api/crm/payments?limit=20&tenant_id={other_tenant_id}",
        f"/api/crm/agreements?limit=20&tenant_id={other_tenant_id}",
        f"/api/documents?limit=20&tenant_id={other_tenant_id}",
        f"/api/legal/cases?limit=20&tenant_id={other_tenant_id}",
        f"/api/sales/leads?limit=20&tenant_id={other_tenant_id}",
        f"/api/sales/opportunities?limit=20&tenant_id={other_tenant_id}",
        f"/api/uploads/demographics?page_size=20&tenant_id={other_tenant_id}",
    ]
    for endpoint in endpoints:
        response = client.get(endpoint, headers=admin_headers)
        assert response.status_code == 200, f"{endpoint}: {response.status_code} {response.text}"
        _assert_tenant_rows(_rows(response.json()), admin_tenant_id)


def test_direct_foreign_records_are_denied_or_hidden(client: Any, platform_headers: dict[str, str], admin_headers: dict[str, str], other_tenant_id: int) -> None:
    probes = [
        ("/api/crm/customers?page_size=20", "/api/crm/customers/{id}/activities"),
        ("/api/legal/cases?limit=20", "/api/legal/cases/{id}"),
        ("/api/documents?limit=20", "/api/documents/{id}"),
    ]
    for list_endpoint, detail_template in probes:
        row = _first_platform_row_for_tenant(client, platform_headers, list_endpoint, other_tenant_id)
        if not row:
            continue
        response = client.get(detail_template.format(id=row["id"]), headers=admin_headers)
        assert response.status_code in {403, 404}, f"{detail_template}: {response.status_code} {response.text}"


def test_preprod_restricted_roles_cannot_export_or_administer(client: Any, agent_headers: dict[str, str], lawyer_headers: dict[str, str], sales_headers: dict[str, str]) -> None:
    blocked_headers = [agent_headers, lawyer_headers, sales_headers]
    blocked_endpoints = [
        "/api/crm/customers/export",
        "/api/crm/payments/export",
        "/api/governance/roles",
        "/api/uploads/batches",
    ]
    for headers in blocked_headers:
        for endpoint in blocked_endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code == 403, f"{endpoint}: {response.status_code} {response.text}"


def test_preprod_user_lists_are_capped_to_twenty(client: Any, admin_headers: dict[str, str], lawyer_headers: dict[str, str], sales_headers: dict[str, str]) -> None:
    checks = [
        ("/api/crm/customers?page_size=20", admin_headers),
        ("/api/crm/obligations?limit=20", admin_headers),
        ("/api/crm/promises?limit=20", admin_headers),
        ("/api/crm/payments?limit=20", admin_headers),
        ("/api/crm/agreements?limit=20", admin_headers),
        ("/api/documents?limit=20", admin_headers),
        ("/api/legal/cases?limit=20", lawyer_headers),
        ("/api/sales/leads?limit=20", sales_headers),
        ("/api/sales/opportunities?limit=20", sales_headers),
        ("/api/uploads/demographics?page_size=20", admin_headers),
    ]
    for endpoint, headers in checks:
        response = client.get(endpoint, headers=headers)
        assert response.status_code == 200, f"{endpoint}: {response.status_code} {response.text}"
        assert len(_rows(response.json())) <= 20
