from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SaasPlanBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    code: str = Field(min_length=2, max_length=80)
    description: str | None = None
    base_price: int = 0
    monthly_price: int = 0
    max_users: int = 0
    max_projects: int = 0
    max_customers: int = 0
    max_storage_mb: int = 0
    max_records: int = 0
    includes_ai: bool = False
    includes_advanced_bi: bool = False
    includes_sales: bool = False
    includes_collections: bool = True
    includes_legal: bool = False
    includes_documents: bool = False
    includes_bi: bool = True
    includes_integrations: bool = False
    status: str = "active"
    is_active: bool = True


class SaasPlanCreate(SaasPlanBase):
    pass


class SaasPlanOut(SaasPlanBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantSubscriptionUpsert(BaseModel):
    plan_id: int
    start_date: datetime | None = None
    end_date: datetime | None = None
    renewal_date: datetime | None = None
    status: str = "active"
    billing_cycle: str = "monthly"
    notes: str | None = None


class TenantSubscriptionOut(TenantSubscriptionUpsert):
    id: int
    tenant_id: int
    created_at: datetime
    plan: SaasPlanOut | None = None

    model_config = {"from_attributes": True}


class TenantModuleIn(BaseModel):
    module_code: str
    enabled: bool = True
    is_enabled: bool | None = None
    configuration_json: str | None = None


class TenantModuleOut(TenantModuleIn):
    id: int
    tenant_id: int
    module_id: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ModuleOut(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    category: str
    base_price: int
    is_active: bool
    icon: str | None = None
    order: int
    created_at: datetime

    model_config = {"from_attributes": True}
