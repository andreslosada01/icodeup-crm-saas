from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.routes.crm.access import customer_for_access, customer_query, project_for_access
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import LegalAction, LegalCase, LegalDeadline, LegalHearing, User
from app.schemas.legal import LegalActionCreate, LegalActionOut, LegalCaseCreate, LegalCaseOut, LegalCasePatch, LegalDeadlineOut, LegalHearingCreate, LegalHearingOut
from app.services.audit_service import record_audit


router = APIRouter()
LEGAL_MANAGE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}
LEGAL_READ_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, QUALITY_SUPERVISOR, AGENT}


def ensure_legal_read(user: User) -> None:
    if user.role not in LEGAL_READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso al modulo juridico.")


def ensure_legal_manage(user: User) -> None:
    if user.role not in LEGAL_MANAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso para gestionar casos juridicos.")


def legal_case_for_access(db: Session, case_id: int, user: User, write: bool = False) -> LegalCase:
    legal_case = db.get(LegalCase, case_id)
    if legal_case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso juridico no encontrado.")
    customer_for_access(db, legal_case.customer_id, user, write=write)
    if write:
        ensure_legal_manage(user)
    return legal_case


def validate_lawyer(db: Session, tenant_id: int, assigned_lawyer_id: int | None) -> None:
    if assigned_lawyer_id is None:
        return
    lawyer = db.get(User, assigned_lawyer_id)
    if lawyer is None or lawyer.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El abogado asignado no pertenece a la empresa.")


@router.get("/cases", response_model=list[LegalCaseOut])
def list_cases(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[LegalCase]:
    ensure_legal_read(user)
    if user.role == PLATFORM_ADMIN:
        query = select(LegalCase).order_by(LegalCase.created_at.desc())
    else:
        visible_customers = list(db.scalars(customer_query(db, user)))
        customer_ids = [customer.id for customer in visible_customers]
        query = select(LegalCase).where(LegalCase.customer_id.in_(customer_ids)).order_by(LegalCase.created_at.desc()) if customer_ids else select(LegalCase).where(False)
    return list(db.scalars(query))


@router.post("/cases", response_model=LegalCaseOut, status_code=status.HTTP_201_CREATED)
def create_case(payload: LegalCaseCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LegalCase:
    ensure_legal_manage(user)
    customer = customer_for_access(db, payload.customer_id, user, write=False)
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
    ensure_legal_read(user)
    return legal_case_for_access(db, case_id, user)


@router.patch("/cases/{case_id}", response_model=LegalCaseOut)
def update_case(case_id: int, payload: LegalCasePatch, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LegalCase:
    legal_case = legal_case_for_access(db, case_id, user, write=True)
    updates = payload.model_dump(exclude_unset=True)
    if "assigned_lawyer_id" in updates:
        validate_lawyer(db, legal_case.tenant_id, updates["assigned_lawyer_id"])
    for field, value in updates.items():
        setattr(legal_case, field, value)
    db.commit()
    db.refresh(legal_case)
    return legal_case


@router.post("/cases/{case_id}/actions", response_model=LegalActionOut, status_code=status.HTTP_201_CREATED)
def create_action(case_id: int, payload: LegalActionCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LegalAction:
    legal_case = legal_case_for_access(db, case_id, user, write=True)
    action = LegalAction(tenant_id=legal_case.tenant_id, legal_case_id=legal_case.id, user_id=user.id, **payload.model_dump())
    legal_case.next_deadline_at = payload.next_deadline_at or legal_case.next_deadline_at
    if payload.next_deadline_at:
        db.add(LegalDeadline(tenant_id=legal_case.tenant_id, legal_case_id=legal_case.id, title=f"Seguimiento: {payload.action_type}", due_at=payload.next_deadline_at, priority="medium"))
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@router.get("/deadlines", response_model=list[LegalDeadlineOut])
def list_deadlines(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[LegalDeadline]:
    ensure_legal_read(user)
    if user.role == PLATFORM_ADMIN:
        query = select(LegalDeadline).order_by(LegalDeadline.due_at.asc())
    else:
        cases = list_cases(db, user)
        case_ids = [item.id for item in cases]
        query = select(LegalDeadline).where(LegalDeadline.legal_case_id.in_(case_ids)).order_by(LegalDeadline.due_at.asc()) if case_ids else select(LegalDeadline).where(False)
    return list(db.scalars(query))


@router.post("/cases/{case_id}/hearings", response_model=LegalHearingOut, status_code=status.HTTP_201_CREATED)
def create_hearing(case_id: int, payload: LegalHearingCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> LegalHearing:
    legal_case = legal_case_for_access(db, case_id, user, write=True)
    hearing = LegalHearing(tenant_id=legal_case.tenant_id, legal_case_id=legal_case.id, **payload.model_dump())
    db.add(hearing)
    db.commit()
    db.refresh(hearing)
    return hearing
