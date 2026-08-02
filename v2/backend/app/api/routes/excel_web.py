from __future__ import annotations

import csv
import json
from math import ceil
from io import StringIO
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
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
    OperationalSheetRow,
    Payment,
    PaymentAgreement,
    PaymentPromise,
    Project,
    SavedDataView,
    Tenant,
    UploadBatch,
    User,
    UserProjectAssignment,
)
from app.schemas.collection_ops import (
    ExcelWebQuery,
    ExcelWebQueryResult,
    OperationalSheetRowCreate,
    OperationalSheetRowOut,
    OperationalSheetRowPatch,
    SavedDataViewCreate,
    SavedDataViewOut,
)
from app.core.roles import AGENT, COORDINATOR
from app.services.access_control import get_profile_role_code, is_platform_admin, require_permission, user_has_permission
from app.services.audit_service import record_audit


router = APIRouter()


SOURCE_DEFS = {
    "customers": {"label": "Clientes", "columns": ["id", "name", "document", "phone", "email", "city", "segment", "balance", "dpd", "status", "risk", "assigned_user_id"]},
    "obligations": {"label": "Obligaciones", "columns": ["id", "customer_id", "obligation_number", "product_type", "portfolio_name", "original_amount", "current_balance", "days_past_due", "status", "risk", "assigned_user_id", "assigned_leader_id"]},
    "activities": {"label": "Gestiones", "columns": ["id", "customer_id", "obligation_id", "user_id", "channel", "result", "note", "created_at"]},
    "promises": {"label": "Promesas", "columns": ["id", "customer_id", "obligation_id", "user_id", "amount", "due_date", "status", "channel"]},
    "payments": {"label": "PayControl 360", "columns": ["id", "customer_id", "user_id", "amount", "paid_at", "method", "reference"]},
    "agreements": {"label": "Acuerdos", "columns": ["id", "customer_id", "obligation_id", "user_id", "total_amount", "installment_count", "status", "created_at"]},
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
EXCEL_PAGE_SIZE = 10
EXCEL_EXPORT_LIMIT = 5000
SHEET_STATUSES = {"Pendiente", "Seguimiento", "Gestionado", "Pagos", "Cerrado"}


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


def _page_size(value: int | None) -> int:
    return min(max(int(value or EXCEL_PAGE_SIZE), 1), EXCEL_PAGE_SIZE)


def _require_sheet_manage(db: Session, user: User) -> None:
    if user_has_permission(db, user, "excel_web.sheet.manage") or user_has_permission(db, user, "excel_web.views.manage"):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permiso insuficiente para administrar la hoja operativa.")


def _target_tenant_id(db: Session, user: User, tenant_id: int | None = None) -> int:
    try:
        requested_id = int(tenant_id) if tenant_id else None
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Empresa invalida.") from exc
    if is_platform_admin(db, user):
        if requested_id:
            tenant = db.get(Tenant, requested_id)
            if tenant is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
            return tenant.id
        return user.tenant_id
    if requested_id and requested_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Empresa fuera de tu alcance.")
    return user.tenant_id


def _apply_filters(query, model: Any, filters: dict[str, Any]):
    text = filters.get("text") or filters.get("search")
    if text:
        expressions = []
        for field in ("name", "document", "phone", "email", "status", "risk", "case_number", "company", "obligation_number", "product_type", "portfolio_name"):
            if hasattr(model, field):
                expressions.append(getattr(model, field).ilike(f"%{text}%"))
        if expressions:
            query = query.where(or_(*expressions))
    for field in ("status", "risk", "project_id", "customer_id", "assigned_user_id", "user_id", "tenant_id"):
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
    date_field = next((getattr(model, field) for field in ("created_at", "paid_at", "due_date", "next_deadline_at", "date") if hasattr(model, field)), None)
    if date_field is not None and filters.get("date_from"):
        query = query.where(date_field >= filters["date_from"])
    if date_field is not None and filters.get("date_to"):
        query = query.where(date_field <= filters["date_to"])
    return query


def _apply_sheet_scope(db: Session, user: User, query, tenant_id: int | None = None):
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(OperationalSheetRow.tenant_id == tenant_id)
        return query
    query = query.where(OperationalSheetRow.tenant_id == user.tenant_id)
    if user.role == "tenant_admin":
        return query
    customer_ids = _customer_scope_select(db, user)
    team_ids = _team_user_ids(db, user)
    project_ids = _project_ids(db, user)
    if _is_agent_scope(db, user):
        return query.where((OperationalSheetRow.user_id == user.id) | OperationalSheetRow.customer_id.in_(customer_ids))
    if _is_leader_scope(db, user):
        conditions = [OperationalSheetRow.user_id.in_(team_ids), OperationalSheetRow.customer_id.in_(customer_ids)]
        if project_ids:
            conditions.append(OperationalSheetRow.project_id.in_(project_ids))
        return query.where(or_(*conditions))
    profile = _profile_code(db, user)
    if profile in {"lawyer", "sales_advisor"}:
        return query.where((OperationalSheetRow.user_id == user.id) | OperationalSheetRow.customer_id.in_(customer_ids))
    return query.where(OperationalSheetRow.user_id == user.id)


def _apply_sheet_filters(query, filters: dict[str, Any]):
    text = filters.get("text") or filters.get("q") or filters.get("search")
    if text:
        pattern = f"%{text}%"
        query = query.where(
            or_(
                OperationalSheetRow.customer_name.ilike(pattern),
                OperationalSheetRow.document.ilike(pattern),
                OperationalSheetRow.obligation_number.ilike(pattern),
                OperationalSheetRow.management_note.ilike(pattern),
                OperationalSheetRow.commitment.ilike(pattern),
                OperationalSheetRow.status.ilike(pattern),
                OperationalSheetRow.portfolio.ilike(pattern),
            )
        )
    for field in ("status", "project_id", "user_id", "customer_id", "obligation_id"):
        value = filters.get(field)
        if value not in (None, ""):
            query = query.where(getattr(OperationalSheetRow, field) == value)
    if filters.get("date_from"):
        query = query.where(OperationalSheetRow.date >= filters["date_from"])
    if filters.get("date_to"):
        query = query.where(OperationalSheetRow.date <= filters["date_to"])
    return query


def _ensure_sheet_references(db: Session, user: User, payload: OperationalSheetRowCreate | OperationalSheetRowPatch) -> None:
    if payload.project_id is not None:
        project = db.get(Project, payload.project_id)
        if project is None or (not is_platform_admin(db, user) and project.tenant_id != user.tenant_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Proyecto no autorizado para esta fila.")
    if payload.customer_id is not None:
        accessible_customer = db.scalar(select(Customer.id).where(Customer.id == payload.customer_id, Customer.id.in_(_customer_scope_select(db, user))))
        if accessible_customer is None and not (is_platform_admin(db, user) and db.get(Customer, payload.customer_id) is not None):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cliente no autorizado para esta fila.")
    if payload.obligation_id is not None:
        query = select(CustomerObligation.id).where(CustomerObligation.id == payload.obligation_id)
        query = _apply_role_scope(db, user, "obligations", CustomerObligation, query)
        if db.scalar(query) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Obligacion no autorizada para esta fila.")


def _safe_csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _sheet_to_out(db: Session, item: OperationalSheetRow) -> OperationalSheetRowOut:
    owner = db.get(User, item.user_id)
    return OperationalSheetRowOut(
        id=item.id,
        tenant_id=item.tenant_id,
        project_id=item.project_id,
        user_id=item.user_id,
        user_name=owner.name if owner else None,
        customer_id=item.customer_id,
        obligation_id=item.obligation_id,
        date=item.date,
        portfolio=item.portfolio,
        customer_name=item.customer_name,
        document=item.document,
        obligation_number=item.obligation_number,
        management_note=item.management_note,
        commitment=item.commitment,
        amount=item.amount,
        status=item.status,
        next_action_at=item.next_action_at,
        metadata=json.loads(item.metadata_json or "{}"),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


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
    page_size = _page_size(payload.page_size)
    if payload.source not in _allowed_source_codes(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fuente no autorizada para tu alcance.")
    if payload.source not in SOURCE_MODELS:
        return ExcelWebQueryResult(source=payload.source, columns=[], rows=[], total=0, page=payload.page, page_size=page_size, total_pages=0)
    model = SOURCE_MODELS[payload.source]
    columns = [column for column in (payload.columns or SOURCE_DEFS[payload.source]["columns"]) if column in SOURCE_DEFS[payload.source]["columns"]]
    query = select(model)
    count_query = select(func.count(model.id))
    query = _apply_role_scope(db, user, payload.source, model, query)
    count_query = _apply_role_scope(db, user, payload.source, model, count_query)
    query = _apply_filters(query, model, payload.filters)
    count_query = _apply_filters(count_query, model, payload.filters)
    total = db.scalar(count_query) or 0
    items = list(db.scalars(query.order_by(model.id.desc()).offset((payload.page - 1) * page_size).limit(page_size)))
    return ExcelWebQueryResult(source=payload.source, columns=columns, rows=[_row(model, item, columns) for item in items], total=total, page=payload.page, page_size=page_size, total_pages=ceil(total / page_size) if total else 0)


@router.get("/sheet-rows")
def list_sheet_rows(
    page: int = 1,
    page_size: int = EXCEL_PAGE_SIZE,
    tenant_id: int | None = None,
    q: str | None = None,
    row_status: str | None = Query(default=None, alias="status"),
    project_id: int | None = None,
    user_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    require_permission(db, user, "excel_web.query")
    page_size = _page_size(page_size)
    filters = {
        "q": q or "",
        "status": row_status or "",
        "project_id": project_id,
        "user_id": user_id,
        "date_from": date_from,
        "date_to": date_to,
    }
    query = _apply_sheet_scope(db, user, select(OperationalSheetRow), tenant_id=tenant_id)
    count_query = _apply_sheet_scope(db, user, select(func.count(OperationalSheetRow.id)), tenant_id=tenant_id)
    query = _apply_sheet_filters(query, filters)
    count_query = _apply_sheet_filters(count_query, filters)
    total = db.scalar(count_query) or 0
    items = list(db.scalars(query.order_by(OperationalSheetRow.id.desc()).offset((max(page, 1) - 1) * page_size).limit(page_size)))
    return {
        "items": [_sheet_to_out(db, item).model_dump(mode="json") for item in items],
        "total": total,
        "page": max(page, 1),
        "page_size": page_size,
        "total_pages": ceil(total / page_size) if total else 0,
        "statuses": sorted(SHEET_STATUSES),
    }


@router.post("/sheet-rows", status_code=status.HTTP_201_CREATED, response_model=OperationalSheetRowOut)
def create_sheet_row(payload: OperationalSheetRowCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> OperationalSheetRowOut:
    _require_sheet_manage(db, user)
    _ensure_sheet_references(db, user, payload)
    tenant_id = _target_tenant_id(db, user, payload.tenant_id)
    item = OperationalSheetRow(
        tenant_id=tenant_id,
        project_id=payload.project_id,
        user_id=user.id,
        customer_id=payload.customer_id,
        obligation_id=payload.obligation_id,
        date=payload.date,
        portfolio=payload.portfolio,
        customer_name=payload.customer_name,
        document=payload.document,
        obligation_number=payload.obligation_number,
        management_note=payload.management_note,
        commitment=payload.commitment,
        amount=payload.amount,
        status=payload.status if payload.status in SHEET_STATUSES else "Pendiente",
        next_action_at=payload.next_action_at,
        metadata_json=json.dumps(payload.metadata),
    )
    db.add(item)
    db.flush()
    record_audit(db, user, "excel_web_sheet_row", "create", entity_id=item.id, tenant_id=tenant_id, module="excel_web", after={"status": item.status, "amount": item.amount}, request=request)
    db.commit()
    db.refresh(item)
    return _sheet_to_out(db, item)


@router.patch("/sheet-rows/{row_id}", response_model=OperationalSheetRowOut)
def update_sheet_row(row_id: int, payload: OperationalSheetRowPatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> OperationalSheetRowOut:
    _require_sheet_manage(db, user)
    query = _apply_sheet_scope(db, user, select(OperationalSheetRow).where(OperationalSheetRow.id == row_id))
    item = db.scalar(query)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fila de seguimiento no encontrada.")
    _ensure_sheet_references(db, user, payload)
    before = {"status": item.status, "amount": item.amount}
    data = payload.model_dump(exclude_unset=True)
    if data.get("status") and data["status"] not in SHEET_STATUSES:
        data["status"] = "Pendiente"
    metadata = data.pop("metadata", None)
    for key, value in data.items():
        setattr(item, key, value)
    if metadata is not None:
        item.metadata_json = json.dumps(metadata)
    db.flush()
    record_audit(db, user, "excel_web_sheet_row", "update", entity_id=item.id, tenant_id=item.tenant_id, module="excel_web", before=before, after={"status": item.status, "amount": item.amount}, request=request)
    db.commit()
    db.refresh(item)
    return _sheet_to_out(db, item)


@router.get("/views", response_model=list[SavedDataViewOut])
def list_views(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[SavedDataViewOut]:
    require_permission(db, user, "excel_web.views.manage")
    query = select(SavedDataView).where((SavedDataView.user_id == user.id) | (SavedDataView.is_public.is_(True))).order_by(SavedDataView.is_favorite.desc(), SavedDataView.name)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(SavedDataView.tenant_id == tenant_id)
    else:
        query = query.where(SavedDataView.tenant_id == user.tenant_id)
    return [_view_to_out(item) for item in db.scalars(query)]


@router.post("/views", response_model=SavedDataViewOut, status_code=status.HTTP_201_CREATED)
def create_view(payload: SavedDataViewCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> SavedDataViewOut:
    require_permission(db, user, "excel_web.views.manage")
    if payload.source not in _allowed_source_codes(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fuente no autorizada para tu alcance.")
    tenant_id = _target_tenant_id(db, user, payload.tenant_id)
    view = SavedDataView(
        tenant_id=tenant_id,
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
def export_data(payload: ExcelWebQuery, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Response:
    require_permission(db, user, "excel_web.export")
    if payload.source not in _allowed_source_codes(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fuente no autorizada para tu alcance.")
    if payload.source not in SOURCE_MODELS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuente no encontrada.")
    model = SOURCE_MODELS[payload.source]
    columns = [column for column in (payload.columns or SOURCE_DEFS[payload.source]["columns"]) if column in SOURCE_DEFS[payload.source]["columns"]]
    count_query = _apply_filters(_apply_role_scope(db, user, payload.source, model, select(func.count(model.id))), model, payload.filters)
    total = db.scalar(count_query) or 0
    if total > EXCEL_EXPORT_LIMIT:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"La consulta supera el limite seguro de {EXCEL_EXPORT_LIMIT} filas. Reduce filtros antes de exportar.")
    query = _apply_filters(_apply_role_scope(db, user, payload.source, model, select(model)), model, payload.filters)
    items = list(db.scalars(query.order_by(model.id.desc()).limit(EXCEL_EXPORT_LIMIT)))
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for item in items:
        writer.writerow({column: _safe_csv_value(getattr(item, column, None)) for column in columns})
    log_tenant_id = _target_tenant_id(db, user, payload.filters.get("tenant_id"))
    log = DataExportLog(tenant_id=log_tenant_id, user_id=user.id, source=payload.source, filters_json=json.dumps(payload.filters), columns_json=json.dumps(columns), row_count=len(items), status="completed")
    db.add(log)
    db.flush()
    record_audit(db, user, "excel_web_export", "create", entity_id=log.id, tenant_id=log_tenant_id, module="excel_web", after={"source": payload.source, "rows": len(items)}, request=request)
    db.commit()
    file_name = f"iep_{payload.source}_{log.id}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


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
