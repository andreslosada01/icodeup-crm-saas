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
from app.services.access_control import get_profile_role_code, require_active_module, require_permission, user_has_permission
from app.services.plan_limits import check_storage_limit


router = APIRouter(dependencies=[Depends(require_active_module("documents"))])
DOCUMENT_MANAGE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}
DOCUMENT_READ_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, QUALITY_SUPERVISOR, AGENT}


def ensure_document_read(db: Session, user: User) -> None:
    if user_has_permission(db, user, "documents.view"):
        return
    if user.role not in DOCUMENT_READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso documental.")


def ensure_document_manage(db: Session, user: User) -> None:
    if user_has_permission(db, user, "documents.create") or user_has_permission(db, user, "documents.update"):
        return
    if user.role not in DOCUMENT_MANAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso para gestionar documentos.")


def safe_storage_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_") or "documento"


def validate_document_relations(db: Session, payload: DocumentCreate, tenant_id: int, user: User) -> None:
    profile_role = get_profile_role_code(db, user)
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
        if user.role == AGENT and profile_role == "lawyer" and legal_case.assigned_lawyer_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Caso juridico no asignado.")
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
    profile_role = get_profile_role_code(db, user)
    if user.role == AGENT and profile_role == "lawyer":
        if document.legal_case_id is None:
            if document.customer_id is None:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Documento no asociado a un caso juridico asignado.")
            customer_for_access(db, document.customer_id, user)
        else:
            legal_case = db.get(LegalCase, document.legal_case_id)
            if legal_case is None or legal_case.assigned_lawyer_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Documento no asociado a un caso juridico asignado.")
    elif user.role == AGENT and profile_role not in {"legal_director", "sales_leader", "sales_advisor"}:
        if document.customer_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Documento no asociado a un cliente asignado.")
        customer_for_access(db, document.customer_id, user)
    if write:
        ensure_document_manage(db, user)
    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[Document]:
    require_permission(db, user, "documents.view")
    ensure_document_read(db, user)
    query = select(Document).order_by(Document.created_at.desc())
    if not is_platform(user):
        query = query.where(Document.tenant_id == user.tenant_id)
    profile_role = get_profile_role_code(db, user)
    if user.role == AGENT and profile_role == "lawyer":
        legal_case_ids = select(LegalCase.id).where(LegalCase.tenant_id == user.tenant_id, LegalCase.assigned_lawyer_id == user.id)
        query = query.where(Document.legal_case_id.in_(legal_case_ids))
    elif user.role == AGENT and profile_role not in {"legal_director", "sales_leader", "sales_advisor"}:
        visible_customers = list(db.scalars(customer_query(db, user)))
        customer_ids = [customer.id for customer in visible_customers]
        query = query.where(Document.customer_id.in_(customer_ids)) if customer_ids else query.where(False)
    return list(db.scalars(query))


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Document:
    require_permission(db, user, "documents.create")
    ensure_document_manage(db, user)
    tenant_id = payload.tenant_id if is_platform(user) and payload.tenant_id else user.tenant_id
    validate_document_relations(db, payload, tenant_id, user)
    check_storage_limit(db, tenant_id, additional_mb=payload.size_bytes / (1024 * 1024), user=user)
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
    require_permission(db, user, "documents.view")
    ensure_document_read(db, user)
    return document_for_access(db, document_id, user)


@router.patch("/{document_id}", response_model=DocumentOut)
def update_document(document_id: int, payload: DocumentPatch, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Document:
    require_permission(db, user, "documents.update")
    document = document_for_access(db, document_id, user, write=True)
    updates = payload.model_dump(exclude_unset=True)
    if "size_bytes" in updates and updates["size_bytes"] is not None:
        additional_bytes = max(0, int(updates["size_bytes"]) - document.size_bytes)
        check_storage_limit(db, document.tenant_id, additional_mb=additional_bytes / (1024 * 1024), user=user)
    for field, value in updates.items():
        setattr(document, field, value)
    record_audit(db, user, "document", "update", document.id, document.tenant_id, after=updates)
    db.commit()
    db.refresh(document)
    return document
