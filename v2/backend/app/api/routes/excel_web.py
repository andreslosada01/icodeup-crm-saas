from __future__ import annotations

import json
from math import ceil
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import (
    CallRecording,
    Customer,
    CustomerDemographic,
    CustomerObligation,
    DataExportLog,
    Document,
    GeneratedAlert,
    ImportBatch,
    Lead,
    LegalCase,
    ManagementActivity,
    Opportunity,
    Payment,
    PaymentAgreement,
    PaymentPromise,
    SavedDataView,
    UploadBatch,
    User,
    UserProjectAssignment,
)
from app.schemas.collection_ops import ExcelWebQuery, ExcelWebQueryResult, SavedDataViewCreate, SavedDataViewOut
from app.core.roles import AGENT, COORDINATOR
from app.services.access_control import get_profile_role_code, is_platform_admin, require_permission
from app.services.audit_service import record_audit


router = APIRouter()


SOURCE_DEFS = {
    "customers": {"label": "Clientes", "columns": ["id", "name", "document", "phone", "email", "city", "segment", "balance", "dpd", "status", "risk", "assigned_user_id"]},
    "obligations": {"label": "Obligaciones", "columns": ["id", "customer_id", "obligation_number", "product_type", "portfolio_name", "original_amount", "current_balance", "days_past_due", "status", "risk", "assigned_user_id", "assigned_leader_id"]},
    "activities": {"label": "Gestiones", "columns": ["id", "customer_id", "user_id", "channel", "result", "note", "created_at"]},
    "promises": {"label": "Promesas", "columns": ["id", "customer_id", "user_id", "amount", "due_date", "status", "channel"]},
    "payments": {"label": "Pagos", "columns": ["id", "customer_id", "user_id", "amount", "paid_at", "method", "reference"]},
    "agreements": {"label": "Acuerdos", "columns": ["id", "customer_id", "user_id", "total_amount", "installment_count", "status", "created_at"]},
    "demographics": {"label": "Demograficos", "columns": ["id", "customer_id", "source", "phone", "email", "city", "state", "employer", "score"]},
    "recordings": {"label": "Grabaciones", "columns": ["id", "customer_id", "user_id", "call_id", "phone_number", "direction", "duration_seconds", "status", "provider_code"]},
    "legal_cases": {"label": "Juridico", "columns": ["id", "customer_id", "assigned_lawyer_id", "case_number", "process_type", "status", "stage", "risk", "next_deadline_at"]},
    "sales_leads": {"label": "Leads", "columns": ["id", "assigned_user_id", "name", "company", "phone", "email", "source", "status", "priority"]},
    "opportunities": {"label": "Oportunidades", "columns": ["id", "lead_id", "customer_id", "assigned_user_id", "name", "amount", "stage", "probability", "status"]},
    "documents": {"label": "Documentos", "columns": ["id", "project_id", "customer_id", "legal_case_id", "document_type", "original_name", "status", "created_at"]},
    "uploads": {"label": "Cargas", "columns": ["id", "project_id", "upload_type", "original_filename", "status", "total_rows", "valid_rows", "error_rows", "created_at"]},
    "alerts": {"label": "Alertas", "columns": ["id", "module", "entity_type", "entity_id", "title", "severity", "status", "due_at", "assigned_user_id"]},
}

SOURCE_MODELS = {
    "customers": Customer,
    "obligations": CustomerObligation,
    "activities": ManagementActivity,
    "promises": PaymentPromise,
    "payments": Payment,
    "agreements": PaymentAgreement,
    "demographics": CustomerDemographic,
    "recordings": CallRecording,
    "legal_cases": LegalCase,
    "sales_leads": Lead,
    "opportunities": Opportunity,
    "documents": Document,
    "uploads": UploadBatch,
    "alerts": GeneratedAlert,
}


AGENT_SOURCES = {"customers", "obligations", "activities", "promises", "payments", "agreements", "alerts", "documents"}
LEADER_SOURCES = AGENT_SOURCES | {"demographics"}
SALES_SOURCES = {"customers", "sales_leads", "opportunities", "alerts"}
LEGAL_SOURCES = {"customers", "legal_cases", "documents", "alerts"}


