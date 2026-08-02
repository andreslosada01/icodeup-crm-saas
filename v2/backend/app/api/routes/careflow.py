from __future__ import annotations

import json
from datetime import datetime, time, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.roles import AGENT, COORDINATOR, QUALITY_SUPERVISOR
from app.db.session import get_db
from app.models import CareCase, CareCaseCategory, CareCaseEvent, Customer, Project, Tenant, User, UserProjectAssignment
from app.schemas.careflow import (
    CareCaseAssign,
    CareCaseCategoryCreate,
    CareCaseCategoryOut,
    CareCaseClose,
    CareCaseCreate,
    CareCaseEventCreate,
    CareCaseEventOut,
    CareCaseListResponse,
    CareCaseOut,
    CareCasePatch,
    CareFlowSummaryOut,
)
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin, require_module, require_permission, require_tenant, user_has_permission
from app.services.audit_service import record_audit


router = APIRouter()

CAREFLOW_MODULE = "careflow"
CASE_PAGE_SIZE = 10
OPEN_STATUSES = {"nuevo", "asignado", "en_proceso", "pendiente_cliente", "pendiente_interno"}
CLOSED_STATUSES = {"resuelto", "cerrado", "cancelado"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _json(value: str | None, fallback: Any | None = None) -> Any:
    if not value:
        return {} if fallback is None else fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {} if fallback is None else fallback


def _set_json(item: Any, field: str, value: dict[str, Any] | None) -> None:
    setattr(item, field, json.dumps(value or {}, ensure_ascii=True))


def _tenant_id_for_payload(db: Session, user: User, tenant_id: int | None = None) -> int:
    require_module(db, user, CAREFLOW_MODULE, tenant_id)
    return require_tenant(db, user, tenant_id).id


def _careflow_role(db: Session, user: User) -> str:
    profile = get_profile_role_code(db, user)
    if is_platform_admin(db, user):
        return "platform_admin"
    if is_company_admin(db, user):
        return "tenant_admin"
    if user.role == COORDINATOR or profile in {"collections_leader", "operational_leader"}:
        return "coordinator"
    if user.role == QUALITY_SUPERVISOR or profile == "tenant_auditor":
        return "quality_supervisor"
    if user.role == AGENT:
        return "agent"
    return "operational"


def _team_user_ids(db: Session, user: User) -> list[int]:
    ids = [user.id]
    ids.extend(db.scalars(select(User.id).where(User.tenant_id == user.tenant_id, User.leader_id == user.id, User.status == "active")))
    return list(dict.fromkeys(ids))


def _active_project_ids(db: Session, user: User) -> list[int]:
    return list(
        db.scalars(
            select(UserProjectAssignment.project_id).where(
                UserProjectAssignment.tenant_id == user.tenant_id,
                UserProjectAssignment.user_id == user.id,
                UserProjectAssignment.is_active.is_(True),
            )
        )
    )


def _validate_project(db: Session, tenant_id: int, project_id: int | None) -> Project | None:
    if project_id is None:
        return None
    project = db.get(Project, project_id)
    if project is None or project.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La cartera no pertenece a la empresa del caso.")
    return project


def _validate_customer(db: Session, tenant_id: int, customer_id: int | None, project_id: int | None = None) -> Customer | None:
    if customer_id is None:
        return None
    customer = db.get(Customer, customer_id)
    if customer is None or customer.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El cliente no pertenece a la empresa del caso.")
    if project_id and customer.project_id and customer.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El cliente no pertenece a la cartera seleccionada.")
    return customer


def _validate_assignee(db: Session, tenant_id: int, user_id: int | None) -> User | None:
    if user_id is None:
        return None
    target = db.get(User, user_id)
    if target is None or target.tenant_id != tenant_id or target.status != "active":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El responsable no pertenece a la empresa o esta inactivo.")
    return target


def _sla_status(item: CareCase) -> str:
    if item.status in CLOSED_STATUSES:
        return "en_tiempo"
    if not item.due_at:
        return "en_tiempo"
    now = _now()
    if item.due_at < now:
        return "vencido"
    if item.due_at <= now + timedelta(hours=24):
        return "proximo_a_vencer"
    return "en_tiempo"


def _sync_sla(item: CareCase) -> None:
    item.sla_status = _sla_status(item)


def _next_case_number(db: Session, tenant_id: int) -> str:
    year = _now().year
    total = (db.scalar(select(func.count(CareCase.id)).where(CareCase.tenant_id == tenant_id)) or 0) + 1
    while True:
        candidate = f"CF-{year}-{total:05d}"
        exists = db.scalar(select(CareCase.id).where(CareCase.tenant_id == tenant_id, CareCase.case_number == candidate))
        if exists is None:
            return candidate
        total += 1


def _visible_case_query(db: Session, user: User, tenant_id: int | None = None):
    query = select(CareCase)
    role = _careflow_role(db, user)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(CareCase.tenant_id == tenant_id)
        return query
    query = query.where(CareCase.tenant_id == user.tenant_id)
    if role in {"tenant_admin", "quality_supervisor"}:
        return query
    if role == "coordinator":
        team_ids = _team_user_ids(db, user)
        project_ids = _active_project_ids(db, user)
        conditions = [CareCase.assigned_user_id.in_(team_ids), CareCase.created_by_id == user.id, CareCase.assigned_user_id.is_(None)]
        if project_ids:
            conditions.append(CareCase.project_id.in_(project_ids))
        return query.where(or_(*conditions))
    return query.where(or_(CareCase.assigned_user_id == user.id, CareCase.created_by_id == user.id))


def _case_for_access(db: Session, case_id: int, user: User, write: bool = False) -> CareCase:
    item = db.get(CareCase, case_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso CareFlow no encontrado.")
    require_module(db, user, CAREFLOW_MODULE, item.tenant_id)
    visible_id = db.scalar(_visible_case_query(db, user, item.tenant_id).where(CareCase.id == case_id).with_only_columns(CareCase.id))
    if visible_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Caso fuera de tu alcance operativo.")
    if write and _careflow_role(db, user) == "quality_supervisor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Calidad tiene acceso de lectura/evaluacion, no administracion del caso.")
    return item


def _event_to_out(db: Session, item: CareCaseEvent) -> CareCaseEventOut:
    creator = db.get(User, item.created_by_id)
    return CareCaseEventOut(
        id=item.id,
        tenant_id=item.tenant_id,
        case_id=item.case_id,
        event_type=item.event_type,
        description=item.description,
        previous_value=item.previous_value,
        new_value=item.new_value,
        created_by_id=item.created_by_id,
        created_by_name=creator.name if creator else None,
        created_at=item.created_at,
        metadata=_json(item.metadata_json),
    )


def _case_to_out(db: Session, item: CareCase, include_events: bool = False) -> CareCaseOut:
    _sync_sla(item)
    tenant = db.get(Tenant, item.tenant_id)
    project = db.get(Project, item.project_id) if item.project_id else None
    customer = db.get(Customer, item.customer_id) if item.customer_id else None
    assigned = db.get(User, item.assigned_user_id) if item.assigned_user_id else None
    creator = db.get(User, item.created_by_id)
    closer = db.get(User, item.closed_by_id) if item.closed_by_id else None
    events = []
    if include_events:
        rows = db.scalars(select(CareCaseEvent).where(CareCaseEvent.case_id == item.id).order_by(CareCaseEvent.created_at.desc(), CareCaseEvent.id.desc()).limit(CASE_PAGE_SIZE))
        events = [_event_to_out(db, row) for row in rows]
    return CareCaseOut(
        id=item.id,
        tenant_id=item.tenant_id,
        tenant_name=tenant.name if tenant else None,
        project_id=item.project_id,
        project_name=project.name if project else None,
        customer_id=item.customer_id,
        customer_name=customer.name if customer else None,
        case_number=item.case_number,
        title=item.title,
        description=item.description,
        channel=item.channel,
        case_type=item.case_type,
        category=item.category,
        priority=item.priority,
        status=item.status,
        origin=item.origin,
        assigned_user_id=item.assigned_user_id,
        assigned_user_name=assigned.name if assigned else None,
        created_by_id=item.created_by_id,
        created_by_name=creator.name if creator else None,
        closed_by_id=item.closed_by_id,
        closed_by_name=closer.name if closer else None,
        due_at=item.due_at,
        resolved_at=item.resolved_at,
        closed_at=item.closed_at,
        sla_status=item.sla_status,
        metadata=_json(item.metadata_json),
        created_at=item.created_at,
        updated_at=item.updated_at,
        events=events,
    )


def _add_event(
    db: Session,
    item: CareCase,
    user: User,
    event_type: str,
    description: str,
    previous_value: str | None = None,
    new_value: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> CareCaseEvent:
    event = CareCaseEvent(
        tenant_id=item.tenant_id,
        case_id=item.id,
        event_type=event_type,
        description=description,
        previous_value=previous_value,
        new_value=new_value,
        created_by_id=user.id,
        metadata_json=json.dumps(metadata or {}, ensure_ascii=True),
    )
    db.add(event)
    return event


@router.get("/categories", response_model=list[CareCaseCategoryOut])
def list_categories(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[CareCaseCategory]:
    target_tenant_id = _tenant_id_for_payload(db, user, tenant_id)
    require_permission(db, user, "careflow.view")
    return list(db.scalars(select(CareCaseCategory).where(CareCaseCategory.tenant_id == target_tenant_id, CareCaseCategory.is_active.is_(True)).order_by(CareCaseCategory.name)))


@router.post("/categories", response_model=CareCaseCategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CareCaseCategoryCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CareCaseCategory:
    require_permission(db, user, "careflow.configure")
    tenant_id = _tenant_id_for_payload(db, user, payload.tenant_id)
    item = db.scalar(select(CareCaseCategory).where(CareCaseCategory.tenant_id == tenant_id, CareCaseCategory.name == payload.name.strip()))
    if item is None:
        item = CareCaseCategory(tenant_id=tenant_id, name=payload.name.strip())
        db.add(item)
    item.description = payload.description
    item.default_priority = payload.default_priority
    item.default_sla_hours = payload.default_sla_hours
    item.is_active = payload.is_active
    db.flush()
    record_audit(db, user, "care_case_category", "upsert", item.id, tenant_id, module=CAREFLOW_MODULE, after=payload.model_dump(), request=request)
    db.commit()
    db.refresh(item)
    return item


@router.get("/cases", response_model=CareCaseListResponse)
def list_cases(
    tenant_id: int | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    priority: str | None = None,
    channel: str | None = None,
    assigned_user_id: int | None = None,
    project_id: int | None = None,
    customer_id: int | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=CASE_PAGE_SIZE, ge=1, le=CASE_PAGE_SIZE),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> CareCaseListResponse:
    require_module(db, user, CAREFLOW_MODULE, tenant_id)
    require_permission(db, user, "careflow.view")
    query = _visible_case_query(db, user, tenant_id)
    if status_filter:
        query = query.where(CareCase.status == status_filter)
    if priority:
        query = query.where(CareCase.priority == priority)
    if channel:
        query = query.where(CareCase.channel == channel)
    if assigned_user_id:
        query = query.where(CareCase.assigned_user_id == assigned_user_id)
    if project_id:
        query = query.where(CareCase.project_id == project_id)
    if customer_id:
        query = query.where(CareCase.customer_id == customer_id)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(or_(CareCase.title.ilike(like), CareCase.case_number.ilike(like), CareCase.description.ilike(like)))
    total = db.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
    items = list(db.scalars(query.order_by(CareCase.updated_at.desc(), CareCase.id.desc()).offset((page - 1) * page_size).limit(page_size)))
    return CareCaseListResponse(items=[_case_to_out(db, item) for item in items], total=total, page=page, page_size=page_size, total_pages=max(1, (total + page_size - 1) // page_size))


@router.get("/cases/{case_id}", response_model=CareCaseOut)
def get_case(case_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CareCaseOut:
    require_permission(db, user, "careflow.view")
    item = _case_for_access(db, case_id, user)
    return _case_to_out(db, item, include_events=True)


@router.post("/cases", response_model=CareCaseOut, status_code=status.HTTP_201_CREATED)
def create_case(payload: CareCaseCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CareCaseOut:
    require_permission(db, user, "careflow.create")
    tenant_id = _tenant_id_for_payload(db, user, payload.tenant_id)
    role = _careflow_role(db, user)
    project = _validate_project(db, tenant_id, payload.project_id)
    customer = _validate_customer(db, tenant_id, payload.customer_id, project.id if project else payload.project_id)
    assigned_user_id = payload.assigned_user_id
    if role == "agent":
        assigned_user_id = user.id
    assignee = _validate_assignee(db, tenant_id, assigned_user_id)
    item = CareCase(
        tenant_id=tenant_id,
        project_id=project.id if project else None,
        customer_id=customer.id if customer else None,
        case_number=_next_case_number(db, tenant_id),
        title=payload.title.strip(),
        description=payload.description,
        channel=payload.channel,
        case_type=payload.case_type,
        category=payload.category,
        priority=payload.priority,
        status="asignado" if assignee else "nuevo",
        origin=payload.origin,
        assigned_user_id=assignee.id if assignee else None,
        created_by_id=user.id,
        due_at=payload.due_at,
    )
    _set_json(item, "metadata_json", payload.metadata)
    _sync_sla(item)
    db.add(item)
    db.flush()
    _add_event(db, item, user, "comentario", "Caso creado desde CareFlow 360.", new_value=item.status, metadata={"source": "careflow_mvp"})
    record_audit(db, user, "care_case", "create", item.id, tenant_id, module=CAREFLOW_MODULE, after=payload.model_dump(), request=request)
    db.commit()
    db.refresh(item)
    return _case_to_out(db, item, include_events=True)


@router.patch("/cases/{case_id}", response_model=CareCaseOut)
def update_case(case_id: int, payload: CareCasePatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CareCaseOut:
    require_permission(db, user, "careflow.update")
    item = _case_for_access(db, case_id, user, write=True)
    updates = payload.model_dump(exclude_unset=True)
    previous_status = item.status
    project_id = updates.get("project_id", item.project_id)
    _validate_project(db, item.tenant_id, project_id)
    _validate_customer(db, item.tenant_id, updates.get("customer_id", item.customer_id), project_id)
    if "metadata" in updates:
        _set_json(item, "metadata_json", updates.pop("metadata"))
    for field, value in updates.items():
        setattr(item, field, value.strip() if isinstance(value, str) else value)
    if item.status in {"resuelto"} and item.resolved_at is None:
        item.resolved_at = _now()
    if item.status in CLOSED_STATUSES and item.closed_at is None:
        item.closed_at = _now()
        item.closed_by_id = user.id
    if item.status != previous_status:
        _add_event(db, item, user, "cambio_estado", f"Estado actualizado de {previous_status} a {item.status}.", previous_status, item.status)
    _sync_sla(item)
    record_audit(db, user, "care_case", "update", item.id, item.tenant_id, module=CAREFLOW_MODULE, after=payload.model_dump(exclude_unset=True), request=request)
    db.commit()
    db.refresh(item)
    return _case_to_out(db, item, include_events=True)


@router.post("/cases/{case_id}/events", response_model=CareCaseEventOut, status_code=status.HTTP_201_CREATED)
def add_case_event(case_id: int, payload: CareCaseEventCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CareCaseEventOut:
    require_permission(db, user, "careflow.events.create")
    item = _case_for_access(db, case_id, user)
    event = _add_event(db, item, user, payload.event_type, payload.description, payload.previous_value, payload.new_value, payload.metadata)
    record_audit(db, user, "care_case_event", "create", item.id, item.tenant_id, module=CAREFLOW_MODULE, after=payload.model_dump(), request=request)
    db.commit()
    db.refresh(event)
    return _event_to_out(db, event)


@router.post("/cases/{case_id}/assign", response_model=CareCaseOut)
def assign_case(case_id: int, payload: CareCaseAssign, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CareCaseOut:
    require_permission(db, user, "careflow.assign")
    item = _case_for_access(db, case_id, user, write=True)
    assignee = _validate_assignee(db, item.tenant_id, payload.assigned_user_id)
    previous = item.assigned_user_id
    item.assigned_user_id = assignee.id if assignee else None
    if item.status == "nuevo":
        item.status = "asignado"
    _sync_sla(item)
    _add_event(db, item, user, "asignacion", payload.note or "Responsable asignado.", str(previous) if previous else None, str(item.assigned_user_id))
    record_audit(db, user, "care_case", "assign", item.id, item.tenant_id, module=CAREFLOW_MODULE, after=payload.model_dump(), request=request)
    db.commit()
    db.refresh(item)
    return _case_to_out(db, item, include_events=True)


@router.post("/cases/{case_id}/close", response_model=CareCaseOut)
def close_case(case_id: int, payload: CareCaseClose, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CareCaseOut:
    require_permission(db, user, "careflow.close")
    item = _case_for_access(db, case_id, user, write=True)
    previous = item.status
    item.status = payload.status
    item.closed_by_id = user.id
    item.closed_at = _now()
    if payload.status == "resuelto" and item.resolved_at is None:
        item.resolved_at = item.closed_at
    _sync_sla(item)
    _add_event(db, item, user, "cierre", payload.resolution or "Caso cerrado desde CareFlow 360.", previous, item.status)
    record_audit(db, user, "care_case", "close", item.id, item.tenant_id, module=CAREFLOW_MODULE, after=payload.model_dump(), request=request)
    db.commit()
    db.refresh(item)
    return _case_to_out(db, item, include_events=True)


@router.get("/summary", response_model=CareFlowSummaryOut)
def careflow_summary(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CareFlowSummaryOut:
    require_module(db, user, CAREFLOW_MODULE, tenant_id)
    require_permission(db, user, "careflow.view")
    month_start = datetime.combine(_now().date().replace(day=1), time.min, tzinfo=timezone.utc)
    visible = _visible_case_query(db, user, tenant_id).subquery()
    by_status = {
        status_key: count
        for status_key, count in db.execute(select(visible.c.status, func.count()).group_by(visible.c.status)).all()
    }
    by_priority = {
        priority_key: count
        for priority_key, count in db.execute(select(visible.c.priority, func.count()).group_by(visible.c.priority)).all()
    }
    return CareFlowSummaryOut(
        new_cases=by_status.get("nuevo", 0),
        assigned_to_me=db.scalar(select(func.count()).select_from(visible).where(visible.c.assigned_user_id == user.id, visible.c.status.in_(OPEN_STATUSES))) or 0,
        overdue_cases=db.scalar(select(func.count()).select_from(visible).where(visible.c.sla_status == "vencido", visible.c.status.in_(OPEN_STATUSES))) or 0,
        due_soon_cases=db.scalar(select(func.count()).select_from(visible).where(visible.c.sla_status == "proximo_a_vencer", visible.c.status.in_(OPEN_STATUSES))) or 0,
        closed_this_month=db.scalar(select(func.count()).select_from(visible).where(visible.c.closed_at >= month_start)) or 0,
        unassigned_cases=db.scalar(select(func.count()).select_from(visible).where(visible.c.assigned_user_id.is_(None), visible.c.status.in_(OPEN_STATUSES))) or 0,
        critical_open_cases=db.scalar(select(func.count()).select_from(visible).where(visible.c.priority == "critica", visible.c.status.in_(OPEN_STATUSES))) or 0,
        by_status=by_status,
        by_priority=by_priority,
    )
