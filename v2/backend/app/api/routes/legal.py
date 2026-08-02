from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.routes.crm.access import customer_for_access, customer_query, project_for_access
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import Customer, Document, LegalAction, LegalCase, LegalDeadline, LegalHearing, User, WorkflowDefinition, WorkflowStage
from app.schemas.legal import LegalActionCreate, LegalActionOut, LegalCaseCreate, LegalCaseOut, LegalCasePatch, LegalDeadlineOut, LegalHearingCreate, LegalHearingOut
from app.services.audit_service import record_audit
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin, require_active_module, require_permission, user_has_permission


router = APIRouter(dependencies=[Depends(require_active_module("legal"))])
LEGAL_MANAGE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}
LEGAL_READ_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, QUALITY_SUPERVISOR, AGENT}
DEFAULT_LEGAL_STAGES = [
    {"code": "RECIBIDO", "name": "Recibido", "color": "#64748b", "order": 10},
    {"code": "ESTUDIO", "name": "En estudio", "color": "#2563eb", "order": 20},
    {"code": "RADICADO", "name": "Radicado", "color": "#7c3aed", "order": 30},
    {"code": "TRAMITE", "name": "En tramite", "color": "#f59e0b", "order": 40},
    {"code": "AUDIENCIA", "name": "Audiencia", "color": "#dc2626", "order": 50},
    {"code": "FALLO", "name": "Fallo", "color": "#16a34a", "order": 60},
    {"code": "CERRADO", "name": "Cerrado", "color": "#0f766e", "order": 70},
]


def _norm(value: str | None) -> str:
    return (value or "").strip().lower().replace("_", " ").replace("-", " ")


def legal_stages(db: Session, tenant_id: int | None) -> list[dict]:
    workflow = None
    if tenant_id:
        workflow = db.scalar(select(WorkflowDefinition).where(WorkflowDefinition.module == "legal", WorkflowDefinition.tenant_id == tenant_id, WorkflowDefinition.is_active.is_(True)).order_by(WorkflowDefinition.id.desc()))
    workflow = workflow or db.scalar(select(WorkflowDefinition).where(WorkflowDefinition.module == "legal", WorkflowDefinition.tenant_id.is_(None), WorkflowDefinition.is_active.is_(True)).order_by(WorkflowDefinition.id.desc()))
    if not workflow:
        return DEFAULT_LEGAL_STAGES
    stages = list(db.scalars(select(WorkflowStage).where(WorkflowStage.workflow_id == workflow.id, WorkflowStage.is_active.is_(True)).order_by(WorkflowStage.order, WorkflowStage.name)))
    return [{"code": stage.code, "name": stage.name, "color": stage.color, "order": stage.order, "is_final": stage.is_final} for stage in stages] or DEFAULT_LEGAL_STAGES


def case_progress_payload(db: Session, legal_case: LegalCase) -> dict:
    stages = legal_stages(db, legal_case.tenant_id)
    stage_text = _norm(legal_case.stage or legal_case.status)
    current_index = 0
    for index, stage in enumerate(stages):
        if _norm(stage["code"]) == stage_text or _norm(stage["name"]) == stage_text:
            current_index = index
            break
    last_action = db.scalar(select(func.max(LegalAction.action_date)).where(LegalAction.legal_case_id == legal_case.id))
    nearest_deadline = db.scalar(
        select(LegalDeadline)
        .where(LegalDeadline.legal_case_id == legal_case.id, LegalDeadline.status.in_(["open", "pending"]))
        .order_by(LegalDeadline.due_at.asc())
    )
    reference_date = last_action or legal_case.created_at
    days_in_stage = max(0, int((datetime.now(timezone.utc) - reference_date).days)) if reference_date else 0
    denominator = max(len(stages) - 1, 1)
    return {
        "case_id": legal_case.id,
        "stage": legal_case.stage or legal_case.status,
        "stage_code": stages[current_index]["code"] if stages else None,
        "stage_name": stages[current_index]["name"] if stages else legal_case.stage,
        "progress_percent": round((current_index / denominator) * 100),
        "next_action": legal_case.next_action,
        "last_movement_at": last_action,
        "responsible_user_id": legal_case.assigned_lawyer_id,
        "risk": legal_case.risk,
        "days_in_stage": days_in_stage,
        "nearest_deadline": {"id": nearest_deadline.id, "title": nearest_deadline.title, "due_at": nearest_deadline.due_at, "priority": nearest_deadline.priority} if nearest_deadline else None,
        "stages": stages,
    }


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


