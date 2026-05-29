from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.routes.crm.access import customer_for_access, customer_query, project_for_access
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import Customer, LegalAction, LegalCase, LegalDeadline, LegalHearing, User
from app.schemas.legal import LegalActionCreate, LegalActionOut, LegalCaseCreate, LegalCaseOut, LegalCasePatch, LegalDeadlineOut, LegalHearingCreate, LegalHearingOut
from app.services.audit_service import record_audit
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin, require_active_module, require_permission, user_has_permission


router = APIRouter(dependencies=[Depends(require_active_module("legal"))])
LEGAL_MANAGE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}
LEGAL_READ_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, QUALITY_SUPERVISOR, AGENT}


def ensure_legal_read(db: Session, user: User) -> None:
    if user_has_permission(db, user, "legal.cases.view") or user_has_permission(db, user, "legal.deadlines.view"):
        return
    if user.role not in LEGAL_READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso al modulo juridico.")


def ensure_legal_manage(db: Session, user: User) -> None:
    if user_has_permission(db, user, "legal.cases.create") or user_has_permission(db, user, "legal.cases.update"):
        return
    if user.role not in LEGAL_MANAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso para gestionar casos juridicos.")


def legal_case_for_access(db: Session, case_id: int, user: User, write: bool = False) -> LegalCase:
    legal_case = db.get(LegalCase, case_id)
    if legal_case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso juridico no encontrado.")
    if not is_platform_admin(db, user):
        if legal_case.tenant_id != user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Caso juridico fuera de tu empresa.")
        profile_role = get_profile_role_code(db, user)
        if profile_role == "lawyer" and not is_company_admin(db, user) and legal_case.assigned_lawyer_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Caso juridico no asignado.")
        elif profile_role not in {"lawyer", "legal_director"}:
            customer_for_access(db, legal_case.customer_id, user, write=write)
    if write:
        ensure_legal_manage(db, user)
    return legal_case


