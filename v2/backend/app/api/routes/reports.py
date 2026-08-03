from __future__ import annotations

import csv
from io import StringIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import User
from app.schemas.reports import OperationalReportResponse, OperationalReportsMeta
from app.services.operational_reports import (
    REPORT_LABELS,
    REPORT_PAGE_SIZE,
    OperationalReportFilters,
    available_reports,
    build_operational_report,
    build_operational_report_export,
)


router = APIRouter()


def report_filters(
    tenant_id: int | None = None,
    project_id: int | None = None,
    user_id: int | None = None,
    advisor_id: int | None = None,
    leader_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    status: str | None = None,
    channel: str | None = None,
    result: str | None = None,
    risk: str | None = None,
    search: str | None = None,
    typification: str | None = None,
    min_score: int | None = None,
    effective: bool | None = None,
    min_dpd: int | None = None,
    max_dpd: int | None = None,
    min_balance: int | None = None,
    max_balance: int | None = None,
    no_management: bool | None = None,
    active_promise: bool | None = None,
    contact_restriction: bool | None = None,
    overdue: bool | None = None,
    fulfilled: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=REPORT_PAGE_SIZE, ge=1, le=REPORT_PAGE_SIZE),
) -> OperationalReportFilters:
    from datetime import date

    def parse_date(value: str | None) -> date | None:
        return date.fromisoformat(value) if value else None

    return OperationalReportFilters(
        tenant_id=tenant_id,
        project_id=project_id,
        user_id=user_id,
        advisor_id=advisor_id,
        leader_id=leader_id,
        date_from=parse_date(date_from),
        date_to=parse_date(date_to),
        status=status,
        channel=channel,
        result=result,
        risk=risk,
        search=search,
        typification=typification,
        min_score=min_score,
        effective=effective,
        min_dpd=min_dpd,
        max_dpd=max_dpd,
        min_balance=min_balance,
        max_balance=max_balance,
        no_management=no_management,
        active_promise=active_promise,
        contact_restriction=contact_restriction,
        overdue=overdue,
        fulfilled=fulfilled,
        page=page,
        page_size=page_size,
    )


@router.get("/operational/meta", response_model=OperationalReportsMeta)
def operational_reports_meta(
    tenant_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    return {"reports": available_reports(db, user, tenant_id), "page_size": REPORT_PAGE_SIZE, "agent_restricted": True}


@router.get("/operational/clients", response_model=OperationalReportResponse)
def operational_clients_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "clients", filters)


@router.get("/operational/activities", response_model=OperationalReportResponse)
def operational_activities_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "activities", filters)


@router.get("/operational/promises", response_model=OperationalReportResponse)
def operational_promises_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "promises", filters)


@router.get("/operational/payments", response_model=OperationalReportResponse)
def operational_payments_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "payments", filters)


@router.get("/operational/agreements", response_model=OperationalReportResponse)
def operational_agreements_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "agreements", filters)


@router.get("/operational/productivity-hourly", response_model=OperationalReportResponse)
def operational_productivity_hourly_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "productivity-hourly", filters)


@router.get("/operational/productivity-advisor", response_model=OperationalReportResponse)
def operational_productivity_advisor_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "productivity-advisor", filters)


@router.get("/operational/demographics", response_model=OperationalReportResponse)
def operational_demographics_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "demographics", filters)


@router.get("/operational/tasks", response_model=OperationalReportResponse)
def operational_tasks_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "tasks", filters)


@router.get("/operational/careflow", response_model=OperationalReportResponse)
def operational_careflow_report(filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return build_operational_report(db, user, "careflow", filters)


@router.get("/operational/{report_code}/export")
def export_operational_report(report_code: str, filters: OperationalReportFilters = Depends(report_filters), db: Session = Depends(get_db), user: User = Depends(current_user)) -> StreamingResponse:
    result = build_operational_report_export(db, user, report_code, filters)
    output = StringIO()
    writer = csv.writer(output)
    columns = result.get("columns") or []
    writer.writerow([column["label"] for column in columns])
    for item in result.get("items") or []:
        writer.writerow([item.get(column["key"], "") for column in columns])
    output.seek(0)
    filename = f"iep_reporte_{REPORT_LABELS.get(report_code, report_code).lower().replace(' ', '_')}.csv"
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
