from __future__ import annotations

import os
from typing import Any

import pytest
from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models import Customer, CustomerDemographic, CustomerObligation, ManagementActivity, Payment, PaymentAgreement, PaymentPromise, Project, Tenant, UploadBatch, User

from .conftest import TENANT_PASSWORD


PILOT_SLUG = "icodeup-advisors"
PILOT_ADMIN_EMAIL = "admin.icodeup@demo.icodeup.local"
PILOT_LEADER_EMAIL = "lider.cobranzas.icodeup@demo.icodeup.local"
PILOT_AGENT_EMAIL = "gestor1.icodeup@demo.icodeup.local"
PILOT_PASSWORD = os.getenv("ICODEUP_TEST_PILOT_PASSWORD") or TENANT_PASSWORD
PILOT_AGENT_EMAILS = [f"gestor{index}.icodeup@demo.icodeup.local" for index in range(1, 6)]
PILOT_PROJECT_CODES = {"PILOTO-CONSUMO", "PILOTO-PREVENTIVA", "PILOTO-JURIDICA"}


@pytest.fixture(scope="session")
def pilot_db():
    if SessionLocal is None:
        pytest.skip("Database session is not configured.")
    with SessionLocal() as db:
        yield db


@pytest.fixture(scope="session")
def pilot_tenant(pilot_db):
    tenant = pilot_db.scalar(select(Tenant).where(Tenant.slug == PILOT_SLUG))
    if tenant is None:
        pytest.skip("Icodeup Advisors pilot seed is not loaded. Set ENABLE_PILOT_ICODEUP_SEED=true and restart the app.")
    return tenant


def _login_or_skip(client: Any, email: str) -> dict[str, Any]:
    if not PILOT_PASSWORD:
        pytest.skip("Set ICODEUP_TEST_PILOT_PASSWORD or ICODEUP_TEST_TENANT_PASSWORD to validate pilot logins.")
    response = client.post("/api/auth/login", json={"email": email, "password": PILOT_PASSWORD})
    if response.status_code in {400, 401, 404}:
        pytest.skip(f"Pilot user {email} is not available or password is not configured.")
    assert response.status_code == 200, response.text
    data = response.json()
    data["headers"] = {"Authorization": f"Bearer {data['access_token']}"}
    return data


def _rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("rows"), list):
        return payload["rows"]
    return []


def test_pilot_seed_inventory_counts(pilot_db, pilot_tenant) -> None:
    tenant_id = pilot_tenant.id
    users = set(pilot_db.scalars(select(User.email).where(User.tenant_id == tenant_id)))
    assert {PILOT_ADMIN_EMAIL, PILOT_LEADER_EMAIL, *PILOT_AGENT_EMAILS}.issubset(users)

    projects = set(pilot_db.scalars(select(Project.code).where(Project.tenant_id == tenant_id)))
    assert PILOT_PROJECT_CODES.issubset(projects)

    assert (pilot_db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == tenant_id)) or 0) >= 300
    assert (pilot_db.scalar(select(func.count(CustomerObligation.id)).where(CustomerObligation.tenant_id == tenant_id)) or 0) >= 500
    assert (pilot_db.scalar(select(func.count(ManagementActivity.id)).where(ManagementActivity.tenant_id == tenant_id)) or 0) >= 300
    assert (pilot_db.scalar(select(func.count(PaymentPromise.id)).where(PaymentPromise.tenant_id == tenant_id)) or 0) >= 50
    assert (pilot_db.scalar(select(func.count(Payment.id)).where(Payment.tenant_id == tenant_id)) or 0) >= 30
    assert (pilot_db.scalar(select(func.count(PaymentAgreement.id)).where(PaymentAgreement.tenant_id == tenant_id)) or 0) >= 20
    assert (pilot_db.scalar(select(func.count(CustomerDemographic.id)).where(CustomerDemographic.tenant_id == tenant_id, CustomerDemographic.source == "PILOTO_ICODEUP")) or 0) >= 100
    assert (pilot_db.scalar(select(func.count(UploadBatch.id)).where(UploadBatch.tenant_id == tenant_id)) or 0) >= 3


def test_pilot_seed_assignment_integrity(pilot_db, pilot_tenant) -> None:
    tenant_id = pilot_tenant.id
    agent_ids = set(pilot_db.scalars(select(User.id).where(User.tenant_id == tenant_id, User.email.in_(PILOT_AGENT_EMAILS))))
    assert len(agent_ids) == 5

    assigned_customer_agents = set(pilot_db.scalars(select(Customer.assigned_user_id).where(Customer.tenant_id == tenant_id)))
    assert agent_ids.issubset({item for item in assigned_customer_agents if item is not None})

    missing_assigned_user = pilot_db.scalar(select(func.count(CustomerObligation.id)).where(CustomerObligation.tenant_id == tenant_id, CustomerObligation.assigned_user_id.is_(None))) or 0
    missing_assigned_leader = pilot_db.scalar(select(func.count(CustomerObligation.id)).where(CustomerObligation.tenant_id == tenant_id, CustomerObligation.assigned_leader_id.is_(None))) or 0
    assert missing_assigned_user == 0
    assert missing_assigned_leader == 0


def test_pilot_admin_scope_does_not_leak_and_can_see_own_operation(client: Any, pilot_tenant) -> None:
    admin_session = _login_or_skip(client, PILOT_ADMIN_EMAIL)
    headers = admin_session["headers"]

    customers = client.get("/api/crm/customers?page_size=10", headers=headers)
    assert customers.status_code == 200, customers.text
    body = customers.json()
    assert body["total"] >= 300
    assert all(int(item["tenant_id"]) == int(pilot_tenant.id) for item in body["items"])

    manipulated = client.get("/api/crm/customers?page_size=10&tenant_id=1", headers=headers)
    assert manipulated.status_code == 200, manipulated.text
    assert all(int(item["tenant_id"]) == int(pilot_tenant.id) for item in manipulated.json()["items"])


def test_pilot_leader_dashboard_and_agent_scope(client: Any) -> None:
    leader_session = _login_or_skip(client, PILOT_LEADER_EMAIL)
    agent_session = _login_or_skip(client, PILOT_AGENT_EMAIL)

    leader_dashboard = client.get("/api/teams/dashboard", headers=leader_session["headers"])
    assert leader_dashboard.status_code == 200, leader_dashboard.text
    assert leader_dashboard.json().get("customers", 0) >= 1

    agent_customers = client.get("/api/crm/customers?page_size=10", headers=agent_session["headers"])
    assert agent_customers.status_code == 200, agent_customers.text
    for customer in agent_customers.json()["items"]:
        assert int(customer["assigned_user_id"]) == int(agent_session["user"]["id"])


def test_pilot_excel_web_and_upload_batches(client: Any) -> None:
    agent_session = _login_or_skip(client, PILOT_AGENT_EMAIL)
    admin_session = _login_or_skip(client, PILOT_ADMIN_EMAIL)

    excel = client.post(
        "/api/excel-web/query",
        headers=agent_session["headers"],
        json={"source": "customers", "filters": {}, "columns": ["name", "document", "assigned_user_id"], "page": 1, "page_size": 20},
    )
    assert excel.status_code == 200, excel.text
    assert excel.json()["total"] >= 1

    batches = client.get("/api/uploads/batches", headers=admin_session["headers"])
    assert batches.status_code == 200, batches.text
    filenames = {row.get("original_filename") for row in _rows(batches.json())}
    assert "reparto_icodeup_piloto_consumo.csv" in filenames or "reparto_icodeup_piloto_preventiva.csv" in filenames