def validate_lawyer(db: Session, tenant_id: int, assigned_lawyer_id: int | None) -> None:
    if assigned_lawyer_id is None:
        return
    lawyer = db.get(User, assigned_lawyer_id)
    if lawyer is None or lawyer.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El abogado asignado no pertenece a la empresa.")
    if not user_has_permission(db, lawyer, "legal.cases.view"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El abogado asignado no tiene permisos juridicos.")


def customer_for_legal_create(db: Session, customer_id: int, user: User) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado.")
    if is_platform_admin(db, user):
        return customer
    if customer.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cliente fuera de tu empresa.")
    profile_role = get_profile_role_code(db, user)
    if profile_role in {"lawyer", "legal_director"} or is_company_admin(db, user):
        return customer
    return customer_for_access(db, customer_id, user, write=False)


@router.get("/cases", response_model=list[LegalCaseOut])
def list_cases(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[LegalCase]:
    require_permission(db, user, "legal.cases.view")
    ensure_legal_read(db, user)
    profile_role = get_profile_role_code(db, user)
    if is_platform_admin(db, user):
        query = select(LegalCase).order_by(LegalCase.created_at.desc())
    elif is_company_admin(db, user) or profile_role == "legal_director":
        query = select(LegalCase).where(LegalCase.tenant_id == user.tenant_id).order_by(LegalCase.created_at.desc())
    elif profile_role == "lawyer":
        query = select(LegalCase).where(LegalCase.tenant_id == user.tenant_id, LegalCase.assigned_lawyer_id == user.id).order_by(LegalCase.created_at.desc())
    else:
        visible_customers = list(db.scalars(customer_query(db, user)))
        customer_ids = [customer.id for customer in visible_customers]
        query = select(LegalCase).where(LegalCase.customer_id.in_(customer_ids)).order_by(LegalCase.created_at.desc()) if customer_ids else select(LegalCase).where(False)
    return list(db.scalars(query))


@router.post("/cases", response_model=LegalCaseOut, status_code=status.HTTP_201_CREATED)
def create_case(payload: LegalCaseCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LegalCase:
    require_permission(db, user, "legal.cases.create")
    ensure_legal_manage(db, user)
    customer = customer_for_legal_create(db, payload.customer_id, user)
    validate_lawyer(db, customer.tenant_id, payload.assigned_lawyer_id)
    legal_case = LegalCase(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        **payload.model_dump(exclude={"customer_id"}),
    )
    db.add(legal_case)
    db.flush()
    record_audit(db, user, "legal_case", "create", legal_case.id, legal_case.tenant_id, after={"customer_id": legal_case.customer_id, "status": legal_case.status})
    db.commit()
    db.refresh(legal_case)
    return legal_case


@router.get("/cases/{case_id}", response_model=LegalCaseOut)
def get_case(case_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LegalCase:
    require_permission(db, user, "legal.cases.view")
    ensure_legal_read(db, user)
    return legal_case_for_access(db, case_id, user)


@router.patch("/cases/{case_id}", response_model=LegalCaseOut)
def update_case(case_id: int, payload: LegalCasePatch, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LegalCase:
    require_permission(db, user, "legal.cases.update")
    legal_case = legal_case_for_access(db, case_id, user, write=True)
    updates = payload.model_dump(exclude_unset=True)
    if "assigned_lawyer_id" in updates:
        validate_lawyer(db, legal_case.tenant_id, updates["assigned_lawyer_id"])
    for field, value in updates.items():
        setattr(legal_case, field, value)
    record_audit(db, user, "legal_case", "update", legal_case.id, legal_case.tenant_id, after=updates)
    db.commit()
    db.refresh(legal_case)
    return legal_case


@router.post("/cases/{case_id}/actions", response_model=LegalActionOut, status_code=status.HTTP_201_CREATED)
def create_action(case_id: int, payload: LegalActionCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LegalAction:
    require_permission(db, user, "legal.cases.update")
    legal_case = legal_case_for_access(db, case_id, user, write=True)
    action = LegalAction(tenant_id=legal_case.tenant_id, legal_case_id=legal_case.id, user_id=user.id, **payload.model_dump())
    legal_case.next_deadline_at = payload.next_deadline_at or legal_case.next_deadline_at
    if payload.next_deadline_at:
        db.add(LegalDeadline(tenant_id=legal_case.tenant_id, legal_case_id=legal_case.id, title=f"Seguimiento: {payload.action_type}", due_at=payload.next_deadline_at, priority="medium"))
    db.add(action)
    db.flush()
    record_audit(db, user, "legal_action", "create", action.id, legal_case.tenant_id, after={"case_id": legal_case.id, "action_type": action.action_type})
    db.commit()
    db.refresh(action)
    return action


@router.get("/deadlines", response_model=list[LegalDeadlineOut])
def list_deadlines(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[LegalDeadline]:
    require_permission(db, user, "legal.deadlines.view")
    ensure_legal_read(db, user)
    if is_platform_admin(db, user):
        query = select(LegalDeadline).order_by(LegalDeadline.due_at.asc())
    else:
        cases = list_cases(db, user)
        case_ids = [item.id for item in cases]
        query = select(LegalDeadline).where(LegalDeadline.legal_case_id.in_(case_ids)).order_by(LegalDeadline.due_at.asc()) if case_ids else select(LegalDeadline).where(False)
    return list(db.scalars(query))


@router.post("/cases/{case_id}/hearings", response_model=LegalHearingOut, status_code=status.HTTP_201_CREATED)
def create_hearing(case_id: int, payload: LegalHearingCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LegalHearing:
    require_permission(db, user, "legal.cases.update")
    legal_case = legal_case_for_access(db, case_id, user, write=True)
    hearing = LegalHearing(tenant_id=legal_case.tenant_id, legal_case_id=legal_case.id, **payload.model_dump())
    db.add(hearing)
    db.flush()
    record_audit(db, user, "legal_hearing", "create", hearing.id, legal_case.tenant_id, after={"case_id": legal_case.id, "hearing_type": hearing.hearing_type})
    db.commit()
    db.refresh(hearing)
    return hearing
