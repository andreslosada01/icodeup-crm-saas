from __future__ import annotations

from .conftest import csv_rows


def test_admin_cannot_query_other_tenant_parties(client, admin_headers, other_tenant_id):
    response = client.get(f"/api/governance/parties?tenant_id={other_tenant_id}", headers=admin_headers)
    assert response.status_code == 403


def test_agent_only_sees_assigned_customer_scope(client, agent_headers, agent_session):
    response = client.get("/api/crm/customers?page_size=10", headers=agent_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "items" in payload
    for customer in payload["items"]:
        assert customer.get("assigned_user_id") in {None, agent_session["user"]["id"]}


def test_customer_export_does_not_leak_other_tenant(client, admin_headers, admin_tenant_id, other_tenant_id):
    response = client.get(f"/api/crm/customers/export?tenant_id={other_tenant_id}", headers=admin_headers)
    assert response.status_code == 200, response.text
    for row in csv_rows(response.text):
        assert int(row["tenant_id"]) == admin_tenant_id
