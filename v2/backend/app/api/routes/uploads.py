from __future__ import annotations

import csv
import json
from io import StringIO
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Customer, CustomerDemographic, Project, UploadBatch, User
from app.schemas.collection_ops import CustomerDemographicCreate, CustomerDemographicOut, UploadBatchOut, UploadConfirmRequest, UploadPreviewRequest, UploadPreviewResponse
from app.services.access_control import is_platform_admin, require_permission, require_tenant
from app.services.audit_service import record_audit


router = APIRouter()


def _tenant_id(db: Session, user: User, requested: int | None = None) -> int:
    return require_tenant(db, user, requested).id


def _ensure_project(db: Session, tenant_id: int, project_id: int | None) -> None:
    if project_id is None:
        return
    project = db.get(Project, project_id)
    if project is None or project.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Proyecto fuera de la empresa.")


def _parse_csv(text: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(StringIO(text))
    columns = list(reader.fieldnames or [])
    rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    return columns, rows


def _preview(payload: UploadPreviewRequest) -> UploadPreviewResponse:
    columns, rows = _parse_csv(payload.csv_text)
    errors: list[dict] = []
    required = ["document"] if payload.upload_type in {"reparto_cartera", "demograficos"} else []
    for index, row in enumerate(rows, start=2):
        missing = [field for field in required if not row.get(payload.mapping.get(field, field))]
        if missing:
            errors.append({"row": index, "missing": missing, "message": "Faltan campos obligatorios."})
    return UploadPreviewResponse(
        total_rows=len(rows),
        valid_rows=max(0, len(rows) - len(errors)),
        error_rows=len(errors),
        columns=columns,
        sample=rows[:10],
        errors=errors[:50],
    )


@router.post("/preview", response_model=UploadPreviewResponse)
def preview_upload(payload: UploadPreviewRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> UploadPreviewResponse:
    require_permission(db, user, "uploads.view")
    tenant_id = _tenant_id(db, user, payload.tenant_id)
    _ensure_project(db, tenant_id, payload.project_id)
    return _preview(payload)


@router.post("/confirm", response_model=UploadBatchOut, status_code=status.HTTP_201_CREATED)
def confirm_upload(payload: UploadConfirmRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> UploadBatch:
    permission = "uploads.repartos.manage" if payload.upload_type == "reparto_cartera" else "uploads.manage"
    if payload.upload_type == "demograficos":
        permission = "uploads.demographics.manage"
    require_permission(db, user, permission)
    tenant_id = _tenant_id(db, user, payload.tenant_id)
    _ensure_project(db, tenant_id, payload.project_id)
    preview = _preview(payload)
    created_rows = 0
    updated_rows = 0
    if payload.create_records and payload.upload_type == "reparto_cartera" and payload.project_id:
        _columns, rows = _parse_csv(payload.csv_text)
        for row in rows:
            document = row.get(payload.mapping.get("document", "document")) or row.get("documento")
            name = row.get(payload.mapping.get("name", "name")) or row.get("cliente") or row.get("nombre")
            if not document or not name:
                continue
            customer = db.scalar(select(Customer).where(Customer.tenant_id == tenant_id, Customer.document == document))
            if customer is None:
                customer = Customer(tenant_id=tenant_id, project_id=payload.project_id, name=name, document=document)
                db.add(customer)
                created_rows += 1
            else:
                updated_rows += 1
            customer.phone = row.get(payload.mapping.get("phone", "phone"), customer.phone)
            customer.email = row.get(payload.mapping.get("email", "email"), customer.email)
            customer.city = row.get(payload.mapping.get("city", "city"), customer.city)
            customer.segment = row.get(payload.mapping.get("segment", "segment"), customer.segment)
            balance = row.get(payload.mapping.get("balance", "balance"))
            if balance and balance.isdigit():
                customer.balance = int(balance)
                customer.original_balance = customer.original_balance or int(balance)
            dpd = row.get(payload.mapping.get("dpd", "dpd"))
            if dpd and dpd.isdigit():
                customer.dpd = int(dpd)
    batch = UploadBatch(
        tenant_id=tenant_id,
        project_id=payload.project_id,
        uploaded_by_id=user.id,
        upload_type=payload.upload_type,
        original_filename=payload.file_name,
        status="completed" if preview.error_rows == 0 else "completed_with_errors",
        total_rows=preview.total_rows,
        valid_rows=preview.valid_rows,
        error_rows=preview.error_rows,
        created_rows=created_rows,
        updated_rows=updated_rows,
        mapping_json=json.dumps(payload.mapping),
        summary_json=json.dumps({"columns": preview.columns, "sample": preview.sample[:3], "errors": preview.errors[:10]}),
        error_file_path=f"tenants/demo/uploads/errors_{payload.upload_type}.csv" if preview.error_rows else None,
        result_file_path=f"tenants/demo/uploads/result_{payload.upload_type}.csv",
    )
    db.add(batch)
    db.flush()
    record_audit(db, user, "upload_batch", "confirm", entity_id=batch.id, tenant_id=tenant_id, module="uploads", after={"upload_type": payload.upload_type, "rows": preview.total_rows}, request=request)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/batches", response_model=list[UploadBatchOut])
def list_batches(upload_type: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[UploadBatch]:
    require_permission(db, user, "uploads.view")
    query = select(UploadBatch).order_by(UploadBatch.created_at.desc()).limit(100)
    if not is_platform_admin(db, user):
        query = query.where(UploadBatch.tenant_id == user.tenant_id)
    if upload_type:
        query = query.where(UploadBatch.upload_type == upload_type)
    return list(db.scalars(query))


@router.get("/batches/{batch_id}", response_model=UploadBatchOut)
def get_batch(batch_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> UploadBatch:
    require_permission(db, user, "uploads.view")
    batch = db.get(UploadBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado.")
    if not is_platform_admin(db, user) and batch.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lote fuera de tu empresa.")
    return batch


@router.get("/batches/{batch_id}/errors")
def batch_errors(batch_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "uploads.download")
    batch = get_batch(batch_id, db, user)
    return {"batch_id": batch.id, "error_file_path": batch.error_file_path, "summary": json.loads(batch.summary_json or "{}")}


@router.get("/batches/{batch_id}/result")
def batch_result(batch_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "uploads.download")
    batch = get_batch(batch_id, db, user)
    return {"batch_id": batch.id, "result_file_path": batch.result_file_path, "summary": json.loads(batch.summary_json or "{}")}


@router.get("/demographics", response_model=list[CustomerDemographicOut])
def list_demographics(customer_id: int | None = None, page: int = 1, page_size: int = 50, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[CustomerDemographicOut]:
    require_permission(db, user, "demographics.view")
    page_size = min(max(page_size, 1), 100)
    query = select(CustomerDemographic).order_by(CustomerDemographic.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    if not is_platform_admin(db, user):
        query = query.where(CustomerDemographic.tenant_id == user.tenant_id)
    if customer_id:
        query = query.where(CustomerDemographic.customer_id == customer_id)
    return [_demographic_to_out(item) for item in db.scalars(query)]


@router.post("/demographics", response_model=CustomerDemographicOut, status_code=status.HTTP_201_CREATED)
def create_demographic(payload: CustomerDemographicCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CustomerDemographicOut:
    require_permission(db, user, "demographics.manage")
    tenant_id = _tenant_id(db, user, payload.tenant_id)
    customer = db.get(Customer, payload.customer_id)
    if customer is None or customer.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente fuera de la empresa.")
    existing = db.scalar(
        select(CustomerDemographic).where(
            CustomerDemographic.tenant_id == tenant_id,
            CustomerDemographic.customer_id == customer.id,
            CustomerDemographic.source == payload.source,
            CustomerDemographic.phone == payload.phone,
            CustomerDemographic.email == payload.email,
        )
    )
    if existing:
        return _demographic_to_out(existing)
    demographic = CustomerDemographic(**payload.model_dump(exclude={"tenant_id", "metadata"}), tenant_id=tenant_id, metadata_json=json.dumps(payload.metadata))
    db.add(demographic)
    db.flush()
    record_audit(db, user, "customer_demographic", "create", entity_id=demographic.id, tenant_id=tenant_id, module="uploads", after={"customer_id": customer.id, "source": payload.source}, request=request)
    db.commit()
    db.refresh(demographic)
    return _demographic_to_out(demographic)


def _demographic_to_out(item: CustomerDemographic) -> CustomerDemographicOut:
    return CustomerDemographicOut(
        id=item.id,
        tenant_id=item.tenant_id,
        customer_id=item.customer_id,
        source=item.source,
        phone=item.phone,
        email=item.email,
        address=item.address,
        city=item.city,
        state=item.state,
        employer=item.employer,
        job_title=item.job_title,
        reference_name=item.reference_name,
        reference_phone=item.reference_phone,
        score=item.score,
        metadata=json.loads(item.metadata_json or "{}"),
        is_active=item.is_active,
        created_at=item.created_at,
    )
