from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import ManagementActivity, PaymentPromise, User
from app.schemas.crm import PromiseCreate, PromiseOut
from app.services.audit_service import record_audit
from app.services.access_control import require_permission

from .access import customer_for_access, customer_query, ensure_read_access


router = APIRouter()


@router.get("/promises", response_model=list[PromiseOut])
def list_promises(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[PromiseOut]:
    require_permission(db, user, "collections.promises.view")
    ensure_read_access(user)
    customers = list(db.scalars(customer_query(db, user)))
    customer_map = {customer.id: customer for customer in customers}
    promises = list(db.scalars(select(PaymentPromise).where(PaymentPromise.customer_id.in_(customer_map.keys())).order_by(PaymentPromise.due_date.desc()))) if customer_map else []
    return [
        PromiseOut(
            id=item.id,
            customer_id=item.customer_id,
            customer_name=customer_map[item.customer_id].name if item.customer_id in customer_map else None,
            amount=item.amount,
            due_date=item.due_date,
            channel=item.channel,
            status=item.status,
            created_at=item.created_at,
        )
        for item in promises
    ]


@router.post("/promises", response_model=PromiseOut, status_code=status.HTTP_201_CREATED)
def create_promise(payload: PromiseCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PromiseOut:
    require_permission(db, user, "collections.promises.create")
    customer = customer_for_access(db, payload.customer_id, user, write=True)
    promise = PaymentPromise(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        user_id=user.id,
        amount=payload.amount,
        due_date=payload.due_date,
        channel=payload.channel,
    )
    customer.status = "Promesa"
    customer.next_action = "Confirmar cumplimiento de promesa"
    db.add(promise)
    db.flush()
    record_audit(db, user, "payment_promise", "create", promise.id, promise.tenant_id, after={"customer_id": customer.id, "amount": promise.amount})
    db.commit()
    db.refresh(promise)
    return PromiseOut(id=promise.id, customer_id=customer.id, customer_name=customer.name, amount=promise.amount, due_date=promise.due_date, channel=promise.channel, status=promise.status, created_at=promise.created_at)


@router.patch("/promises/{promise_id}/complete", response_model=PromiseOut)
def complete_promise(promise_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PromiseOut:
    require_permission(db, user, "collections.promises.update")
    promise = db.get(PaymentPromise, promise_id)
    if promise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promesa no encontrada.")
    customer = customer_for_access(db, promise.customer_id, user, write=True)
    promise.status = "Cumplida"
    db.add(ManagementActivity(tenant_id=customer.tenant_id, project_id=customer.project_id, customer_id=customer.id, user_id=user.id, channel="manual", result="Promesa cumplida", note="Promesa marcada como cumplida."))
    db.commit()
    return PromiseOut(id=promise.id, customer_id=customer.id, customer_name=customer.name, amount=promise.amount, due_date=promise.due_date, channel=promise.channel, status=promise.status, created_at=promise.created_at)
