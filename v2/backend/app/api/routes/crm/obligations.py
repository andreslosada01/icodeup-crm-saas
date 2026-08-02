from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.roles import AGENT, COORDINATOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import Customer, CustomerObligation, User, UserProjectAssignment
from app.schemas.crm import CustomerObligationCreate, CustomerObligationOut, CustomerObligationPatch
from app.schemas.teams import ObligationAssignmentUpdate
from app.services.access_control import get_profile_role_code, require_permission
from app.services.audit_service import record_audit

from .access import customer_for_access, customer_query, is_platform, project_for_access, validate_assigned_user
from .utils import risk_from_dpd


router = APIRouter()


def _team_user_ids(db: Session, user: User) -> list[int]:
    ids = [user.id]
    ids.extend(db.scalars(select(User.id).where(User.tenant_id == user.tenant_id, User.leader_id == user.id)))
    return list(dict.fromkeys(ids))


def obligation_query(db: Session, user: User):
    query = select(CustomerObligation)
    if not is_platform(user):
        query = query.where(CustomerObligation.tenant_id == user.tenant_id)
    if user.role == TENANT_ADMIN:
        return query
    profile_role = get_profile_role_code(db, user)
    if user.role == COORDINATOR or profile_role == "collections_leader":
        team_ids = _team_user_ids(db, user)
        customer_ids = select(Customer.id).where(Customer.tenant_id == user.tenant_id, Customer.assigned_user_id.in_(team_ids))
        project_ids = list(
            db.scalars(
                select(UserProjectAssignment.project_id).where(
                    UserProjectAssignment.user_id == user.id,
                    UserProjectAssignment.is_active.is_(True),
                )
            )
        )
        conditions = [
            CustomerObligation.assigned_user_id.in_(team_ids),
            CustomerObligation.assigned_leader_id == user.id,
            CustomerObligation.customer_id.in_(customer_ids),
        ]
        if project_ids:
            conditions.append(CustomerObligation.project_id.in_(project_ids))
        return query.where(or_(*conditions))
    if user.role == AGENT:
        if profile_role in {"collections_leader", "sales_leader", "legal_director"}:
            query = query.where(
                CustomerObligation.assigned_user_id.in_(_team_user_ids(db, user))
                | CustomerObligation.assigned_leader_id.in_(_team_user_ids(db, user))
                | CustomerObligation.customer_id.in_(select(Customer.id).where(Customer.tenant_id == user.tenant_id, Customer.assigned_user_id.in_(_team_user_ids(db, user))))
            )
        elif profile_role not in {"sales_advisor", "lawyer"}:
            query = query.where(
                (CustomerObligation.assigned_user_id == user.id)
                | CustomerObligation.customer_id.in_(select(Customer.id).where(Customer.tenant_id == user.tenant_id, Customer.assigned_user_id == user.id))
            )
    return query


def obligation_for_access(db: Session, obligation_id: int, user: User, write: bool = False) -> CustomerObligation:
    obligation = db.get(CustomerObligation, obligation_id)
    if obligation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligacion no encontrada.")
    customer_for_access(db, obligation.customer_id, user, write=write)
    if user.role == AGENT and not write:
        profile_role = get_profile_role_code(db, user)
        if profile_role == "collections_agent" and obligation.assigned_user_id not in {None, user.id}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Obligacion fuera de tu asignacion.")
    return obligation


