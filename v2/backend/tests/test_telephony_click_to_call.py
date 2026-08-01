from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest
from fastapi import HTTPException

from app.api.routes import telephony as telephony_routes
from app.models import TelephonyProvider
from .conftest import AGENT_EMAIL, LEADER_EMAIL, TENANT_PASSWORD, login


SECOND_AGENT_EMAIL = "gestor2.andina@demo.icodeup.local"
IPCOM_CONFIG = {
    "trunk_name": "IpCom",
    "dtmf_mode": "rfc2833",
    "nat": "force_rport,comedia",
    "codecs": "ulaw,alaw,g729",
    "external_prefix": "0218739#",
    "mobile_prepend": "000157",
    "mobile_match_pattern": "3XXXXXXXXX",
    "country_context": "Colombia",
    "outbound_enabled": True,
    "priority": 1,
}


def _headers(session: dict[str, Any]) -> dict[str, str]:
    return session["headers"]


def _rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    return []


def _create_provider(
    client: Any,
    admin_headers: dict[str, str],
    *,
    tenant_id: int | None = None,
    name_prefix: str = "PBX QA Manual",
    provider_type: str = "manual",
    host: str | None = None,
    port: int | None = None,
    is_active: bool = True,
    is_primary: bool = False,
    outbound_enabled: bool = True,
    priority: int | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    suffix = time.time_ns()
    payload: dict[str, Any] = {
        "tenant_id": tenant_id,
        "name": f"{name_prefix} {suffix}",
        "provider_type": provider_type,
        "host": host,
        "port": port,
        "is_active": is_active,
        "is_primary": is_primary,
        "outbound_enabled": outbound_enabled,
        "priority": priority,
        "config": config or {"mode": "simulated"},
    }
    response = client.post(
        "/api/telephony/providers",
        headers=admin_headers,
        json=payload,
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


def test_agent_cannot_create_provider(client: Any, agent_session: dict[str, Any]) -> None:
    response = client.post(
        "/api/telephony/providers",
        headers=_headers(agent_session),
        json={"name": "Proveedor no autorizado", "provider_type": "manual", "config": {"mode": "simulated"}},
    )
    assert response.status_code == 403, response.text


def test_primary_provider_demotes_previous_primary(client: Any, admin_session: dict[str, Any]) -> None:
    first = _create_provider(client, _headers(admin_session), name_prefix="IpCom QA primario A", is_primary=True, priority=1, config=IPCOM_CONFIG)
    second = _create_provider(client, _headers(admin_session), name_prefix="IpCom QA primario B", is_primary=True, priority=1, config=IPCOM_CONFIG)
    response = client.get("/api/telephony/providers", headers=_headers(admin_session))
    assert response.status_code == 200, response.text
    by_id = {item["id"]: item for item in response.json()}
    assert by_id[first["id"]]["is_primary"] is False
    assert by_id[second["id"]]["is_primary"] is True


def test_tenant_admin_cannot_list_other_tenant_provider(client: Any, admin_session: dict[str, Any], platform_headers: dict[str, str], other_tenant_id: int) -> None:
    provider = _create_provider(
        client,
        platform_headers,
        tenant_id=other_tenant_id,
        name_prefix="PBX QA otro tenant",
        provider_type="manual",
    )
    response = client.get("/api/telephony/providers", headers=_headers(admin_session))
    assert response.status_code == 200, response.text
    assert all(item["id"] != provider["id"] for item in response.json())


def test_provider_config_rejects_sensitive_keys(client: Any, admin_session: dict[str, Any]) -> None:
    response = client.post(
        "/api/telephony/providers",
        headers=_headers(admin_session),
        json={"name": f"PBX secreto QA {time.time_ns()}", "provider_type": "manual", "config": {"ami_secret": "no-versionar"}},
    )
    assert response.status_code == 422, response.text


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
    response = client.post("/api/telephony/click-to-call", headers=_headers(agent_session), json={"customer_id": customer["id"], "phone_number": "3001234567"})
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["ok"] is True
    assert payload["call_log_id"] == payload["call_log"]["id"]
    assert payload["mode"] in {"manual", "simulated"}
    assert payload["call_log"]["customer_id"] == customer["id"]
    assert payload["call_log"]["call_status"] == "initiated"
    assert payload["call_log"]["metadata"]["real_call_executed"] is False
    assert payload["call_log"]["metadata"]["extension_number"]


def test_click_to_call_uses_primary_provider_and_ipcom_dialing(client: Any, admin_session: dict[str, Any], agent_session: dict[str, Any]) -> None:
    provider = _create_provider(
        client,
        _headers(admin_session),
        name_prefix="IpCom QA",
        provider_type="sip_trunk",
        host="35.192.135.117",
        port=5060,
        is_primary=True,
        outbound_enabled=True,
        priority=1,
        config=IPCOM_CONFIG,
    )
    _create_extension(client, _headers(admin_session), agent_session["user"]["id"], provider["id"], "76QA")
    customer = _first_customer(client, _headers(agent_session))
    response = client.post(
        "/api/telephony/click-to-call",
        headers=_headers(agent_session),
        json={"customer_id": customer["id"], "phone_number": "300 123-4567"},
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    metadata = payload["call_log"]["metadata"]
    assert payload["mode"] == "simulated"
    assert payload["call_log"]["provider_id"] == provider["id"]
    assert payload["call_log"]["management_activity_id"]
    assert metadata["dial_string"] == "0218739#0001573001234567"
    assert metadata["provider_is_primary"] is True
    assert metadata["real_call_executed"] is False


def test_invalid_phone_does_not_start_click_to_call(client: Any, admin_session: dict[str, Any], agent_session: dict[str, Any]) -> None:
    provider = _create_provider(client, _headers(admin_session))
    _create_extension(client, _headers(admin_session), agent_session["user"]["id"], provider["id"], "75QA")
    customer = _first_customer(client, _headers(agent_session))
    response = client.post("/api/telephony/click-to-call", headers=_headers(agent_session), json={"customer_id": customer["id"], "phone_number": "2012345678"})
    assert response.status_code == 422, response.text
    assert "celular colombiano" in response.text


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
        payload = response.json()["detail"]
        assert payload["ok"] is False
        assert payload["code"] == "extension_not_configured"
        assert "extension telefonica configurada" in payload["message"]
    finally:
        restored = client.patch(f"/api/telephony/extensions/{extension['id']}", headers=_headers(admin_session), json={"is_active": True})
        assert restored.status_code == 200, restored.text


def test_call_log_scope_for_agent_and_leader(client: Any, admin_session: dict[str, Any], agent_session: dict[str, Any], leader_session: dict[str, Any]) -> None:
    provider = _create_provider(client, _headers(admin_session))
    _create_extension(client, _headers(admin_session), agent_session["user"]["id"], provider["id"], "79QA")
    customer = _first_customer(client, _headers(agent_session))
    created = client.post("/api/telephony/click-to-call", headers=_headers(agent_session), json={"customer_id": customer["id"], "phone_number": "3001234567"})
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


@pytest.mark.safe_static
def test_ipcom_dialing_rule_builds_expected_dial_string() -> None:
    provider = TelephonyProvider(
        tenant_id=1,
        name="IpCom",
        provider_type="sip_trunk",
        host="35.192.135.117",
        port=5060,
        is_active=True,
        config_json='{"external_prefix":"0218739#","mobile_prepend":"000157","mobile_match_pattern":"3XXXXXXXXX"}',
    )
    dialing = telephony_routes._dial_string_for_provider(provider, "(300) 123-4567")
    assert dialing["normalized_phone"] == "3001234567"
    assert dialing["dial_string"] == "0218739#0001573001234567"


@pytest.mark.safe_static
def test_invalid_mobile_number_is_rejected_before_dialing() -> None:
    with pytest.raises(HTTPException) as exc_info:
        telephony_routes._dial_string_for_provider(None, "2012345678")
    assert exc_info.value.status_code == 422
    assert "celular colombiano" in str(exc_info.value.detail)


@pytest.mark.safe_static
def test_provider_config_blocks_secret_like_keys() -> None:
    with pytest.raises(HTTPException) as exc_info:
        telephony_routes._assert_safe_config({"ami_secret": "no-versionar"})
    assert exc_info.value.status_code == 422
    assert "credenciales sensibles" in str(exc_info.value.detail)


@pytest.mark.safe_static
def test_frontend_click_to_call_does_not_open_external_protocols() -> None:
    app_js = Path(__file__).resolve().parents[2] / "frontend" / "static" / "assets" / "app.js"
    content = app_js.read_text(encoding="utf-8")
    forbidden_snippets = [
        "return `tel:",
        "href=\"tel:",
        "href='tel:",
        "window.location",
        "location.href",
        "window.open(\"tel:",
        "window.open('tel:",
        "sip:",
        "callto:",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in content