def _profile_code(db: Session, user: User) -> str | None:
    return get_profile_role_code(db, user)


def _team_user_ids(db: Session, user: User) -> list[int]:
    ids = [user.id]
    ids.extend(db.scalars(select(User.id).where(User.tenant_id == user.tenant_id, User.leader_id == user.id)))
    return list(dict.fromkeys(ids))


def _project_ids(db: Session, user: User) -> list[int]:
    return list(db.scalars(select(UserProjectAssignment.project_id).where(UserProjectAssignment.user_id == user.id)))


def _is_leader_scope(db: Session, user: User) -> bool:
    profile = _profile_code(db, user)
    return user.role == COORDINATOR or profile in {"collections_leader", "sales_leader", "legal_director"}


def _is_agent_scope(db: Session, user: User) -> bool:
    return user.role == AGENT and _profile_code(db, user) == "collections_agent"


def _allowed_source_codes(db: Session, user: User) -> set[str]:
    if is_platform_admin(db, user) or user.role == "tenant_admin":
        return set(SOURCE_DEFS)
    profile = _profile_code(db, user)
    if profile in {"lawyer", "legal_director"}:
        return LEGAL_SOURCES
    if profile in {"sales_advisor", "sales_leader"}:
        return SALES_SOURCES
    if _is_leader_scope(db, user):
        return LEADER_SOURCES
    if _is_agent_scope(db, user):
        return AGENT_SOURCES
    return {"customers", "alerts"}


def _customer_scope_select(db: Session, user: User):
    customer_ids = select(Customer.id).where(Customer.tenant_id == user.tenant_id)
    profile = _profile_code(db, user)
    if _is_agent_scope(db, user):
        return customer_ids.where(Customer.assigned_user_id == user.id)
    if _is_leader_scope(db, user):
        team_ids = _team_user_ids(db, user)
        project_ids = _project_ids(db, user)
        conditions = [Customer.assigned_user_id.in_(team_ids)]
        if project_ids:
            conditions.append(Customer.project_id.in_(project_ids))
        return customer_ids.where(or_(*conditions))
    if profile == "lawyer":
        return customer_ids.where(Customer.id.in_(select(LegalCase.customer_id).where(LegalCase.tenant_id == user.tenant_id, LegalCase.assigned_lawyer_id == user.id)))
    if profile == "sales_advisor":
        return customer_ids.where(Customer.assigned_user_id == user.id)
    return customer_ids


def _apply_role_scope(db: Session, user: User, source: str, model: Any, query):
    if is_platform_admin(db, user):
        return query
    if hasattr(model, "tenant_id"):
        query = query.where(model.tenant_id == user.tenant_id)
    if user.role == "tenant_admin":
        return query
    profile = _profile_code(db, user)
    customer_ids = _customer_scope_select(db, user)
    team_ids = _team_user_ids(db, user)
    project_ids = _project_ids(db, user)

    if source == "customers":
        return query.where(Customer.id.in_(customer_ids))
    if source == "obligations":
        if _is_agent_scope(db, user):
            return query.where((CustomerObligation.assigned_user_id == user.id) | CustomerObligation.customer_id.in_(customer_ids))
        if _is_leader_scope(db, user):
            conditions = [CustomerObligation.assigned_user_id.in_(team_ids), CustomerObligation.assigned_leader_id == user.id, CustomerObligation.customer_id.in_(customer_ids)]
            if project_ids:
                conditions.append(CustomerObligation.project_id.in_(project_ids))
            return query.where(or_(*conditions))
        return query.where(CustomerObligation.customer_id.in_(customer_ids))
    if source in {"activities", "promises", "payments", "agreements", "documents", "demographics"} and hasattr(model, "customer_id"):
        if _is_agent_scope(db, user) and hasattr(model, "user_id"):
            return query.where((model.user_id == user.id) | model.customer_id.in_(customer_ids))
        return query.where(model.customer_id.in_(customer_ids))
    if source == "alerts" and hasattr(model, "assigned_user_id"):
        if _is_agent_scope(db, user):
            return query.where(model.assigned_user_id == user.id)
        if _is_leader_scope(db, user):
            return query.where(model.assigned_user_id.in_(team_ids))
    if source == "legal_cases" and profile == "lawyer":
        return query.where(LegalCase.assigned_lawyer_id == user.id)
    if source in {"sales_leads", "opportunities"} and profile == "sales_advisor" and hasattr(model, "assigned_user_id"):
        return query.where(model.assigned_user_id == user.id)
    if project_ids and hasattr(model, "project_id") and _is_leader_scope(db, user):
        return query.where(model.project_id.in_(project_ids))
    return query