@router.get("/dashboard")
def legal_dashboard(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "legal.cases.view")
    ensure_legal_read(db, user)
    cases = list_cases(tenant_id=tenant_id, db=db, user=user, limit=10)
    case_ids = [item.id for item in cases]
    deadlines = list(db.scalars(select(LegalDeadline).where(LegalDeadline.legal_case_id.in_(case_ids)).order_by(LegalDeadline.due_at.asc()).limit(10))) if case_ids else []
    hearings = list(db.scalars(select(LegalHearing).where(LegalHearing.legal_case_id.in_(case_ids)).order_by(LegalHearing.scheduled_at.asc()).limit(10))) if case_ids else []
    now = datetime.now(timezone.utc)
    by_stage: dict[str, int] = {}
    by_risk: dict[str, int] = {}
    by_lawyer: dict[str, int] = {}
    for item in cases:
        by_stage[item.stage or item.status] = by_stage.get(item.stage or item.status, 0) + 1
        by_risk[item.risk] = by_risk.get(item.risk, 0) + 1
        lawyer_key = str(item.assigned_lawyer_id or "Sin asignar")
        by_lawyer[lawyer_key] = by_lawyer.get(lawyer_key, 0) + 1
    return {
        "kpis": {
            "active_cases": sum(1 for item in cases if item.status != "closed"),
            "closed_cases": sum(1 for item in cases if item.status == "closed"),
            "upcoming_deadlines": sum(1 for item in deadlines if item.due_at >= now),
            "overdue_deadlines": sum(1 for item in deadlines if item.due_at < now),
            "upcoming_hearings": sum(1 for item in hearings if item.scheduled_at >= now),
            "high_risk_cases": sum(1 for item in cases if (item.risk or "").lower() in {"alto", "high", "critical"}),
        },
        "by_stage": [{"stage": key, "count": value} for key, value in sorted(by_stage.items())],
        "by_risk": [{"risk": key, "count": value} for key, value in sorted(by_risk.items())],
        "by_lawyer": [{"lawyer_id": key, "count": value} for key, value in sorted(by_lawyer.items())],
        "upcoming_deadlines": [
            {"id": item.id, "case_id": item.legal_case_id, "title": item.title, "due_at": item.due_at, "priority": item.priority, "status": item.status}
            for item in deadlines[:8]
        ],
        "upcoming_hearings": [
            {"id": item.id, "case_id": item.legal_case_id, "hearing_type": item.hearing_type, "scheduled_at": item.scheduled_at, "status": item.status, "location": item.location}
            for item in hearings[:8]
        ],
    }


@router.get("/kanban")
def legal_kanban(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "legal.cases.view")
    ensure_legal_read(db, user)
    cases = list_cases(tenant_id=tenant_id, db=db, user=user, limit=10)
    stages = legal_stages(db, tenant_id if is_platform_admin(db, user) and tenant_id else user.tenant_id if not is_platform_admin(db, user) else None)
    columns = []
    for stage in stages:
        stage_key = _norm(stage["name"])
        stage_code = _norm(stage["code"])
        items = [
            {
                "id": item.id,
                "case_number": item.case_number,
                "customer_id": item.customer_id,
                "amount": item.amount,
                "risk": item.risk,
                "next_deadline_at": item.next_deadline_at,
                "assigned_lawyer_id": item.assigned_lawyer_id,
            }
            for item in cases
            if _norm(item.stage or item.status) in {stage_key, stage_code}
        ]
        columns.append({"stage": stage, "count": len(items), "amount": sum(item["amount"] for item in items), "items": items[:20]})
    uncategorized = [
        item for item in cases
        if not any(_norm(item.stage or item.status) in {_norm(stage["name"]), _norm(stage["code"])} for stage in stages)
    ]
    if uncategorized:
        columns.append(
            {
                "stage": {"code": "OTROS", "name": "Otros", "color": "#94a3b8", "order": 999},
                "count": len(uncategorized),
                "amount": sum(item.amount for item in uncategorized),
                "items": [
                    {"id": item.id, "case_number": item.case_number, "customer_id": item.customer_id, "amount": item.amount, "risk": item.risk, "next_deadline_at": item.next_deadline_at}
                    for item in uncategorized[:20]
                ],
            }
        )
    return {"columns": columns}


