from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import ManagementActivity, PaymentPromise, TypificationNode, User, UserProjectAssignment
from app.schemas.crm import ActivityCreate, ActivityOut
from app.schemas.self_service import AdvisorManagementInsightsOut, CustomerManagementInsightsOut
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, TENANT_ADMIN
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin, require_permission, user_has_permission
from app.services.audit_service import record_audit
from app.services.collections_self_service import advisor_management_insights, customer_management_insights

from .access import activity_to_out, customer_for_access, ensure_read_access
from .obligations import obligation_for_access
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


def _user_for_insights(db: Session, user_id: int, user: User) -> User:
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    if is_platform_admin(db, user):
        return target
    if target.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario fuera de tu empresa.")
    if is_company_admin(db, user) or target.id == user.id:
        return target
    profile_role = get_profile_role_code(db, user)
    if user.role == COORDINATOR or profile_role in {"collections_leader", "operational_leader"}:
        if target.leader_id == user.id:
            return target
        shared_project = db.scalar(
            select(UserProjectAssignment.id)
            .where(
                UserProjectAssignment.user_id == target.id,
                UserProjectAssignment.is_active.is_(True),
                UserProjectAssignment.project_id.in_(
                    select(UserProjectAssignment.project_id).where(
                        UserProjectAssignment.user_id == user.id,
                        UserProjectAssignment.is_active.is_(True),
                    )
                ),
            )
        )
        if shared_project:
            return target
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes alcance sobre este usuario.")


@router.get("/customers/{customer_id}/activities", response_model=list[ActivityOut])
def list_activities(customer_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ActivityOut]:
    if not user_has_permission(db, user, "crm.activities.view"):
        require_permission(db, user, "crm.clients.view")
    ensure_read_access(user)
    customer_for_access(db, customer_id, user)
    activities = list(db.scalars(select(ManagementActivity).where(ManagementActivity.customer_id == customer_id).order_by(ManagementActivity.created_at.desc()).limit(10)))
    return [activity_to_out(db, item) for item in activities]


@router.get("/customers/{customer_id}/management-insights", response_model=CustomerManagementInsightsOut)
def customer_management_summary(customer_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CustomerManagementInsightsOut:
    if not user_has_permission(db, user, "crm.activities.view"):
        require_permission(db, user, "crm.clients.view")
    ensure_read_access(user)
    customer = customer_for_access(db, customer_id, user)
    return customer_management_insights(db, customer)


@router.get("/users/{user_id}/management-insights", response_model=AdvisorManagementInsightsOut)
def advisor_management_summary(user_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> AdvisorManagementInsightsOut:
    if not user_has_permission(db, user, "crm.activities.view"):
        require_permission(db, user, "crm.clients.view")
    ensure_read_access(user)
    target = _user_for_insights(db, user_id, user)
    return advisor_management_insights(db, target)


@router.post("/customers/{customer_id}/activities", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(customer_id: int, payload: ActivityCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ActivityOut:
    if not _can_create_activity(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para gestionar este cliente.")
    ensure_read_access(user)
    customer = customer_for_access(db, customer_id, user, write=True)
    obligation = obligation_for_access(db, payload.obligation_id, user, write=False) if payload.obligation_id else None
    if obligation and obligation.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La obligacion no pertenece al cliente seleccionado.")
    typification = db.get(TypificationNode, payload.typification_id) if payload.typification_id else None
    if typification and typification.tenant_id != customer.tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tipificacion fuera de la empresa.")
    result = typification.next_status if typification and typification.next_status else payload.result
    activity = ManagementActivity(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        obligation_id=obligation.id if obligation else None,
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
                obligation_id=obligation.id if obligation else None,
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
        after={
            "customer_id": customer.id,
            "obligation_id": obligation.id if obligation else None,
            "channel": payload.channel,
            "result": result,
            "has_promise": bool(payload.promise_amount and payload.promise_due_date),
        },
        request=request,
    )
    db.commit()
    db.refresh(activity)
    return activity_to_out(db, activity)
