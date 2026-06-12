from __future__ import annotations

import time
from typing import Any

from .conftest import AGENT_EMAIL, LEADER_EMAIL, TENANT_PASSWORD, login


SECOND_AGENT_EMAIL = "gestor2.andina@demo.icodeup.local"


def _headers(session: dict[str, Any]) -> dict[str, str]:
    return session["headers"]


def _rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    return []


def _create_provider(client: Any, admin_headers: dict[str, str]) -> dict[str, Any]:
    suffix = int(time.time() * 1000)
    response = client.post(
        "/api/telephony/providers",
        headers=admin_headers,
        json={"name": f"PBX QA Manual {suffix}", "provider_type": "manual", "is_active": True, "config": {"mode": "simulated"}},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _find_user(client: Any, admin_headers: dict[str, str], email: str) -> dict[str, Any]:
    response = client.get("/api/governance/users", headers=admin_headers)
    assert response.status_code == 200, response.text
    for item in response.json():
        if item["email"] == email:
            return item
    raise AssertionError(f"User {email} not found.")


def _create_extension(client: Any, admin_headers: dict[str, str], user_id: int, provider_id: int, number: str = "77QA") -> dict[str, Any]:
    response = client.post(
        "/api/telephony/extensions",
        headers=admin_headers,
        json={
            "user_id": user_id,
            "provider_id": provider_id,
            "extension_number": f"{number}{int(time.time() * 1000) % 100000}",
            "display_name": "Extension QA",
            "status": "available",
            "is_active": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _extension_for_user(client: Any, admin_headers: dict[str, str], user_id: int) -> dict[str, Any] | None:
    response = client.get("/api/telephony/extensions", headers=admin_headers)
    assert response.status_code == 200, response.text
    for item in response.json():
        if int(item["user_id"]) == int(user_id):
            return item
    return None


def _first_customer(client: Any, headers: dict[str, str]) -> dict[str, Any]:
    response = client.get("/api/crm/customers?page_size=1", headers=headers)
    assert response.status_code == 200, response.text
    rows = response.json()["items"]
    assert rows
    return rows[0]


def test_admin_creates_provider_and_extension(client: Any, admin_session: dict[str, Any]) -> None:
    provider = _create_provider(client, _headers(admin_session))
    agent = _find_user(client, _headers(admin_session), AGENT_EMAIL)
    extension = _create_extension(client, _headers(admin_session), agent["id"], provider["id"])
    assert extension["provider_id"] == provider["id"]
    assert extension["user_id"] == agent["id"]


def test_seed_creates_simulated_provider_and_demo_extensions(client: Any, admin_session: dict[str, Any]) -> None:
    providers = client.get("/api/telephony/providers", headers=_headers(admin_session))
    assert providers.status_code == 200, providers.text
    simulated = [item for item in providers.json() if item["name"] == "Telefonia simulada local"]
    assert len(simulated) == 1
    assert simulated[0]["provider_type"] == "manual"
    assert simulated[0]["is_active"] is True

    extensions = client.get("/api/telephony/extensions", headers=_headers(admin_session))
    assert extensions.status_code == 200, extensions.text
    by_number = {item["extension_number"]: item for item in extensions.json()}
    assert by_number["1000"]["is_active"] is True
    assert by_number["1001"]["is_active"] is True
    assert by_number["1002"]["is_active"] is True
    assert by_number["1099"]["is_active"] is True


def test_agent_with_extension_can_start_simulated_click_to_call(client: Any, admin_session: dict[str, Any], agent_session: dict[str, Any]) -> None:
    provider = _create_provider(client, _headers(admin_session))
    _create_extension(client, _headers(admin_session), agent_session["user"]["id"], provider["id"], "78QA")
    customer = _first_customer(client, _headers(agent_session))
    response = client.post("/api/telephony/click-to-call", headers=_headers(agent_session), json={"customer_id": customer["id"]})
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["ok"] is True
    assert payload["mode"] in {"manual", "simulated"}
    assert payload["call_log"]["customer_id"] == customer["id"]
    assert payload["call_log"]["call_status"] == "initiated"
    assert payload["call_log"]["metadata"]["real_call_executed"] is False
    assert payload["call_log"]["metadata"]["extension_number"]


def test_agent_without_extension_receives_clear_error(client: Any, admin_session: dict[str, Any]) -> None:
    second_agent = login(client, SECOND_AGENT_EMAIL, TENANT_PASSWORD)
    extension = _extension_for_user(client, _headers(admin_session), second_agent["user"]["id"])
    assert extension is not None
    disabled = client.patch(f"/api/telephony/extensions/{extension['id']}", headers=_headers(admin_session), json={"is_active": False})
    assert disabled.status_code == 200, disabled.text
    customer = _first_customer(client, _headers(second_agent))
    try:
        response = client.post("/api/telephony/click-to-call", headers=_headers(second_agent), json={"customer_id": customer["id"]})
        assert response.status_code == 422, response.text
        assert "extension telefonica configurada" in response.text
    finally:
        restored = client.patch(f"/api/telephony/extensions/{extension['id']}", headers=_headers(admin_session), json={"is_active": True})
        assert restored.status_code == 200, restored.text


def test_call_log_scope_for_agent_and_leader(client: Any, admin_session: dict[str, Any], agent_session: dict[str, Any], leader_session: dict[str, Any]) -> None:
    provider = _create_provider(client, _headers(admin_session))
    _create_extension(client, _headers(admin_session), agent_session["user"]["id"], provider["id"], "79QA")
    customer = _first_customer(client, _headers(agent_session))
    created = client.post("/api/telephony/click-to-call", headers=_headers(agent_session), json={"customer_id": customer["id"]})
    assert created.status_code == 201, created.text
    call_id = created.json()["call_log"]["id"]

    agent_logs = client.get("/api/telephony/call-logs", headers=_headers(agent_session))
    assert agent_logs.status_code == 200, agent_logs.text
    assert any(item["id"] == call_id for item in agent_logs.json())
    assert all(item["user_id"] == agent_session["user"]["id"] for item in agent_logs.json())

    leader_logs = client.get("/api/telephony/call-logs", headers=_headers(leader_session))
    assert leader_logs.status_code == 200, leader_logs.text
    assert any(item["id"] == call_id for item in leader_logs.json())

    admin_logs = client.get("/api/telephony/call-logs", headers=_headers(admin_session))
    assert admin_logs.status_code == 200, admin_logs.text
    assert any(item["id"] == call_id for item in admin_logs.json())


def test_admin_tenant_and_customer_access_do_not_cross_tenants(client: Any, admin_session: dict[str, Any], platform_headers: dict[str, str], other_tenant_id: int) -> None:
    own_logs = client.get(f"/api/telephony/call-logs?tenant_id={other_tenant_id}", headers=_headers(admin_session))
    assert own_logs.status_code in {200, 403}, own_logs.text
    if own_logs.status_code == 200:
        assert all(item["tenant_id"] == admin_session["user"]["tenant_id"] for item in own_logs.json())

    tenants = client.get("/api/admin/tenants", headers=platform_headers)
    assert tenants.status_code == 200, tenants.text
    other_customer = None
    for tenant in tenants.json():
        if int(tenant["id"]) != int(admin_session["user"]["tenant_id"]) and tenant.get("customer_count", 0):
            response = client.get(f"/api/crm/customers?tenant_id={tenant['id']}&page_size=1", headers=platform_headers)
            if response.status_code == 200 and response.json().get("items"):
                other_customer = response.json()["items"][0]
                break
    if other_customer:
        response = client.post("/api/telephony/click-to-call", headers=_headers(admin_session), json={"customer_id": other_customer["id"]})
        assert response.status_code in {403, 422}, response.text
