from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LeadCreate(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    assigned_user_id: int | None = None
    name: str = Field(min_length=2, max_length=220)
    company: str | None = None
    document: str | None = None
    phone: str | None = None
    email: str | None = None
    source: str | None = None
    interest: str | None = None
    status: str = "new"
    priority: str = "medium"
    notes: str | None = None


class LeadPatch(BaseModel):
    project_id: int | None = None
    assigned_user_id: int | None = None
    name: str | None = None
    company: str | None = None
    document: str | None = None
    phone: str | None = None
    email: str | None = None
    source: str | None = None
    interest: str | None = None
    status: str | None = None
    priority: str | None = None
    notes: str | None = None


class LeadOut(LeadCreate):
    id: int
    tenant_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OpportunityCreate(BaseModel):
    tenant_id: int | None = None
    lead_id: int | None = None
    customer_id: int | None = None
    assigned_user_id: int | None = None
    name: str = Field(min_length=2, max_length=220)
    amount: int = 0
    stage: str = "qualification"
    probability: int = 0
    expected_close_date: datetime | None = None
    status: str = "open"
    lost_reason: str | None = None
    notes: str | None = None


class OpportunityPatch(BaseModel):
    lead_id: int | None = None
    customer_id: int | None = None
    assigned_user_id: int | None = None
    name: str | None = None
    amount: int | None = None
    stage: str | None = None
    probability: int | None = None
    expected_close_date: datetime | None = None
    status: str | None = None
    lost_reason: str | None = None
    notes: str | None = None


class OpportunityOut(OpportunityCreate):
    id: int
    tenant_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
