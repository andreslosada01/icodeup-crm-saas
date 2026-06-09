from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ScopedConfigBase(BaseModel):
    tenant_id: int | None = None
    module: str = Field(min_length=2, max_length=80)
    is_active: bool = True


class FunctionalCatalogCreate(ScopedConfigBase):
    catalog_type: str = Field(min_length=2, max_length=120)
    code: str = Field(min_length=2, max_length=120)
    label: str = Field(min_length=2, max_length=220)
    description: str | None = None
    color: str | None = None
    order: int = 0
    is_system: bool = False


class FunctionalCatalogPatch(BaseModel):
    label: str | None = None
    description: str | None = None
    color: str | None = None
    order: int | None = None
    is_active: bool | None = None
    is_system: bool | None = None


class FunctionalCatalogOut(FunctionalCatalogCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BusinessRuleCreate(ScopedConfigBase):
    rule_type: str = Field(min_length=2, max_length=120)
    code: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=220)
    description: str | None = None
    condition_json: str | None = None
    action_json: str | None = None
    severity: str = "medium"


class BusinessRulePatch(BaseModel):
    name: str | None = None
    description: str | None = None
    condition_json: str | None = None
    action_json: str | None = None
    severity: str | None = None
    is_active: bool | None = None


class BusinessRuleOut(BusinessRuleCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertRuleCreate(ScopedConfigBase):
    code: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=220)
    description: str | None = None
    condition_type: str = Field(min_length=2, max_length=120)
    threshold_days: int = 0
    severity: str = "medium"
    target_role: str | None = None
    message_template: str | None = None


class AlertRulePatch(BaseModel):
    name: str | None = None
    description: str | None = None
    condition_type: str | None = None
    threshold_days: int | None = None
    severity: str | None = None
    target_role: str | None = None
    message_template: str | None = None
    is_active: bool | None = None


class AlertRuleOut(AlertRuleCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowCreate(ScopedConfigBase):
    code: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=220)
    description: str | None = None


class WorkflowPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class WorkflowOut(WorkflowCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowStageCreate(BaseModel):
    code: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=220)
    description: str | None = None
    order: int = 0
    color: str | None = None
    is_final: bool = False
    is_active: bool = True


class WorkflowStagePatch(BaseModel):
    name: str | None = None
    description: str | None = None
    order: int | None = None
    color: str | None = None
    is_final: bool | None = None
    is_active: bool | None = None


class WorkflowStageOut(WorkflowStageCreate):
    id: int
    workflow_id: int

    model_config = {"from_attributes": True}
