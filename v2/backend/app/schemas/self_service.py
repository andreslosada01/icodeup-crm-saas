from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.teams import ProjectUserAssignmentOut, TeamProjectOut


class ScoringRuleOut(BaseModel):
    id: int | None = None
    code: str
    name: str
    description: str | None = None
    source: str = "business_rules"
    condition: dict[str, Any] = Field(default_factory=dict)
    action: dict[str, Any] = Field(default_factory=dict)
    severity: str = "medium"
    is_active: bool = True


class ManagementScoreOut(BaseModel):
    activity_id: int
    customer_id: int
    customer_name: str | None = None
    project_id: int | None = None
    obligation_id: int | None = None
    obligation_number: str | None = None
    user_id: int
    user_name: str | None = None
    channel: str
    result: str
    note: str | None = None
    created_at: datetime
    score: int
    label: str
    is_effective: bool
    scoring_source: str


class CustomerManagementInsightsOut(BaseModel):
    customer_id: int
    customer_name: str
    best_current_month: ManagementScoreOut | None = None
    best_previous_month: ManagementScoreOut | None = None
    best_historical: ManagementScoreOut | None = None
    recent: list[ManagementScoreOut] = Field(default_factory=list)


class AdvisorManagementInsightsOut(BaseModel):
    user_id: int
    user_name: str
    activities_today: int = 0
    activities_month: int = 0
    effective_month: int = 0
    promises_created_month: int = 0
    payments_month: int = 0
    agreements_created_month: int = 0
    best_current_month: ManagementScoreOut | None = None
    best_historical: ManagementScoreOut | None = None


class OperationalCenterOut(BaseModel):
    selected_project: TeamProjectOut | None = None
    projects: list[TeamProjectOut] = Field(default_factory=list)
    assignments: list[ProjectUserAssignmentOut] = Field(default_factory=list)
    active_modules: list[dict[str, Any]] = Field(default_factory=list)
    scoring_rules: list[ScoringRuleOut] = Field(default_factory=list)
    alert_rules: list[dict[str, Any]] = Field(default_factory=list)
    users_summary: dict[str, int] = Field(default_factory=dict)


class SessionPriorityOut(BaseModel):
    id: str
    role_group: str
    title: str
    message: str
    severity: str = "medium"
    value: str | None = None
    action: str | None = None
    entity_type: str | None = None
    entity_id: int | None = None


class SessionSummaryOut(BaseModel):
    role_group: str
    generated_at: datetime
    priorities: list[SessionPriorityOut] = Field(default_factory=list)
    settings: dict[str, int] = Field(default_factory=dict)
