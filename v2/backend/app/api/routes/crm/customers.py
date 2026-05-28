from __future__ import annotations

import math

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.roles import AGENT
from app.db.session import get_db
from app.models import Customer, User
from app.schemas.crm import CustomerCreate, CustomerListResponse, CustomerOut
from app.services.audit_service import record_audit

from .access import customer_query, customer_to_out, ensure_manage_access, ensure_read_access, is_platform, project_for_access, validate_assigned_user
from .utils import next_action_for, priority_score, risk_from_dpd


router = APIRouter()


@router.get("/customers", response_model=CustomerListResponse)
def list_customers(
    q: str | None = None,
    tenant_id: int | None = None,
    project_id: int | None = None,
    assigned_user_id: int | None = None,
    status_value: str | None = Query(default=None, alias="status"),
    risk: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> CustomerListResponse:
    ensure_read_access(user)
    page = max(1, page)
    page_size = min(10, max(1, page_size))
    query = customer_query(db, user)
    if tenant_id and is_platform(user):
        query = query.where(Customer.tenant_id == tenant_id)
    if project_id:
        query = query.where(Customer.project_id == project_id)
    if assigned_user_id and user.role != AGENT:
        query = query.where(Customer.assigned_user_id == assigned_user_id)
    if status_value:
        query = query.where(Customer.status == status_value)
    if risk:
        query = query.where(Customer.risk == risk)
    if q:
        pattern = f"%{q.lower()}%"
        query = query.where(func.lower(Customer.name).like(pattern) | func.lower(Customer.document).like(pattern) | func.lower(Customer.phone).like(pattern))
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(db.scalars(query.order_by(Customer.priority.desc(), Customer.dpd.desc()).offset((page - 1) * page_size).limit(page_size)))
    return CustomerListResponse(
        items=[customer_to_out(db, item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.post("/customers", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CustomerOut:
    ensure_manage_access(user)
    project = project_for_access(db, payload.project_id, user)
    tenant_id = project.tenant_id
    validate_assigned_user(db, tenant_id, payload.assigned_user_id)
    risk = payload.risk or risk_from_dpd(payload.dpd, payload.balance)
    customer = Customer(
        tenant_id=tenant_id,
        project_id=project.id,
        assigned_user_id=payload.assigned_user_id,
        name=payload.name.strip(),
        document=payload.document.strip(),
        phone=payload.phone,
        email=payload.email,
        city=payload.city,
        segment=payload.segment,
        obligation=payload.obligation,
        balance=payload.balance,
        original_balance=payload.original_balance or payload.balance,
        dpd=payload.dpd,
        status=payload.status,
        risk=risk,
        priority=priority_score(payload.dpd, payload.balance, risk, payload.status),
        next_action=next_action_for(payload.status, risk),
        contactability=payload.contactability,
        notes=payload.notes,
        next_contact_at=payload.next_contact_at,
    )
    db.add(customer)
    db.flush()
    record_audit(db, user, "customer", "create", customer.id, customer.tenant_id, after={"name": customer.name, "document": customer.document})
    db.commit()
    db.refresh(customer)
    return customer_to_out(db, customer)
