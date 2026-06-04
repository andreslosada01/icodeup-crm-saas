from __future__ import annotations

import csv
import importlib.util
import os
from io import StringIO
from typing import Any

import pytest


RUN_INTEGRATION = os.getenv("ICODEUP_RUN_INTEGRATION_TESTS") == "1"
HTTPX_AVAILABLE = importlib.util.find_spec("httpx") is not None

if HTTPX_AVAILABLE:
    import httpx


BASE_URL = os.getenv("ICODEUP_TEST_BASE_URL", "http://127.0.0.1:8020")
PLATFORM_EMAIL = os.getenv("ICODEUP_TEST_PLATFORM_EMAIL", "superadmin@demo.icodeup.local")
PLATFORM_PASSWORD = os.getenv("ICODEUP_TEST_PLATFORM_PASSWORD")
TENANT_ADMIN_EMAIL = os.getenv("ICODEUP_TEST_TENANT_ADMIN_EMAIL", "admin.andina@demo.icodeup.local")
LEADER_EMAIL = os.getenv("ICODEUP_TEST_LEADER_EMAIL", "coord.cobranzas.andina@demo.icodeup.local")
AGENT_EMAIL = os.getenv("ICODEUP_TEST_AGENT_EMAIL", "gestor1.andina@demo.icodeup.local")
LAWYER_EMAIL = os.getenv("ICODEUP_TEST_LAWYER_EMAIL", "abogado.andina@demo.icodeup.local")
SALES_EMAIL = os.getenv("ICODEUP_TEST_SALES_EMAIL", "comercial.andina@demo.icodeup.local")
TENANT_PASSWORD = os.getenv("ICODEUP_TEST_TENANT_PASSWORD")
LAWYER_PASSWORD = os.getenv("ICODEUP_TEST_LAWYER_PASSWORD", TENANT_PASSWORD)
SALES_PASSWORD = os.getenv("ICODEUP_TEST_SALES_PASSWORD", TENANT_PASSWORD)
LEADER_PASSWORD = os.getenv("ICODEUP_TEST_LEADER_PASSWORD", TENANT_PASSWORD)
CREDENTIALS_CONFIGURED = bool(PLATFORM_PASSWORD and TENANT_PASSWORD)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if RUN_INTEGRATION and HTTPX_AVAILABLE and CREDENTIALS_CONFIGURED:
        return
    reason = "Set ICODEUP_RUN_INTEGRATION_TESTS=1 and use a safe seeded test database to run SaaS integration tests."
    if not HTTPX_AVAILABLE:
        reason = "httpx is not installed; install backend dependencies before running integration tests."
    elif RUN_INTEGRATION and not CREDENTIALS_CONFIGURED:
        reason = "Set ICODEUP_TEST_PLATFORM_PASSWORD and ICODEUP_TEST_TENANT_PASSWORD to run integration tests."
    marker = pytest.mark.skip(reason=reason)
    for item in items:
        item.add_marker(marker)


@pytest.fixture(scope="session")
def client():
    if not HTTPX_AVAILABLE:
        pytest.skip("httpx is not installed.")
    with httpx.Client(base_url=BASE_URL, timeout=15.0) as test_client:
        yield test_client


def login(client: Any, email: str, password: str) -> dict[str, Any]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    if response.status_code != 200:
        pytest.fail(f"Login failed for {email}: {response.status_code} {response.text}")
    data = response.json()
    data["headers"] = {"Authorization": f"Bearer {data['access_token']}"}
    return data


@pytest.fixture(scope="session")
def platform_session(client: Any) -> dict[str, Any]:
    return login(client, PLATFORM_EMAIL, PLATFORM_PASSWORD)


@pytest.fixture(scope="session")
def admin_session(client: Any) -> dict[str, Any]:
    return login(client, TENANT_ADMIN_EMAIL, TENANT_PASSWORD)


@pytest.fixture(scope="session")
def agent_session(client: Any) -> dict[str, Any]:
    return login(client, AGENT_EMAIL, TENANT_PASSWORD)


@pytest.fixture(scope="session")
def leader_session(client: Any) -> dict[str, Any]:
    return login(client, LEADER_EMAIL, LEADER_PASSWORD)


@pytest.fixture(scope="session")
def lawyer_session(client: Any) -> dict[str, Any]:
    return login(client, LAWYER_EMAIL, LAWYER_PASSWORD)


@pytest.fixture(scope="session")
def sales_session(client: Any) -> dict[str, Any]:
    return login(client, SALES_EMAIL, SALES_PASSWORD)


@pytest.fixture(scope="session")
def platform_headers(platform_session: dict[str, Any]) -> dict[str, str]:
    return platform_session["headers"]


@pytest.fixture(scope="session")
def admin_headers(admin_session: dict[str, Any]) -> dict[str, str]:
    return admin_session["headers"]


@pytest.fixture(scope="session")
def agent_headers(agent_session: dict[str, Any]) -> dict[str, str]:
    return agent_session["headers"]


@pytest.fixture(scope="session")
def leader_headers(leader_session: dict[str, Any]) -> dict[str, str]:
    return leader_session["headers"]


@pytest.fixture(scope="session")
def lawyer_headers(lawyer_session: dict[str, Any]) -> dict[str, str]:
    return lawyer_session["headers"]


@pytest.fixture(scope="session")
def sales_headers(sales_session: dict[str, Any]) -> dict[str, str]:
    return sales_session["headers"]


@pytest.fixture(scope="session")
def admin_tenant_id(admin_session: dict[str, Any]) -> int:
    return int(admin_session["user"]["tenant_id"])


@pytest.fixture(scope="session")
def other_tenant_id(client: Any, platform_headers: dict[str, str], admin_tenant_id: int) -> int:
    response = client.get("/api/admin/tenants", headers=platform_headers)
    if response.status_code != 200:
        pytest.skip("Cannot discover tenants for cross-tenant checks.")
    tenants = response.json()
    for tenant in tenants:
        if int(tenant["id"]) != admin_tenant_id and tenant.get("slug") != "icodeup-platform":
            return int(tenant["id"])
    pytest.skip("No second tenant available for cross-tenant checks.")


def menu_ids(client: Any, headers: dict[str, str]) -> set[str]:
    response = client.get("/api/menu/me", headers=headers)
    assert response.status_code == 200, response.text
    return {item["section"] for item in response.json().get("items", [])}


def csv_rows(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(StringIO(text))
    return list(reader)
