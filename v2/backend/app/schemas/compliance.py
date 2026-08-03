from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


CONTACT_CHANNELS = {"phone", "whatsapp", "email", "sms", "presencial", "web", "manual"}
CONTACT_SEVERITIES = {"info", "warning", "block"}


class ContactRuleBase(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    code: str | None = Field(default=None, max_length=120)
    name: str = Field(min_length=2, max_length=220)
    description: str | None = None
    channels: list[str] = Field(default_factory=list)
    blocked_channels: list[str] = Field(default_factory=list)
    allowed_days: list[str] = Field(default_factory=list)
    start_time: str | None = None
    end_time: str | None = None
    max_attempts_per_day: int | None = Field(default=None, ge=0)
    max_attempts_per_week: int | None = Field(default=None, ge=0)
    max_attempts_per_channel_day: int | None = Field(default=None, ge=0)
    blocked_customer_ids: list[int] = Field(default_factory=list)
    blocked_obligation_ids: list[int] = Field(default_factory=list)
    restricted_contactability_values: list[str] = Field(default_factory=list)
    requires_consent: bool = False
    consent_granted: bool | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    severity: str = "warning"
    priority: int = 100
    recommended_action: str | None = None
    is_active: bool = True


class ContactRuleCreate(ContactRuleBase):
    pass


class ContactRulePatch(BaseModel):
    project_id: int | None = None
    code: str | None = Field(default=None, max_length=120)
    name: str | None = Field(default=None, min_length=2, max_length=220)
    description: str | None = None
    channels: list[str] | None = None
    blocked_channels: list[str] | None = None
    allowed_days: list[str] | None = None
    start_time: str | None = None
    end_time: str | None = None
    max_attempts_per_day: int | None = Field(default=None, ge=0)
    max_attempts_per_week: int | None = Field(default=None, ge=0)
    max_attempts_per_channel_day: int | None = Field(default=None, ge=0)
    blocked_customer_ids: list[int] | None = None
    blocked_obligation_ids: list[int] | None = None
    restricted_contactability_values: list[str] | None = None
    requires_consent: bool | None = None
    consent_granted: bool | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    severity: str | None = None
    priority: int | None = None
    recommended_action: str | None = None
    is_active: bool | None = None


class ContactRuleOut(ContactRuleBase):
    id: int
    condition: dict[str, Any] = Field(default_factory=dict)
    action: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ContactRuleListResponse(BaseModel):
    items: list[ContactRuleOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class MatchedContactRuleOut(BaseModel):
    id: int
    code: str
    name: str
    severity: str
    decision: str
    reason: str
    priority: int = 100


class ContactEvaluationRequest(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    customer_id: int
    obligation_id: int | None = None
    channel: str = Field(min_length=2, max_length=40)
    current_at: datetime | None = None
    source: str | None = None


class ContactEvaluationOut(BaseModel):
    allowed: bool
    severity: str
    reason: str
    matched_rules: list[MatchedContactRuleOut] = Field(default_factory=list)
    recommended_action: str | None = None
    channels_available: list[str] = Field(default_factory=list)
    attempts_today: int = 0
    attempts_week: int = 0
    attempts_by_channel_today: dict[str, int] = Field(default_factory=dict)
    next_window: str | None = None


class ContactStatusOut(BaseModel):
    customer_id: int
    tenant_id: int
    project_id: int | None = None
    status: str
    severity: str
    reason: str
    channels_enabled: list[str] = Field(default_factory=list)
    last_contact_by_channel: dict[str, str | None] = Field(default_factory=dict)
    attempts_today: int = 0
    attempts_week: int = 0
    attempts_by_channel_today: dict[str, int] = Field(default_factory=dict)
    active_restrictions: list[MatchedContactRuleOut] = Field(default_factory=list)
    next_window: str | None = None