def obligation_to_out(db: Session, item: CustomerObligation) -> CustomerObligationOut:
    customer = db.get(Customer, item.customer_id)
    assigned = db.get(User, item.assigned_user_id) if item.assigned_user_id else None
    leader = db.get(User, item.assigned_leader_id) if item.assigned_leader_id else None
    return CustomerObligationOut(
        id=item.id,
        tenant_id=item.tenant_id,
        project_id=item.project_id,
        customer_id=item.customer_id,
        customer_name=customer.name if customer else None,
        obligation_number=item.obligation_number,
        product_type=item.product_type,
        portfolio_name=item.portfolio_name,
        purchase_number=item.purchase_number,
        original_amount=item.original_amount,
        original_balance=item.original_amount,
        current_balance=item.current_balance,
        priority=item.priority,
        capital_amount=item.capital_amount,
        interest_amount=item.interest_amount,
        fees_amount=item.fees_amount,
        days_past_due=item.days_past_due,
        status=item.status,
        risk=item.risk,
        due_date=item.due_date,
        assignment_date=item.assignment_date,
        assigned_user_id=item.assigned_user_id,
        assigned_user_name=assigned.name if assigned else None,
        assigned_leader_id=item.assigned_leader_id,
        assigned_leader_name=leader.name if leader else None,
        metadata_json=item.metadata_json,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/obligations", response_model=list[CustomerObligationOut])
def list_obligations(
    customer_id: int | None = None,
    project_id: int | None = None,
    assigned_user_id: int | None = None,
    q: str | None = None,
    limit: int = Query(default=10, ge=1, le=10),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[CustomerObligationOut]:
    require_permission(db, user, "crm.clients.view")
    query = obligation_query(db, user)
    if customer_id:
        query = query.where(CustomerObligation.customer_id == customer_id)
    if project_id:
        query = query.where(CustomerObligation.project_id == project_id)
    if assigned_user_id and user.role != AGENT:
        query = query.where(CustomerObligation.assigned_user_id == assigned_user_id)
    if q:
        pattern = f"%{q.lower()}%"
        query = query.where(func.lower(CustomerObligation.obligation_number).like(pattern) | func.lower(CustomerObligation.product_type).like(pattern))
    items = db.scalars(query.order_by(CustomerObligation.priority.desc(), CustomerObligation.days_past_due.desc(), CustomerObligation.current_balance.desc()).limit(limit))
    return [obligation_to_out(db, item) for item in items]


@router.get("/customers/{customer_id}/obligations", response_model=list[CustomerObligationOut])
def list_customer_obligations(customer_id: int, limit: int = Query(default=10, ge=1, le=10), db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[CustomerObligationOut]:
    require_permission(db, user, "crm.clients.view")
    customer_for_access(db, customer_id, user)
    items = db.scalars(obligation_query(db, user).where(CustomerObligation.customer_id == customer_id).order_by(CustomerObligation.priority.desc(), CustomerObligation.days_past_due.desc()).limit(limit))
    return [obligation_to_out(db, item) for item in items]


@router.post("/obligations", response_model=CustomerObligationOut, status_code=status.HTTP_201_CREATED)
def create_obligation(payload: CustomerObligationCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CustomerObligationOut:
    require_permission(db, user, "crm.clients.create")
    customer = customer_for_access(db, payload.customer_id, user, write=True)
    if payload.assigned_user_id:
        validate_assigned_user(db, customer.tenant_id, payload.assigned_user_id)
    if payload.assigned_leader_id:
        validate_assigned_user(db, customer.tenant_id, payload.assigned_leader_id)
    project_id = payload.project_id or customer.project_id
    if project_id:
        project = project_for_access(db, project_id, user)
        if project.tenant_id != customer.tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El proyecto no pertenece a la empresa del cliente.")
    original_amount = payload.original_balance if payload.original_balance is not None else payload.original_amount
    item = CustomerObligation(
        tenant_id=customer.tenant_id,
        project_id=project_id,
        customer_id=customer.id,
        obligation_number=payload.obligation_number,
        product_type=payload.product_type,
        portfolio_name=payload.portfolio_name,
        purchase_number=payload.purchase_number,
        original_amount=original_amount,
        current_balance=payload.current_balance,
        priority=payload.priority,
        capital_amount=payload.capital_amount,
        interest_amount=payload.interest_amount,
        fees_amount=payload.fees_amount,
        days_past_due=payload.days_past_due,
        status=payload.status,
        risk=payload.risk or risk_from_dpd(payload.days_past_due, payload.current_balance),
        due_date=payload.due_date,
        assignment_date=payload.assignment_date,
        assigned_user_id=payload.assigned_user_id or customer.assigned_user_id,
        assigned_leader_id=payload.assigned_leader_id,
        metadata_json=payload.metadata_json,
    )
    db.add(item)
    db.flush()
    record_audit(db, user, "customer_obligation", "create", item.id, item.tenant_id, module="collections", after={"customer_id": customer.id, "obligation_number": item.obligation_number})
    db.commit()
    db.refresh(item)
    return obligation_to_out(db, item)


@router.patch("/obligations/{obligation_id}", response_model=CustomerObligationOut)
def update_obligation(obligation_id: int, payload: CustomerObligationPatch, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CustomerObligationOut:
    require_permission(db, user, "crm.clients.update")
    item = obligation_for_access(db, obligation_id, user, write=True)
    updates = payload.model_dump(exclude_unset=True)
    if "assigned_user_id" in updates and updates["assigned_user_id"]:
        validate_assigned_user(db, item.tenant_id, updates["assigned_user_id"])
    if "assigned_leader_id" in updates and updates["assigned_leader_id"]:
        validate_assigned_user(db, item.tenant_id, updates["assigned_leader_id"])
    if "project_id" in updates and updates["project_id"]:
        project = project_for_access(db, updates["project_id"], user)
        if project.tenant_id != item.tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El proyecto no pertenece a la empresa de la obligacion.")
    if "original_balance" in updates:
        updates["original_amount"] = updates.pop("original_balance")
    for key, value in updates.items():
        setattr(item, key, value)
    if "risk" not in updates and ("days_past_due" in updates or "current_balance" in updates):
        item.risk = risk_from_dpd(item.days_past_due, item.current_balance)
    record_audit(db, user, "customer_obligation", "update", item.id, item.tenant_id, module="collections", after=updates)
    db.commit()
    db.refresh(item)
    return obligation_to_out(db, item)


@router.patch("/obligations/{obligation_id}/assignment", response_model=CustomerObligationOut)
def update_obligation_assignment(
    obligation_id: int,
    payload: ObligationAssignmentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> CustomerObligationOut:
    require_permission(db, user, "crm.assignments.manage")
    item = obligation_for_access(db, obligation_id, user, write=True)
    before = {
        "assigned_user_id": item.assigned_user_id,
        "assigned_leader_id": item.assigned_leader_id,
        "project_id": item.project_id,
    }
    if payload.project_id is not None:
        project = project_for_access(db, payload.project_id, user)
        if project.tenant_id != item.tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El proyecto no pertenece a la empresa de la obligacion.")
        item.project_id = project.id
    if payload.assigned_user_id is not None:
        validate_assigned_user(db, item.tenant_id, payload.assigned_user_id)
        item.assigned_user_id = payload.assigned_user_id
    if payload.assigned_leader_id is not None:
        validate_assigned_user(db, item.tenant_id, payload.assigned_leader_id)
        item.assigned_leader_id = payload.assigned_leader_id
    record_audit(
        db,
        user,
        "obligation_assignment",
        "update",
        item.id,
        item.tenant_id,
        module="collections",
        before=before,
        after={"assigned_user_id": item.assigned_user_id, "assigned_leader_id": item.assigned_leader_id, "project_id": item.project_id},
        request=request,
    )
    db.commit()
    db.refresh(item)
    return obligation_to_out(db, item)
