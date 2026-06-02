from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PermissionOut(BaseModel):
    id: int
    code: str
    name: str
    module_code: str | None = None
    description: str | None = None

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    code: str | None = Field(default=None, max_length=80)
    description: str | None = None
    permission_codes: list[str] = Field(default_factory=list)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if not value:
            return value
        return value.strip().lower().replace(" ", "_")


class RolePatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = None
    is_active: bool | None = None


class RolePermissionsUpdate(BaseModel):
    permission_codes: list[str] = Field(default_factory=list)


class RoleOut(BaseModel):
    id: int
    tenant_id: int | None = None
    code: str
    name: str
    description: str | None = None
    is_system_role: bool
    is_active: bool
    permission_codes: list[str] = Field(default_factory=list)
    user_count: int = 0


class UserRoleAssign(BaseModel):
    role_id: int


class ModuleStatusOut(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    category: str
    icon: str | None = None
    order: int
    is_active: bool
    tenant_module_id: int | None = None
    enabled: bool = False
    is_enabled: bool = False
    configuration_json: str | None = None
    related_permission_count: int = 0
    critical_permission_count: int = 0
    users_with_access: int = 0
    primary_roles: list[str] = Field(default_factory=list)
    deactivation_impact: str | None = None
    commercial_recommendation: str | None = None


class TenantModuleToggle(BaseModel):
    module_code: str
    enabled: bool
    configuration_json: str | None = None


class TenantSettingsOut(BaseModel):
    tenant_id: int
    name: str
    slug: str
    document_type: str | None = None
    document_number: str | None = None
    logo_url: str | None = None
    primary_color: str
    secondary_color: str
    timezone: str
    login_headline: str | None = None
    login_subheadline: str | None = None


class TenantSettingsPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    document_type: str | None = Field(default=None, max_length=40)
    document_number: str | None = Field(default=None, max_length=80)
    logo_url: str | None = Field(default=None, max_length=420)
    primary_color: str | None = Field(default=None, max_length=20)
    secondary_color: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=80)
    login_headline: str | None = Field(default=None, max_length=180)
    login_subheadline: str | None = Field(default=None, max_length=260)


class AuditLogOut(BaseModel):
    id: int
    tenant_id: int | None = None
    user_id: int | None = None
    module: str | None = None
    entity_type: str
    entity_id: int | None = None
    object_type: str | None = None
    object_id: int | None = None
    action: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PartyCreate(BaseModel):
    tenant_id: int | None = None
    party_type: str = Field(default="person", max_length=40)
    display_name: str = Field(min_length=2, max_length=220)
    legal_name: str | None = Field(default=None, max_length=240)
    document_type: str | None = Field(default=None, max_length=40)
    document_number: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=180)
    phone: str | None = Field(default=None, max_length=80)
    city: str | None = Field(default=None, max_length=120)
    status: str = Field(default="active", max_length=40)
    is_customer: bool = False
    is_debtor: bool = False
    is_supplier: bool = False
    is_employee: bool = False
    is_contact: bool = False
    is_prospect: bool = False
    external_ref: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class PartyPatch(BaseModel):
    party_type: str | None = Field(default=None, max_length=40)
    display_name: str | None = Field(default=None, min_length=2, max_length=220)
    legal_name: str | None = Field(default=None, max_length=240)
    document_type: str | None = Field(default=None, max_length=40)
    document_number: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=180)
    phone: str | None = Field(default=None, max_length=80)
    city: str | None = Field(default=None, max_length=120)
    status: str | None = Field(default=None, max_length=40)
    is_customer: bool | None = None
    is_debtor: bool | None = None
    is_supplier: bool | None = None
    is_employee: bool | None = None
    is_contact: bool | None = None
    is_prospect: bool | None = None
    external_ref: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class PartyOut(PartyCreate):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
