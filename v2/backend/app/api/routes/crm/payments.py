from __future__ import annotations

import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Customer, CustomerObligation, ManagementActivity, Payment, User
from app.schemas.crm import PaymentCreate, PaymentOut
from app.services.audit_service import record_audit
from app.services.access_control import require_permission

from .access import customer_for_access, customer_query, ensure_read_access, is_platform
from .obligations import obligation_for_access


router = APIRouter()


def payment_to_out(db: Session, item: Payment, customer: Customer | None = None) -> PaymentOut:
    customer = customer or db.get(Customer, item.customer_id)
    obligation = db.get(CustomerObligation, item.obligation_id) if item.obligation_id else None
    return PaymentOut(
        id=item.id,
        tenant_id=item.tenant_id,
        project_id=item.project_id,
        customer_id=item.customer_id,
        customer_name=customer.name if customer else None,
        obligation_id=item.obligation_id,
        obligation_number=obligation.obligation_number if obligation else None,
        amount=item.amount,
        paid_at=item.paid_at,
        method=item.method,
        reference=item.reference,
        created_at=item.created_at,
    )


@router.get("/payments", response_model=list[PaymentOut])
def list_payments(tenant_id: int | None = None, limit: int = Query(default=10, ge=1, le=10), db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[PaymentOut]:
    require_permission(db, user, "collections.payments.view")
    ensure_read_access(user)
    query = customer_query(db, user)
    if tenant_id and is_platform(user):
        query = query.where(Customer.tenant_id == tenant_id)
    customers = list(db.scalars(query))
    customer_map = {customer.id: customer for customer in customers}
    payments = list(db.scalars(select(Payment).where(Payment.customer_id.in_(customer_map.keys())).order_by(Payment.paid_at.desc()).limit(limit))) if customer_map else []
    return [payment_to_out(db, item, customer_map.get(item.customer_id)) for item in payments]


@router.get("/payments/export")
def export_payments(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> StreamingResponse:
    require_permission(db, user, "collections.payments.export")
    query = customer_query(db, user)
    if tenant_id and is_platform(user):
        query = query.where(Customer.tenant_id == tenant_id)
    customers = list(db.scalars(query))
    customer_map = {customer.id: customer for customer in customers}
    payments = list(db.scalars(select(Payment).where(Payment.customer_id.in_(customer_map.keys())).order_by(Payment.paid_at.desc()))) if customer_map else []
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["tenant_id", "project_id", "customer_id", "customer_name", "obligation_id", "obligation_number", "amount", "paid_at", "method", "reference"])
    for payment in payments:
        customer = customer_map.get(payment.customer_id)
        obligation = db.get(CustomerObligation, payment.obligation_id) if payment.obligation_id else None
        writer.writerow([payment.tenant_id, payment.project_id, payment.customer_id, customer.name if customer else "", payment.obligation_id or "", obligation.obligation_number if obligation else "", payment.amount, payment.paid_at, payment.method, payment.reference])
    output.seek(0)
    record_audit(db, user, "payment", "export", None, user.tenant_id, module="collections", after={"payment_count": len(payments)})
    db.commit()
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=pagos_iep.csv"})


@router.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PaymentOut:
    require_permission(db, user, "collections.payments.create")
    customer = customer_for_access(db, payload.customer_id, user, write=True)
    obligation = obligation_for_access(db, payload.obligation_id, user, write=False) if payload.obligation_id else None
    if obligation and obligation.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La obligacion no pertenece al cliente seleccionado.")
    payment = Payment(
        tenant_id=customer.tenant_id,
        project_id=obligation.project_id if obligation and obligation.project_id else customer.project_id,
        customer_id=customer.id,
        obligation_id=obligation.id if obligation else None,
        user_id=user.id,
        amount=payload.amount,
        paid_at=payload.paid_at,
        method=payload.method,
        reference=payload.reference,
    )
    if obligation:
        obligation.current_balance = max(0, obligation.current_balance - payload.amount)
        obligation.status = "paid" if obligation.current_balance == 0 else "partial_payment"
        db.flush()
        customer.balance = sum(db.scalars(select(CustomerObligation.current_balance).where(CustomerObligation.customer_id == customer.id, CustomerObligation.tenant_id == customer.tenant_id))) or 0
    else:
        customer.balance = max(0, customer.balance - payload.amount)
    customer.status = "Pagado" if customer.balance == 0 else "Pago parcial"
    customer.next_action = "Cerrar caso" if customer.balance == 0 else "Confirmar saldo restante"
    db.add(payment)
    db.add(ManagementActivity(tenant_id=customer.tenant_id, project_id=payment.project_id, customer_id=customer.id, obligation_id=payment.obligation_id, user_id=user.id, channel="payment", result=customer.status, note=f"Pago registrado por {payload.amount}."))
    db.flush()
    record_audit(db, user, "payment", "create", payment.id, payment.tenant_id, after={"customer_id": customer.id, "obligation_id": payment.obligation_id, "amount": payment.amount})
    db.commit()
    db.refresh(payment)
    return payment_to_out(db, payment, customer)
