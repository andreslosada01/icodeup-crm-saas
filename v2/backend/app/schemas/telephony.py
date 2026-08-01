from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


PROVIDER_TYPE_PATTERN = "^(sip_trunk|asterisk_ami|pbx_ami|pbx_ari|webrtc_sip|external_api|manual)$"


class TelephonyProviderCreate(BaseModel):
    tenant_id: int | None = None
    name: str = Field(min_length=2, max_length=180)
    provider_type: str = Field(default="manual", pattern=PROVIDER_TYPE_PATTERN)
    host: str | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    websocket_url: str | None = None
    api_url: str | None = None
    is_active: bool = True
    is_primary: bool = False
    outbound_enabled: bool = True
    priority: int | None = Field(default=None, ge=1, le=100)
    config: dict[str, Any] = Field(default_factory=dict)


class TelephonyProviderPatch(BaseModel):
    name: str | None = None
    provider_type: str | None = Field(default=None, pattern=PROVIDER_TYPE_PATTERN)
    host: str | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    websocket_url: str | None = None
    api_url: str | None = None
    is_active: bool | None = None
    is_primary: bool | None = None
    outbound_enabled: bool | None = None
    priority: int | None = Field(default=None, ge=1, le=100)
    config: dict[str, Any] | None = None


class TelephonyProviderOut(BaseModel):
    id: int
    tenant_id: int
    name: str
    provider_type: str
    host: str | None = None
    port: int | None = None
    websocket_url: str | None = None
    api_url: str | None = None
    is_active: bool
    is_primary: bool = False
    outbound_enabled: bool = True
    priority: int | None = None
    config: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TelephonyExtensionCreate(BaseModel):
    tenant_id: int | None = None
    user_id: int
    provider_id: int | None = None
    extension_number: str = Field(min_length=2, max_length=40)
    display_name: str | None = None
    sip_username: str | None = None
    sip_domain: str | None = None
    status: str = "not_connected"
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class TelephonyExtensionPatch(BaseModel):
    user_id: int | None = None
    provider_id: int | None = None
    extension_number: str | None = None
    display_name: str | None = None
    sip_username: str | None = None
    sip_domain: str | None = None
    status: str | None = None
    is_active: bool | None = None
    metadata: dict[str, Any] | None = None


class TelephonyExtensionOut(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    user_name: str | None = None
    provider_id: int | None = None
    provider_name: str | None = None
    extension_number: str
    display_name: str | None = None
    sip_username: str | None = None
    sip_domain: str | None = None
    status: str
    is_active: bool
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ClickToCallRequest(BaseModel):
    customer_id: int
    obligation_id: int | None = None
    phone_number: str | None = None
    source: str | None = None


class FinishCallLogRequest(BaseModel):
    call_status: str = Field(default="completed", pattern="^(initiated|ringing|answered|missed|failed|completed)$")
    duration_seconds: int | None = Field(default=None, ge=0)
    external_call_id: str | None = None
    recording_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CallLogOut(BaseModel):
    id: int
    tenant_id: int
    provider_id: int | None = None
    provider_name: str | None = None
    user_id: int
    user_name: str | None = None
    customer_id: int | None = None
    customer_name: str | None = None
    obligation_id: int | None = None
    obligation_number: str | None = None
    phone_number: str
    direction: str
    call_status: str
    started_at: datetime
    answered_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int
    external_call_id: str | None = None
    recording_url: str | None = None
    management_activity_id: int | None = None
    metadata: dict[str, Any]


class ClickToCallResponse(BaseModel):
    ok: bool
    mode: str
    message: str
    call_log_id: int
    call_log: CallLogOut
