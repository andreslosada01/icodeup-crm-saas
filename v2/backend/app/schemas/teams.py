from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


TEAM_PROJECT_ROLES = {"admin", "coordinator", "leader", "agent", "quality", "quality_supervisor", "lawyer", "sales", "auditor", "viewer"}


class TeamProjectOut(BaseModel):
    id: int
    tenant_id: int
    name: str
    code: str
    status: str
    leader_count: int = 0
    agent_count: int = 0
    user_count: int = 0
    customer_count: int = 0
    obligation_count: int = 0
    balance_total: int = 0


class ProjectUserAssignmentCreate(BaseModel):
    user_id: int
    role_in_project: str = "agent"
    is_active: bool = True

    @field_validator("role_in_project")
    @classmethod
    def validate_role(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in TEAM_PROJECT_ROLES:
            raise ValueError("Rol en proyecto no soportado.")
        return normalized


class ProjectUserAssignmentPatch(BaseModel):
    role_in_project: str | None = None
    is_active: bool | None = None

    @field_validator("role_in_project")
    @classmethod
    def validate_role(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in TEAM_PROJECT_ROLES:
            raise ValueError("Rol en proyecto no soportado.")
        return normalized


class ProjectUserAssignmentOut(BaseModel):
    id: int
    tenant_id: int | None = None
    project_id: int
    project_name: str | None = None
    user_id: int
    user_name: str | None = None
    user_email: str | None = None
    user_role: str | None = None
    profile_role: str | None = None
    role_in_project: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


class TeamUserOut(BaseModel):
    id: int
    tenant_id: int
    name: str
    email: str
    role: str
    profile_role: str | None = None
    title: str | None = None
    status: str
    leader_id: int | None = None
    leader_name: str | None = None
    project_ids: list[int] = Field(default_factory=list)
    project_names: list[str] = Field(default_factory=list)


class LeaderAgentAssignmentCreate(BaseModel):
    agent_user_id: int
    project_id: int | None = None


class AssignmentUpdateResult(BaseModel):
    ok: bool = True
    detail: str


class CustomerAssignmentUpdate(BaseModel):
    assigned_user_id: int | None = None
    project_id: int | None = None


class ObligationAssignmentUpdate(BaseModel):
    assigned_user_id: int | None = None
    assigned_leader_id: int | None = None
    project_id: int | None = None


class LeaderSummaryOut(BaseModel):
    leader_id: int
    leader_name: str
    total_agents: int
    customers: int
    obligations: int
    balance_total: int
    activities_today: int
    active_promises: int
    overdue_promises: int
    payments_month: int
    active_agreements: int
    stale_customers: int
    ranking: list[dict] = Field(default_factory=list)
