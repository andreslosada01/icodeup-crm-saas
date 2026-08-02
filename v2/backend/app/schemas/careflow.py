from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


CARE_CHANNEL_PATTERN = "^(llamada|whatsapp|email|web|presencial|interno)$"
CARE_PRIORITY_PATTERN = "^(baja|media|alta|critica)$"
CARE_STATUS_PATTERN = "^(nuevo|asignado|en_proceso|pendiente_cliente|pendiente_interno|resuelto|cerrado|cancelado)$"
CARE_EVENT_PATTERN = "^(comentario|cambio_estado|asignacion|nota|adjunto|cierre|reapertura)$"
CARE_SLA_PATTERN = "^(en_tiempo|proximo_a_vencer|vencido)$"


class CareCaseCategoryCreate(BaseModel):
    tenant_id: int | None = None
    name: str = Field(min_length=2, max_length=160)
    description: str | None = None
    default_priority: str = Field(default="media", pattern=CARE_PRIORITY_PATTERN)
    default_sla_hours: int = Field(default=48, ge=1, le=720)
    is_active: bool = True


class CareCaseCategoryOut(BaseModel):
    id: int
    tenant_id: int
    name: str
    description: str | None = None
    default_priority: str
    default_sla_hours: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CareCaseCreate(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    customer_id: int | None = None
    title: str = Field(min_length=3, max_length=220)
    description: str | None = None
    channel: str = Field(default="interno", pattern=CARE_CHANNEL_PATTERN)
    case_type: str | None = Field(default=None, max_length=120)
    category: str | None = Field(default=None, max_length=120)
    priority: str = Field(default="media", pattern=CARE_PRIORITY_PATTERN)
    origin: str | None = Field(default=None, max_length=80)
    assigned_user_id: int | None = None
    due_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CareCasePatch(BaseModel):
    project_id: int | None = None
    customer_id: int | None = None
    title: str | None = Field(default=None, min_length=3, max_length=220)
    description: str | None = None
    channel: str | None = Field(default=None, pattern=CARE_CHANNEL_PATTERN)
    case_type: str | None = Field(default=None, max_length=120)
    category: str | None = Field(default=None, max_length=120)
    priority: str | None = Field(default=None, pattern=CARE_PRIORITY_PATTERN)
    status: str | None = Field(default=None, pattern=CARE_STATUS_PATTERN)
    origin: str | None = Field(default=None, max_length=80)
    due_at: datetime | None = None
    metadata: dict[str, Any] | None = None


class CareCaseEventCreate(BaseModel):
    event_type: str = Field(default="nota", pattern=CARE_EVENT_PATTERN)
    description: str = Field(min_length=2)
    previous_value: str | None = None
    new_value: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CareCaseAssign(BaseModel):
    assigned_user_id: int
    note: str | None = None


class CareCaseClose(BaseModel):
    resolution: str | None = None
    status: str = Field(default="cerrado", pattern="^(resuelto|cerrado|cancelado)$")


class CareCaseEventOut(BaseModel):
    id: int
    tenant_id: int
    case_id: int
    event_type: str
    description: str
    previous_value: str | None = None
    new_value: str | None = None
    created_by_id: int
    created_by_name: str | None = None
    created_at: datetime
    metadata: dict[str, Any]


class CareCaseOut(BaseModel):
    id: int
    tenant_id: int
    tenant_name: str | None = None
    project_id: int | None = None
    project_name: str | None = None
    customer_id: int | None = None
    customer_name: str | None = None
    case_number: str
    title: str
    description: str | None = None
    channel: str
    case_type: str | None = None
    category: str | None = None
    priority: str
    status: str
    origin: str | None = None
    assigned_user_id: int | None = None
    assigned_user_name: str | None = None
    created_by_id: int
    created_by_name: str | None = None
    closed_by_id: int | None = None
    closed_by_name: str | None = None
    due_at: datetime | None = None
    resolved_at: datetime | None = None
    closed_at: datetime | None = None
    sla_status: str = Field(pattern=CARE_SLA_PATTERN)
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    events: list[CareCaseEventOut] = Field(default_factory=list)


class CareCaseListResponse(BaseModel):
    items: list[CareCaseOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class CareFlowSummaryOut(BaseModel):
    new_cases: int = 0
    assigned_to_me: int = 0
    overdue_cases: int = 0
    due_soon_cases: int = 0
    closed_this_month: int = 0
    unassigned_cases: int = 0
    critical_open_cases: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    by_priority: dict[str, int] = Field(default_factory=dict)
