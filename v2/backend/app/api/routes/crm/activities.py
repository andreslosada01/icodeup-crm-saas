from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import ManagementActivity, PaymentPromise, TypificationNode, User
from app.schemas.crm import ActivityCreate, ActivityOut
from app.services.access_control import require_permission

from .access import activity_to_out, customer_for_access, ensure_read_access
from .utils import next_action_for, priority_score


router = APIRouter()


@router.get("/customers/{customer_id}/activities", response_model=list[ActivityOut])
def list_activities(customer_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ActivityOut]:
    require_permission(db, user, "crm.clients.view")
    ensure_read_access(user)
    customer_for_access(db, customer_id, user)
    activities = list(db.scalars(select(ManagementActivity).where(ManagementActivity.customer_id == customer_id).order_by(ManagementActivity.created_at.desc()).limit(10)))
    return [activity_to_out(db, item) for item in activities]


@router.post("/customers/{customer_id}/activities", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(customer_id: int, payload: ActivityCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ActivityOut:
    require_permission(db, user, "crm.clients.update")
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
    db.commit()
    db.refresh(activity)
    return activity_to_out(db, activity)