def _row(model: Any, item: Any, columns: list[str]) -> dict[str, Any]:
    return {column: getattr(item, column, None) for column in columns}


def _apply_filters(query, model: Any, filters: dict[str, Any]):
    text = filters.get("text") or filters.get("search")
    if text:
        expressions = []
        for field in ("name", "document", "phone", "email", "status", "risk", "case_number", "company", "obligation_number", "product_type", "portfolio_name"):
            if hasattr(model, field):
                expressions.append(getattr(model, field).ilike(f"%{text}%"))
        if expressions:
            query = query.where(or_(*expressions))
    for field in ("status", "risk", "project_id", "customer_id", "assigned_user_id", "user_id"):
        value = filters.get(field)
        if value not in (None, "") and hasattr(model, field):
            query = query.where(getattr(model, field) == value)
    if filters.get("dpd_min") is not None and hasattr(model, "dpd"):
        query = query.where(model.dpd >= int(filters["dpd_min"]))
    if filters.get("dpd_max") is not None and hasattr(model, "dpd"):
        query = query.where(model.dpd <= int(filters["dpd_max"]))
    if filters.get("dpd_min") is not None and hasattr(model, "days_past_due"):
        query = query.where(model.days_past_due >= int(filters["dpd_min"]))
    if filters.get("dpd_max") is not None and hasattr(model, "days_past_due"):
        query = query.where(model.days_past_due <= int(filters["dpd_max"]))
    return query


