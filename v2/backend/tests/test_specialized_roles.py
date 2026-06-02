from __future__ import annotations

from .conftest import menu_ids


def test_lawyer_menu_is_legal_focused(client, lawyer_headers):
    sections = menu_ids(client, lawyer_headers)
    assert {"dashboard", "customers", "legal", "documents"}.issubset(sections)
    assert "governance" not in sections
    assert "tenant-settings" not in sections
    assert "sales" not in sections
    assert "queue" not in sections
    assert "payments" not in sections


def test_lawyer_access_is_limited_to_legal_and_documents(client, lawyer_headers):
    assert client.get("/api/legal/cases", headers=lawyer_headers).status_code == 200
    assert client.get("/api/legal/deadlines", headers=lawyer_headers).status_code == 200
    assert client.get("/api/documents", headers=lawyer_headers).status_code == 200
    assert client.get("/api/sales/leads", headers=lawyer_headers).status_code == 403
    assert client.get("/api/governance/roles", headers=lawyer_headers).status_code == 403
    assert client.get("/api/crm/customers/export", headers=lawyer_headers).status_code == 403
    assert client.get("/api/crm/payments/export", headers=lawyer_headers).status_code == 403


def test_sales_menu_is_sales_focused(client, sales_headers):
    sections = menu_ids(client, sales_headers)
    assert {"dashboard", "customers", "sales"}.issubset(sections)
    assert "governance" not in sections
    assert "tenant-settings" not in sections
    assert "legal" not in sections
    assert "documents" not in sections
    assert "queue" not in sections
    assert "payments" not in sections


def test_sales_access_is_limited_to_commercial_work(client, sales_headers):
    assert client.get("/api/sales/leads", headers=sales_headers).status_code == 200
    assert client.get("/api/sales/opportunities", headers=sales_headers).status_code == 200
    assert client.get("/api/legal/cases", headers=sales_headers).status_code == 403
    assert client.get("/api/documents", headers=sales_headers).status_code == 403
    assert client.get("/api/governance/roles", headers=sales_headers).status_code == 403
    assert client.get("/api/crm/customers/export", headers=sales_headers).status_code == 403
    assert client.get("/api/crm/payments/export", headers=sales_headers).status_code == 403


def test_collections_agent_regression(client, agent_headers):
    sections = menu_ids(client, agent_headers)
    assert {"dashboard", "queue", "customers", "promises", "payments", "agreements"}.issubset(sections)
    assert "legal" not in sections
    assert "sales" not in sections
    assert client.get("/api/crm/customers/export", headers=agent_headers).status_code == 403
