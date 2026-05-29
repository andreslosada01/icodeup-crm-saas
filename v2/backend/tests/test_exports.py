from __future__ import annotations

from .conftest import csv_rows


def test_export_customers_requires_permission(client, agent_headers):
    response = client.get("/api/crm/customers/export", headers=agent_headers)
    assert response.status_code == 403


def test_export_payments_requires_permission(client, agent_headers):
    response = client.get("/api/crm/payments/export", headers=agent_headers)
    assert response.status_code == 403


def test_export_customers_respects_tenant(client, admin_headers, admin_tenant_id):
    response = client.get("/api/crm/customers/export", headers=admin_headers)
    assert response.status_code == 200, response.text
    for row in csv_rows(response.text):
        assert int(row["tenant_id"]) == admin_tenant_id


def test_export_payments_respects_tenant(client, admin_headers, admin_tenant_id):
    response = client.get("/api/crm/payments/export", headers=admin_headers)
    assert response.status_code == 200, response.text
    for row in csv_rows(response.text):
        assert int(row["tenant_id"]) == admin_tenant_id