@router.get("/cases", response_model=list[LegalCaseOut])
def list_cases(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user), limit: int = Query(default=10, ge=1, le=10)) -> list[LegalCase]:
    require_permission(db, user, "legal.cases.view")
    ensure_legal_read(db, user)
    profile_role = get_profile_role_code(db, user)
    if is_platform_admin(db, user):
        query = select(LegalCase).order_by(LegalCase.created_at.desc())
        if tenant_id:
            query = query.where(LegalCase.tenant_id == tenant_id)
    elif is_company_admin(db, user) or profile_role == "legal_director":
        query = select(LegalCase).where(LegalCase.tenant_id == user.tenant_id).order_by(LegalCase.created_at.desc())
    elif profile_role == "lawyer":
        query = select(LegalCase).where(LegalCase.tenant_id == user.tenant_id, LegalCase.assigned_lawyer_id == user.id).order_by(LegalCase.created_at.desc())
    else:
        visible_customers = list(db.scalars(customer_query(db, user)))
        customer_ids = [customer.id for customer in visible_customers]
        query = select(LegalCase).where(LegalCase.customer_id.in_(customer_ids)).order_by(LegalCase.created_at.desc()) if customer_ids else select(LegalCase).where(False)
    return list(db.scalars(query.limit(limit)))


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


@router.get("/cases/{case_id}/progress")
def get_case_progress(case_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "legal.cases.view")
    ensure_legal_read(db, user)
    legal_case = legal_case_for_access(db, case_id, user)
    return case_progress_payload(db, legal_case)


@router.get("/cases/{case_id}/timeline")
def get_case_timeline(case_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "legal.cases.view")
    ensure_legal_read(db, user)
    legal_case = legal_case_for_access(db, case_id, user)
    events = [
        {"type": "case", "title": "Caso creado", "description": legal_case.notes, "date": legal_case.created_at, "severity": legal_case.risk}
    ]
    for action in db.scalars(select(LegalAction).where(LegalAction.legal_case_id == legal_case.id).order_by(LegalAction.action_date.asc())):
        events.append({"type": "action", "title": action.action_type, "description": action.description, "date": action.action_date, "severity": "medium"})
    for hearing in db.scalars(select(LegalHearing).where(LegalHearing.legal_case_id == legal_case.id).order_by(LegalHearing.scheduled_at.asc())):
        events.append({"type": "hearing", "title": hearing.hearing_type, "description": hearing.location or hearing.notes, "date": hearing.scheduled_at, "severity": "high"})
    for deadline in db.scalars(select(LegalDeadline).where(LegalDeadline.legal_case_id == legal_case.id).order_by(LegalDeadline.due_at.asc())):
        events.append({"type": "deadline", "title": deadline.title, "description": deadline.status, "date": deadline.due_at, "severity": deadline.priority})
    for document in db.scalars(select(Document).where(Document.legal_case_id == legal_case.id).order_by(Document.created_at.asc())):
        events.append({"type": "document", "title": document.document_type, "description": document.original_name, "date": document.created_at, "severity": "low"})
    events.sort(key=lambda item: item["date"] or datetime.now(timezone.utc))
    return {"case": {"id": legal_case.id, "case_number": legal_case.case_number, "stage": legal_case.stage, "risk": legal_case.risk}, "events": events}


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
def list_deadlines(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user), limit: int = Query(default=10, ge=1, le=10)) -> list[LegalDeadline]:
    require_permission(db, user, "legal.deadlines.view")
    ensure_legal_read(db, user)
    if is_platform_admin(db, user):
        query = select(LegalDeadline).order_by(LegalDeadline.due_at.asc())
        if tenant_id:
            query = query.where(LegalDeadline.tenant_id == tenant_id)
    else:
        cases = list_cases(db=db, user=user, limit=10)
        case_ids = [item.id for item in cases]
        query = select(LegalDeadline).where(LegalDeadline.legal_case_id.in_(case_ids)).order_by(LegalDeadline.due_at.asc()) if case_ids else select(LegalDeadline).where(False)
    return list(db.scalars(query.limit(limit)))


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