@router.get("/sources")
def sources(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[dict]:
    require_permission(db, user, "excel_web.view")
    allowed_codes = _allowed_source_codes(db, user)
    profile = _profile_code(db, user)
    prefix = "Mis " if _is_agent_scope(db, user) else "Equipo " if _is_leader_scope(db, user) else ""
    rows = []
    for code, definition in SOURCE_DEFS.items():
        if code not in allowed_codes:
            continue
        label = definition["label"]
        if prefix and code in {"customers", "obligations", "activities", "promises", "payments", "agreements", "alerts"}:
            label = f"{prefix}{label.lower()}"
        if profile == "sales_advisor" and code in {"sales_leads", "opportunities"}:
            label = f"Mis {label.lower()}"
        if profile == "lawyer" and code == "legal_cases":
            label = "Mis casos juridicos"
        rows.append({"code": code, **definition, "label": label})
    return rows


@router.post("/query", response_model=ExcelWebQueryResult)
def query_data(payload: ExcelWebQuery, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ExcelWebQueryResult:
    require_permission(db, user, "excel_web.query")
    if payload.source not in _allowed_source_codes(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fuente no autorizada para tu alcance.")
    if payload.source not in SOURCE_MODELS:
        return ExcelWebQueryResult(source=payload.source, columns=[], rows=[], total=0, page=payload.page, page_size=payload.page_size, total_pages=0)
    model = SOURCE_MODELS[payload.source]
    columns = [column for column in (payload.columns or SOURCE_DEFS[payload.source]["columns"]) if column in SOURCE_DEFS[payload.source]["columns"]]
    query = select(model)
    count_query = select(func.count(model.id))
    query = _apply_role_scope(db, user, payload.source, model, query)
    count_query = _apply_role_scope(db, user, payload.source, model, count_query)
    query = _apply_filters(query, model, payload.filters)
    count_query = _apply_filters(count_query, model, payload.filters)
    total = db.scalar(count_query) or 0
    items = list(db.scalars(query.order_by(model.id.desc()).offset((payload.page - 1) * payload.page_size).limit(payload.page_size)))
    return ExcelWebQueryResult(source=payload.source, columns=columns, rows=[_row(model, item, columns) for item in items], total=total, page=payload.page, page_size=payload.page_size, total_pages=ceil(total / payload.page_size) if total else 0)


@router.get("/views", response_model=list[SavedDataViewOut])
def list_views(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[SavedDataViewOut]:
    require_permission(db, user, "excel_web.views.manage")
    query = select(SavedDataView).where((SavedDataView.user_id == user.id) | (SavedDataView.is_public.is_(True))).order_by(SavedDataView.is_favorite.desc(), SavedDataView.name)
    if not is_platform_admin(db, user):
        query = query.where(SavedDataView.tenant_id == user.tenant_id)
    return [_view_to_out(item) for item in db.scalars(query)]


@router.post("/views", response_model=SavedDataViewOut, status_code=status.HTTP_201_CREATED)
def create_view(payload: SavedDataViewCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> SavedDataViewOut:
    require_permission(db, user, "excel_web.views.manage")
    if payload.source not in _allowed_source_codes(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fuente no autorizada para tu alcance.")
    view = SavedDataView(
        tenant_id=user.tenant_id,
        user_id=user.id,
        name=payload.name,
        source=payload.source,
        columns_json=json.dumps(payload.columns),
        filters_json=json.dumps(payload.filters),
        sort_json=json.dumps(payload.sort),
        is_public=payload.is_public,
        is_favorite=payload.is_favorite,
    )
    db.add(view)
    db.commit()
    db.refresh(view)
    return _view_to_out(view)


@router.patch("/views/{view_id}", response_model=SavedDataViewOut)
def update_view(view_id: int, payload: SavedDataViewCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> SavedDataViewOut:
    require_permission(db, user, "excel_web.views.manage")
    if payload.source not in _allowed_source_codes(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fuente no autorizada para tu alcance.")
    view = db.get(SavedDataView, view_id)
    if view is None or (not is_platform_admin(db, user) and view.tenant_id != user.tenant_id) or (view.user_id != user.id and not is_platform_admin(db, user)):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Vista no encontrada.")
    view.name = payload.name
    view.source = payload.source
    view.columns_json = json.dumps(payload.columns)
    view.filters_json = json.dumps(payload.filters)
    view.sort_json = json.dumps(payload.sort)
    view.is_public = payload.is_public
    view.is_favorite = payload.is_favorite
    db.commit()
    db.refresh(view)
    return _view_to_out(view)


@router.post("/export")
def export_data(payload: ExcelWebQuery, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "excel_web.export")
    result = query_data(payload, db, user)
    log = DataExportLog(tenant_id=user.tenant_id, user_id=user.id, source=payload.source, filters_json=json.dumps(payload.filters), columns_json=json.dumps(result.columns), row_count=result.total, status="completed")
    db.add(log)
    db.flush()
    record_audit(db, user, "excel_web_export", "create", entity_id=log.id, tenant_id=user.tenant_id, module="excel_web", after={"source": payload.source, "rows": result.total}, request=request)
    db.commit()
    return {"export_id": log.id, "source": payload.source, "row_count": result.total, "message": "Export registrado. La descarga fisica se habilitara con storage seguro."}


def _view_to_out(item: SavedDataView) -> SavedDataViewOut:
    return SavedDataViewOut(
        id=item.id,
        tenant_id=item.tenant_id,
        user_id=item.user_id,
        name=item.name,
        source=item.source,
        columns=json.loads(item.columns_json or "[]"),
        filters=json.loads(item.filters_json or "{}"),
        sort=json.loads(item.sort_json or "{}"),
        is_public=item.is_public,
        is_favorite=item.is_favorite,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
