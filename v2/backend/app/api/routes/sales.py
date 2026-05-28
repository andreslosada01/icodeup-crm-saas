from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.routes.crm.access import customer_for_access, is_platform, project_for_access, validate_assigned_user
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, TENANT_ADMIN
from app.db.session import get_db
from app.models import Customer, Lead, Opportunity, User
from app.schemas.sales import LeadCreate, LeadOut, LeadPatch, OpportunityCreate, OpportunityOut, OpportunityPatch
from app.services.audit_service import record_audit
from app.services.access_control import require_active_module, require_permission


router = APIRouter(dependencies=[Depends(require_active_module("sales"))])
SALES_MANAGE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}
SALES_READ_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, AGENT}


def ensure_sales_read(user: User) -> None:
    if user.role not in SALES_READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso comercial.")


def ensure_sales_manage(user: User) -> None:
    if user.role not in SALES_MANAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso para gestionar ventas.")


def tenant_from_payload(payload_tenant_id: int | None, user: User) -> int:
    return payload_tenant_id if is_platform(user) and payload_tenant_id else user.tenant_id


def validate_sales_project_and_user(db: Session, tenant_id: int, project_id: int | None, assigned_user_id: int | None, user: User) -> None:
    if project_id:
        project = project_for_access(db, project_id, user)
        if project.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Proyecto fuera de la empresa.")
    validate_assigned_user(db, tenant_id, assigned_user_id)


def lead_for_access(db: Session, lead_id: int, user: User, write: bool = False) -> Lead:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead no encontrado.")
    if not is_platform(user) and lead.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lead fuera de tu empresa.")
    if user.role == AGENT and lead.assigned_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lead no asignado.")
    if write:
        ensure_sales_manage(user)
    return lead


def opportunity_for_access(db: Session, opportunity_id: int, user: User, write: bool = False) -> Opportunity:
    opportunity = db.get(Opportunity, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oportunidad no encontrada.")
    if not is_platform(user) and opportunity.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Oportunidad fuera de tu empresa.")
    if user.role == AGENT and opportunity.assigned_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Oportunidad no asignada.")
    if write:
        ensure_sales_manage(user)
    return opportunity


@router.get("/leads", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[Lead]:
    require_permission(db, user, "sales.leads.view")
    ensure_sales_read(user)
    query = select(Lead).order_by(Lead.created_at.desc())
    if not is_platform(user):
        query = query.where(Lead.tenant_id == user.tenant_id)
    if user.role == AGENT:
        query = query.where(Lead.assigned_user_id == user.id)
    return list(db.scalars(query))


@router.post("/leads", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Lead:
    require_permission(db, user, "sales.leads.create")
    ensure_sales_manage(user)
    tenant_id = tenant_from_payload(payload.tenant_id, user)
    validate_sales_project_and_user(db, tenant_id, payload.project_id, payload.assigned_user_id, user)
    lead = Lead(tenant_id=tenant_id, **payload.model_dump(exclude={"tenant_id"}))
    db.add(lead)
    db.flush()
    record_audit(db, user, "lead", "create", lead.id, lead.tenant_id, after={"name": lead.name, "status": lead.status})
    db.commit()
    db.refresh(lead)
    return lead


@router.patch("/leads/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, payload: LeadPatch, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Lead:
    require_permission(db, user, "sales.leads.update")
    lead = lead_for_access(db, lead_id, user, write=True)
    updates = payload.model_dump(exclude_unset=True)
    if "project_id" in updates or "assigned_user_id" in updates:
        validate_sales_project_and_user(db, lead.tenant_id, updates.get("project_id", lead.project_id), updates.get("assigned_user_id", lead.assigned_user_id), user)
    for field, value in updates.items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/opportunities", response_model=list[OpportunityOut])
def list_opportunities(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[Opportunity]:
    require_permission(db, user, "sales.opportunities.view")
    ensure_sales_read(user)
    query = select(Opportunity).order_by(Opportunity.created_at.desc())
    if not is_platform(user):
        query = query.where(Opportunity.tenant_id == user.tenant_id)
    if user.role == AGENT:
        query = query.where(Opportunity.assigned_user_id == user.id)
    return list(db.scalars(query))


@router.post("/opportunities", response_model=OpportunityOut, status_code=status.HTTP_201_CREATED)
def create_opportunity(payload: OpportunityCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Opportunity:
    require_permission(db, user, "sales.opportunities.create")
    ensure_sales_manage(user)
    tenant_id = tenant_from_payload(payload.tenant_id, user)
    validate_assigned_user(db, tenant_id, payload.assigned_user_id)
    if payload.lead_id:
        lead = lead_for_access(db, payload.lead_id, user)
        if lead.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Lead fuera de la empresa.")
    if payload.customer_id:
        customer = customer_for_access(db, payload.customer_id, user)
        if customer.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente fuera de la empresa.")
    opportunity = Opportunity(tenant_id=tenant_id, **payload.model_dump(exclude={"tenant_id"}))
    db.add(opportunity)
    db.flush()
    record_audit(db, user, "opportunity", "create", opportunity.id, opportunity.tenant_id, after={"name": opportunity.name, "stage": opportunity.stage})
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.patch("/opportunities/{opportunity_id}", response_model=OpportunityOut)
def update_opportunity(opportunity_id: int, payload: OpportunityPatch, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Opportunity:
    require_permission(db, user, "sales.opportunities.update")
    opportunity = opportunity_for_access(db, opportunity_id, user, write=True)
    updates = payload.model_dump(exclude_unset=True)
    if "assigned_user_id" in updates:
        validate_assigned_user(db, opportunity.tenant_id, updates["assigned_user_id"])
    if "lead_id" in updates and updates["lead_id"]:
        lead = lead_for_access(db, updates["lead_id"], user)
        if lead.tenant_id != opportunity.tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Lead fuera de la empresa.")
    if "customer_id" in updates and updates["customer_id"]:
        customer = customer_for_access(db, updates["customer_id"], user)
        if customer.tenant_id != opportunity.tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente fuera de la empresa.")
    for field, value in updates.items():
        setattr(opportunity, field, value)
    db.commit()
    db.refresh(opportunity)
    return opportunity
