from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import ManagementActivity, PaymentPromise, TypificationNode, User
from app.schemas.crm import ActivityCreate, ActivityOut
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, TENANT_ADMIN
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin, require_permission, user_has_permission
from app.services.audit_service import record_audit

from .access import activity_to_out, customer_for_access, ensure_read_access
from .utils import next_action_for, priority_score


router = APIRouter()


def _can_create_activity(db: Session, user: User) -> bool:
    if is_platform_admin(db, user) or is_company_admin(db, user):
        return True
    if user.role in {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}:
        return True
    if user_has_permission(db, user, "crm.activities.create"):
        return True
    profile_role = get_profile_role_code(db, user)
    return user.role == AGENT and profile_role in {"collections_agent", "collections_leader"}


@router.get("/customers/{customer_id}/activities", response_model=list[ActivityOut])
def list_activities(customer_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ActivityOut]:
    if not user_has_permission(db, user, "crm.activities.view"):
        require_permission(db, user, "crm.clients.view")
    ensure_read_access(user)
    customer_for_access(db, customer_id, user)
    activities = list(db.scalars(select(ManagementActivity).where(ManagementActivity.customer_id == customer_id).order_by(ManagementActivity.created_at.desc()).limit(10)))
    return [activity_to_out(db, item) for item in activities]


@router.post("/customers/{customer_id}/activities", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(customer_id: int, payload: ActivityCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ActivityOut:
    if not _can_create_activity(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para gestionar este cliente.")
    ensure_read_access(user)
    customer = customer_for_access(db, customer_id, user, write=True)
    typification = db.get(TypificationNode, payload.typification_id) if payload.typification_id else None
    if typification and typification.tenant_id != customer.tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tipificacion fuera de la empresa.")
    result = typification.next_status if typification and typification.next_status else payload.result
    activity = ManagementActivity(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        user_id=user.id,
        typification_id=payload.typification_id,
        channel=payload.channel,
        result=result,
        note=payload.note,
        next_contact_at=payload.next_contact_at,
    )
    now = datetime.now(timezone.utc)
    customer.status = result
    customer.last_contact_at = now
    customer.next_contact_at = payload.next_contact_at
    customer.next_action = next_action_for(result, customer.risk)
    customer.priority = priority_score(customer.dpd, customer.balance, customer.risk, result)
    db.add(activity)
    if payload.promise_amount and payload.promise_due_date:
        db.add(
            PaymentPromise(
                tenant_id=customer.tenant_id,
                project_id=customer.project_id,
                customer_id=customer.id,
                user_id=user.id,
                amount=payload.promise_amount,
                due_date=payload.promise_due_date,
                channel=payload.channel,
            )
        )
        customer.status = "Promesa"
        customer.next_action = "Confirmar cumplimiento de promesa"
    record_audit(
        db,
        user,
        "management_activity",
        "create",
        tenant_id=customer.tenant_id,
        module="collections",
        entity_id=customer.id,
        object_id=customer.id,
        after={"customer_id": customer.id, "channel": payload.channel, "result": result, "has_promise": bool(payload.promise_amount and payload.promise_due_date)},
        request=request,
    )
    db.commit()
    db.refresh(activity)
    return activity_to_out(db, activity)
