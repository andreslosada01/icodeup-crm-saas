from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import User
from app.schemas.alerts import AlertOut, AlertSummaryOut
from app.services.access_control import require_permission
from app.services.alert_engine import collect_alerts, summarize_alerts


router = APIRouter()


@router.get("", response_model=list[AlertOut])
def list_alerts(
    module: str | None = None,
    severity: str | None = None,
    status: str | None = "open",
    tenant_id: int | None = None,
    assigned_to_me: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
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
    alerts = collect_alerts(db, user, module=module, tenant_id=tenant_id, limit=200)
    return summarize_alerts(alerts)
