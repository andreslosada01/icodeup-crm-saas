from pydantic import BaseModel, Field, field_validator

from app.core.roles import ALL_ROLES, PLATFORM_ADMIN, ROLE_LABELS, TENANT_ADMIN, TENANT_ROLES


class RoleOption(BaseModel):
    value: str
    label: str


class AdminOverview(BaseModel):
    tenants: int
    projects: int
    users: int
    customers: int
    active_tenants: int


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(min_length=2, max_length=120)
    tax_id: str | None = Field(default=None, max_length=80)
    notes: str | None = None

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        return value.strip().lower().replace(" ", "-")


class TenantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    slug: str | None = Field(default=None, min_length=2, max_length=120)
    tax_id: str | None = Field(default=None, max_length=80)
    status: str | None = Field(default=None, max_length=30)
    notes: str | None = None

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip().lower().replace(" ", "-")


class TenantAdminOut(BaseModel):
    id: int
    name: str
    slug: str
    tax_id: str | None = None
    status: str
    notes: str | None = None
    project_count: int = 0
    user_count: int = 0
    customer_count: int = 0


class ProjectCreate(BaseModel):
    tenant_id: int
    name: str = Field(min_length=2, max_length=180)
    code: str = Field(min_length=2, max_length=80)
    description: str | None = None
    status: str = "active"

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper().replace(" ", "-")


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    code: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = None
    status: str | None = Field(default=None, max_length=30)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip().upper().replace(" ", "-")


class ProjectOut(BaseModel):
    id: int
    tenant_id: int
    tenant_name: str
    name: str
    code: str
    description: str | None = None
    status: str
    assigned_user_count: int = 0
    customer_count: int = 0


class UserCreate(BaseModel):
    tenant_id: int
    name: str = Field(min_length=2, max_length=180)
    email: str = Field(min_length=5, max_length=180)
    role: str = TENANT_ADMIN
    password: str = Field(min_length=8, max_length=72)
    phone: str | None = Field(default=None, max_length=80)
    title: str | None = Field(default=None, max_length=120)
    leader_id: int | None = None
    project_ids: list[int] = Field(default_factory=list)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value == PLATFORM_ADMIN or value not in ALL_ROLES:
            raise ValueError("Rol no permitido para usuarios de empresa.")
        return value


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    email: str | None = Field(default=None, min_length=5, max_length=180)
    role: str | None = None
    status: str | None = Field(default=None, max_length=30)
    password: str | None = Field(default=None, min_length=8, max_length=72)
    phone: str | None = Field(default=None, max_length=80)
    title: str | None = Field(default=None, max_length=120)
    leader_id: int | None = None
    project_ids: list[int] | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip().lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value == PLATFORM_ADMIN or value not in ALL_ROLES:
            raise ValueError("Rol no permitido para usuarios de empresa.")
        return value


class ProjectAssignmentIn(BaseModel):
    project_ids: list[int] = Field(default_factory=list)


class UserOut(BaseModel):
    id: int
    tenant_id: int
    tenant_name: str
    name: str
    email: str
    role: str
    role_label: str
    status: str
    phone: str | None = None
    title: str | None = None
    leader_id: int | None = None
    leader_name: str | None = None
    project_ids: list[int] = Field(default_factory=list)
    project_names: list[str] = Field(default_factory=list)


def role_options() -> list[RoleOption]:
    order = [TENANT_ADMIN, "coordinator", "quality_supervisor", "agent"]
    return [RoleOption(value=value, label=ROLE_LABELS[value]) for value in order if value in TENANT_ROLES]
