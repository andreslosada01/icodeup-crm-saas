from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LegalCaseCreate(BaseModel):
    customer_id: int
    assigned_lawyer_id: int | None = None
    case_number: str | None = None
    process_type: str = Field(min_length=2, max_length=120)
    court_name: str | None = None
    amount: int = 0
    status: str = "open"
    stage: str | None = None
    risk: str = "medium"
    next_action: str | None = None
    next_deadline_at: datetime | None = None
    notes: str | None = None


class LegalCasePatch(BaseModel):
    assigned_lawyer_id: int | None = None
    case_number: str | None = None
    process_type: str | None = None
    court_name: str | None = None
    amount: int | None = None
    status: str | None = None
    stage: str | None = None
    risk: str | None = None
    next_action: str | None = None
    next_deadline_at: datetime | None = None
    notes: str | None = None


class LegalCaseOut(BaseModel):
    id: int
    tenant_id: int
    project_id: int | None = None
    customer_id: int
    assigned_lawyer_id: int | None = None
    case_number: str | None = None
    process_type: str
    court_name: str | None = None
    amount: int
    status: str
    stage: str | None = None
    risk: str
    next_action: str | None = None
    next_deadline_at: datetime | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LegalActionCreate(BaseModel):
    action_type: str = Field(min_length=2, max_length=120)
    description: str | None = None
    action_date: datetime
    next_deadline_at: datetime | None = None


class LegalActionOut(LegalActionCreate):
    id: int
    tenant_id: int
    legal_case_id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LegalHearingCreate(BaseModel):
    hearing_type: str = Field(min_length=2, max_length=120)
    scheduled_at: datetime
    location: str | None = None
    status: str = "scheduled"
    notes: str | None = None


class LegalHearingOut(LegalHearingCreate):
    id: int
    tenant_id: int
    legal_case_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LegalDeadlineOut(BaseModel):
    id: int
    tenant_id: int
    legal_case_id: int
    title: str
    due_at: datetime
    status: str
    priority: str
    created_at: datetime

    model_config = {"from_attributes": True}
