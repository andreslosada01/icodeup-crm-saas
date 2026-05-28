from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import ManagementActivity, Payment, User
from app.schemas.crm import PaymentCreate, PaymentOut
from app.services.audit_service import record_audit

from .access import customer_for_access, customer_query, ensure_read_access


router = APIRouter()


@router.get("/payments", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[PaymentOut]:
    ensure_read_access(user)
    customers = list(db.scalars(customer_query(db, user)))
    customer_map = {customer.id: customer for customer in customers}
    payments = list(db.scalars(select(Payment).where(Payment.customer_id.in_(customer_map.keys())).order_by(Payment.paid_at.desc()))) if customer_map else []
    return [
        PaymentOut(id=item.id, customer_id=item.customer_id, customer_name=customer_map[item.customer_id].name if item.customer_id in customer_map else None, amount=item.amount, paid_at=item.paid_at, method=item.method, reference=item.reference, created_at=item.created_at)
        for item in payments
    ]


@router.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PaymentOut:
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
