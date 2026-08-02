from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import User
from app.schemas.alerts import AlertOut, AlertSummaryOut
from app.schemas.self_service import SessionSummaryOut
from app.services.access_control import require_permission
from app.services.alert_engine import collect_alerts, summarize_alerts
from app.services.collections_self_service import build_session_summary


router = APIRouter()


@router.get("", response_model=list[AlertOut])
def list_alerts(
    module: str | None = None,
    severity: str | None = None,
    status: str | None = "open",
    tenant_id: int | None = None,
    assigned_to_me: bool = False,
    limit: int = Query(default=10, ge=1, le=10),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[dict]:
    require_permission(db, user, "alerts.view")
    return collect_alerts(db, user, module=module, severity=severity, status=status, tenant_id=tenant_id, assigned_to_me=assigned_to_me, limit=limit)


@router.get("/summary", response_model=AlertSummaryOut)
def alert_summary(
    module: str | None = None,
    tenant_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    require_permission(db, user, "alerts.view")
    alerts = collect_alerts(db, user, module=module, tenant_id=tenant_id, limit=10)
    return summarize_alerts(alerts)


@router.get("/session-summary", response_model=SessionSummaryOut)
def session_summary(
    tenant_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> SessionSummaryOut:
    require_permission(db, user, "alerts.view")
    return build_session_summary(db, user, tenant_id=tenant_id)
