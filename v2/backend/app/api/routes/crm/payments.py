from __future__ import annotations

import csv
from io import StringIO

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import ManagementActivity, Payment, User
from app.schemas.crm import PaymentCreate, PaymentOut
from app.services.audit_service import record_audit
from app.services.access_control import require_permission

from .access import customer_for_access, customer_query, ensure_read_access


router = APIRouter()


@router.get("/payments", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[PaymentOut]:
    require_permission(db, user, "collections.payments.view")
    ensure_read_access(user)
    customers = list(db.scalars(customer_query(db, user)))
    customer_map = {customer.id: customer for customer in customers}
    payments = list(db.scalars(select(Payment).where(Payment.customer_id.in_(customer_map.keys())).order_by(Payment.paid_at.desc()))) if customer_map else []
    return [
        PaymentOut(id=item.id, customer_id=item.customer_id, customer_name=customer_map[item.customer_id].name if item.customer_id in customer_map else None, amount=item.amount, paid_at=item.paid_at, method=item.method, reference=item.reference, created_at=item.created_at)
        for item in payments
    ]


@router.get("/payments/export")
def export_payments(db: Session = Depends(get_db), user: User = Depends(current_user)) -> StreamingResponse:
    require_permission(db, user, "collections.payments.export")
    customers = list(db.scalars(customer_query(db, user)))
    customer_map = {customer.id: customer for customer in customers}
    payments = list(db.scalars(select(Payment).where(Payment.customer_id.in_(customer_map.keys())).order_by(Payment.paid_at.desc()))) if customer_map else []
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["tenant_id", "project_id", "customer_id", "customer_name", "amount", "paid_at", "method", "reference"])
    for payment in payments:
        customer = customer_map.get(payment.customer_id)
        writer.writerow([payment.tenant_id, payment.project_id, payment.customer_id, customer.name if customer else "", payment.amount, payment.paid_at, payment.method, payment.reference])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=pagos_icodeup360.csv"})


@router.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PaymentOut:
    require_permission(db, user, "collections.payments.create")
    customer = customer_for_access(db, payload.customer_id, user, write=True)
    payment = Payment(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        user_id=user.id,
        amount=payload.amount,
        paid_at=payload.paid_at,
        method=payload.method,
        reference=payload.reference,
    )
    customer.balance = max(0, customer.balance - payload.amount)
    customer.status = "Pagado" if customer.balance == 0 else "Pago parcial"
    customer.next_action = "Cerrar caso" if customer.balance == 0 else "Confirmar saldo restante"
    db.add(payment)
    db.add(ManagementActivity(tenant_id=customer.tenant_id, project_id=customer.project_id, customer_id=customer.id, user_id=user.id, channel="payment", result=customer.status, note=f"Pago registrado por {payload.amount}."))
    db.flush()
    record_audit(db, user, "payment", "create", payment.id, payment.tenant_id, after={"customer_id": customer.id, "amount": payment.amount})
    db.commit()
    db.refresh(payment)
    return PaymentOut(id=payment.id, customer_id=customer.id, customer_name=customer.name, amount=payment.amount, paid_at=payment.paid_at, method=payment.method, reference=payment.reference, created_at=payment.created_at)
