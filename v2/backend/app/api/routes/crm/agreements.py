from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import Customer, PaymentAgreement, PaymentAgreementInstallment, User
from app.schemas.crm import AgreementInstallmentOut, AgreementInstallmentPatch, PaymentAgreementCreate, PaymentAgreementOut
from app.services.audit_service import record_audit
from app.services.access_control import require_permission

from .access import customer_for_access, customer_query, ensure_read_access, is_platform


router = APIRouter()
AGREEMENT_WRITE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, AGENT}


def ensure_agreement_write(user: User) -> None:
    if user.role not in AGREEMENT_WRITE_ROLES or user.role == QUALITY_SUPERVISOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso para gestionar acuerdos.")


def agreement_for_access(db: Session, agreement_id: int, user: User, write: bool = False) -> PaymentAgreement:
    agreement = db.get(PaymentAgreement, agreement_id)
    if agreement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acuerdo no encontrado.")
    customer_for_access(db, agreement.customer_id, user, write=write)
    if write:
        ensure_agreement_write(user)
    return agreement


def agreement_to_out(db: Session, agreement: PaymentAgreement) -> PaymentAgreementOut:
    customer = db.get(Customer, agreement.customer_id)
    installments = sorted(agreement.installments, key=lambda item: item.due_date)
    return PaymentAgreementOut(
        id=agreement.id,
        tenant_id=agreement.tenant_id,
        project_id=agreement.project_id,
        customer_id=agreement.customer_id,
        customer_name=customer.name if customer else None,
        user_id=agreement.user_id,
        total_amount=agreement.total_amount,
        installment_count=agreement.installment_count,
        start_date=agreement.start_date,
        status=agreement.status,
        notes=agreement.notes,
        created_at=agreement.created_at,
        installments=[AgreementInstallmentOut.model_validate(item, from_attributes=True) for item in installments],
    )


@router.get("/agreements", response_model=list[PaymentAgreementOut])
def list_agreements(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[PaymentAgreementOut]:
    require_permission(db, user, "collections.agreements.view")
    ensure_read_access(user)
    if is_platform(user):
        agreements = list(db.scalars(select(PaymentAgreement).order_by(PaymentAgreement.created_at.desc())))
    else:
        customers = list(db.scalars(customer_query(db, user)))
        customer_ids = [customer.id for customer in customers]
        agreements = list(db.scalars(select(PaymentAgreement).where(PaymentAgreement.customer_id.in_(customer_ids)).order_by(PaymentAgreement.created_at.desc()))) if customer_ids else []
    return [agreement_to_out(db, agreement) for agreement in agreements]


@router.post("/agreements", response_model=PaymentAgreementOut, status_code=status.HTTP_201_CREATED)
def create_agreement(payload: PaymentAgreementCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PaymentAgreementOut:
    require_permission(db, user, "collections.agreements.create")
    ensure_agreement_write(user)
    customer = customer_for_access(db, payload.customer_id, user, write=False)
    installments_payload = payload.installments or []
    if installments_payload and len(installments_payload) != payload.installment_count:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El numero de cuotas no coincide con installment_count.")
    agreement = PaymentAgreement(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        user_id=user.id,
        total_amount=payload.total_amount,
        installment_count=payload.installment_count,
        start_date=payload.start_date,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(agreement)
    db.flush()
    if installments_payload:
        for item in installments_payload:
            db.add(PaymentAgreementInstallment(agreement_id=agreement.id, due_date=item.due_date, amount=item.amount))
    else:
        amount = round(payload.total_amount / payload.installment_count)
        for index in range(payload.installment_count):
            db.add(PaymentAgreementInstallment(agreement_id=agreement.id, due_date=payload.start_date + timedelta(days=30 * index), amount=amount))
    customer.status = "Acuerdo"
    customer.next_action = "Monitorear cumplimiento de acuerdo"
    record_audit(db, user, "payment_agreement", "create", agreement.id, agreement.tenant_id, after={"customer_id": customer.id, "total_amount": agreement.total_amount})
    db.commit()
    db.refresh(agreement)
    return agreement_to_out(db, agreement)


@router.get("/agreements/{agreement_id}", response_model=PaymentAgreementOut)
def get_agreement(agreement_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PaymentAgreementOut:
    require_permission(db, user, "collections.agreements.view")
    ensure_read_access(user)
    return agreement_to_out(db, agreement_for_access(db, agreement_id, user))


@router.patch("/agreements/{agreement_id}/installments/{installment_id}", response_model=PaymentAgreementOut)
def update_installment(
    agreement_id: int,
    installment_id: int,
    payload: AgreementInstallmentPatch,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> PaymentAgreementOut:
    require_permission(db, user, "collections.agreements.update")
    agreement = agreement_for_access(db, agreement_id, user, write=True)
    installment = db.get(PaymentAgreementInstallment, installment_id)
    if installment is None or installment.agreement_id != agreement.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuota no encontrada.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(installment, field, value)
    if installment.paid_amount >= installment.amount:
        installment.status = "paid"
    agreement.status = "completed" if all(item.status == "paid" for item in agreement.installments) else agreement.status
    db.commit()
    db.refresh(agreement)
    return agreement_to_out(db, agreement)
