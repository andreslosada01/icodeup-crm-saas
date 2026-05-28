from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.routes.crm.access import customer_for_access, customer_query, is_platform, project_for_access
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import Document, LegalCase, Payment, PaymentAgreement, User
from app.schemas.documents import DocumentCreate, DocumentOut, DocumentPatch
from app.services.audit_service import record_audit


router = APIRouter()
DOCUMENT_MANAGE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}
DOCUMENT_READ_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, QUALITY_SUPERVISOR, AGENT}


def ensure_document_read(user: User) -> None:
    if user.role not in DOCUMENT_READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso documental.")


def ensure_document_manage(user: User) -> None:
    if user.role not in DOCUMENT_MANAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso para gestionar documentos.")


def safe_storage_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_") or "documento"


def validate_document_relations(db: Session, payload: DocumentCreate, tenant_id: int, user: User) -> None:
    if payload.project_id:
        project = project_for_access(db, payload.project_id, user)
        if project.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Proyecto fuera de la empresa.")
    if payload.customer_id:
        customer = customer_for_access(db, payload.customer_id, user)
        if customer.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente fuera de la empresa.")
    if payload.legal_case_id:
        legal_case = db.get(LegalCase, payload.legal_case_id)
        if legal_case is None or legal_case.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Caso juridico fuera de la empresa.")
    if payload.payment_id:
        payment = db.get(Payment, payload.payment_id)
        if payment is None or payment.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Pago fuera de la empresa.")
    if payload.agreement_id:
        agreement = db.get(PaymentAgreement, payload.agreement_id)
        if agreement is None or agreement.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Acuerdo fuera de la empresa.")


def document_for_access(db: Session, document_id: int, user: User, write: bool = False) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado.")
    if not is_platform(user) and document.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Documento fuera de tu empresa.")
    if user.role == AGENT:
        if document.customer_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Documento no asociado a un cliente asignado.")
        customer_for_access(db, document.customer_id, user)
    if write:
        ensure_document_manage(user)
    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[Document]:
    ensure_document_read(user)
    query = select(Document).order_by(Document.created_at.desc())
    if not is_platform(user):
        query = query.where(Document.tenant_id == user.tenant_id)
    if user.role == AGENT:
        visible_customers = list(db.scalars(customer_query(db, user)))
        customer_ids = [customer.id for customer in visible_customers]
        query = query.where(Document.customer_id.in_(customer_ids)) if customer_ids else query.where(False)
    return list(db.scalars(query))


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Document:
    ensure_document_manage(user)
    tenant_id = payload.tenant_id if is_platform(user) and payload.tenant_id else user.tenant_id
    validate_document_relations(db, payload, tenant_id, user)
    storage_path = payload.storage_path or f"tenants/{tenant_id}/documents/{safe_storage_name(payload.original_name)}"
    document = Document(tenant_id=tenant_id, uploaded_by_id=user.id, storage_path=storage_path, **payload.model_dump(exclude={"tenant_id", "storage_path"}))
    db.add(document)
    db.flush()
    record_audit(db, user, "document", "create", document.id, document.tenant_id, after={"document_type": document.document_type, "original_name": document.original_name})
    db.commit()
    db.refresh(document)
    return document


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Document:
    ensure_document_read(user)
    return document_for_access(db, document_id, user)


@router.patch("/{document_id}", response_model=DocumentOut)
def update_document(document_id: int, payload: DocumentPatch, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Document:
    document = document_for_access(db, document_id, user, write=True)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    db.commit()
    db.refresh(document)
    return document
