from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OperationalReportColumn(BaseModel):
    key: str
    label: str
    type: str = "text"


class OperationalReportKpi(BaseModel):
    key: str
    label: str
    value: int | float | str
    detail: str | None = None
    tone: str = "neutral"


class OperationalReportResponse(BaseModel):
    report: str
    title: str
    generated_at: datetime
    available: bool = True
    note: str | None = None
    columns: list[OperationalReportColumn] = Field(default_factory=list)
    kpis: list[OperationalReportKpi] = Field(default_factory=list)
    items: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 1
    filters: dict[str, Any] = Field(default_factory=dict)


class OperationalReportsMeta(BaseModel):
    reports: list[dict[str, Any]]
    page_size: int = 10
    agent_restricted: bool = True
