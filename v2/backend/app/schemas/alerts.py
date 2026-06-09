from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: str
    tenant_id: int
    module: str
    entity_type: str
    entity_id: int | None = None
    title: str
    message: str
    severity: str
    status: str = "open"
    due_at: datetime | None = None
    assigned_user_id: int | None = None
    action: str | None = None


class AlertSummaryOut(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    by_module: dict[str, int]
