from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.routes.crm.access import customer_for_access, is_platform, project_for_access, validate_assigned_user
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, TENANT_ADMIN
from app.db.session import get_db
from app.models import Customer, Lead, Opportunity, User, WorkflowDefinition, WorkflowStage
from app.schemas.sales import LeadCreate, LeadOut, LeadPatch, OpportunityCreate, OpportunityOut, OpportunityPatch
from app.services.audit_service import record_audit
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin, require_active_module, require_permission, user_has_permission


router = APIRouter(dependencies=[Depends(require_active_module("sales"))])
SALES_MANAGE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}
SALES_READ_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, AGENT}
DEFAULT_SALES_STAGES = [
    {"code": "new", "name": "Nuevo", "color": "#64748b", "order": 10},
    {"code": "contacted", "name": "Contactado", "color": "#2563eb", "order": 20},
    {"code": "proposal", "name": "Propuesta", "color": "#7c3aed", "order": 30},
    {"code": "negotiation", "name": "Negociacion", "color": "#f59e0b", "order": 40},
    {"code": "closed_won", "name": "Ganado", "color": "#16a34a", "order": 50},
    {"code": "closed_lost", "name": "Perdido", "color": "#dc2626", "order": 60},
]


def _norm(value: str | None) -> str:
    return (value or "").strip().lower().replace("_", " ").replace("-", " ")


def sales_stages(db: Session, tenant_id: int | None) -> list[dict]:
    workflow = None
    if tenant_id:
        workflow = db.scalar(select(WorkflowDefinition).where(WorkflowDefinition.module == "sales", WorkflowDefinition.tenant_id == tenant_id, WorkflowDefinition.is_active.is_(True)).order_by(WorkflowDefinition.id.desc()))
    workflow = workflow or db.scalar(select(WorkflowDefinition).where(WorkflowDefinition.module == "sales", WorkflowDefinition.tenant_id.is_(None), WorkflowDefinition.is_active.is_(True)).order_by(WorkflowDefinition.id.desc()))
    if not workflow:
        return DEFAULT_SALES_STAGES
    stages = list(db.scalars(select(WorkflowStage).where(WorkflowStage.workflow_id == workflow.id, WorkflowStage.is_active.is_(True)).order_by(WorkflowStage.order, WorkflowStage.name)))
    return [{"code": stage.code.lower(), "name": stage.name, "color": stage.color, "order": stage.order, "is_final": stage.is_final} for stage in stages] or DEFAULT_SALES_STAGES


def ensure_sales_read(db: Session, user: User) -> None:
    if user_has_permission(db, user, "sales.leads.view") or user_has_permission(db, user, "sales.opportunities.view"):
        return
    if user.role not in SALES_READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso comercial.")


def ensure_sales_manage(db: Session, user: User) -> None:
    if (
        user_has_permission(db, user, "sales.leads.create")
        or user_has_permission(db, user, "sales.leads.update")
        or user_has_permission(db, user, "sales.opportunities.create")
        or user_has_permission(db, user, "sales.opportunities.update")
    ):
        return
    if user.role not in SALES_MANAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso para gestionar ventas.")


def sales_assigned_only(db: Session, user: User) -> bool:
    profile_role = get_profile_role_code(db, user)
    if is_platform_admin(db, user) or is_company_admin(db, user):
        return False
    if profile_role == "sales_leader":
        return False
    return user.role == AGENT or profile_role == "sales_advisor"


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
    if sales_assigned_only(db, user) and lead.assigned_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lead no asignado.")
    if write:
        ensure_sales_manage(db, user)
    return lead


def opportunity_for_access(db: Session, opportunity_id: int, user: User, write: bool = False) -> Opportunity:
    opportunity = db.get(Opportunity, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oportunidad no encontrada.")
    if not is_platform(user) and opportunity.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Oportunidad fuera de tu empresa.")
    if sales_assigned_only(db, user) and opportunity.assigned_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Oportunidad no asignada.")
    if write:
        ensure_sales_manage(db, user)
    return opportunity


@router.get("/dashboard")
def sales_dashboard(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "sales.leads.view")
    ensure_sales_read(db, user)
    leads = list_leads(tenant_id=tenant_id, db=db, user=user, limit=10)
    opportunities = list_opportunities(tenant_id=tenant_id, db=db, user=user, limit=10) if user_has_permission(db, user, "sales.opportunities.view") else []
    open_opportunities = [item for item in opportunities if item.status in {"open", "active"}]
    won = [item for item in opportunities if item.status in {"won", "closed_won"} or item.stage in {"closed_won", "won"}]
    lost = [item for item in opportunities if item.status in {"lost", "closed_lost"} or item.stage in {"closed_lost", "lost"}]
    value_pipeline = sum(item.amount for item in open_opportunities)
    weighted_pipeline = sum(int(item.amount * (item.probability / 100)) for item in open_opportunities)
    by_stage: dict[str, dict] = {}
    for item in opportunities:
        stage = item.stage or item.status
        bucket = by_stage.setdefault(stage, {"stage": stage, "count": 0, "amount": 0})
        bucket["count"] += 1
        bucket["amount"] += item.amount
    return {
        "kpis": {
            "active_leads": len([item for item in leads if item.status not in {"lost", "closed", "won"}]),
            "open_opportunities": len(open_opportunities),
            "pipeline_value": value_pipeline,
            "weighted_pipeline": weighted_pipeline,
            "won_opportunities": len(won),
            "lost_opportunities": len(lost),
            "estimated_rate": round((len(won) / max(len(won) + len(lost), 1)) * 100),
        },
        "by_stage": list(by_stage.values()),
        "top_opportunities": [
            {"id": item.id, "name": item.name, "amount": item.amount, "stage": item.stage, "probability": item.probability, "expected_close_date": item.expected_close_date}
            for item in sorted(open_opportunities, key=lambda row: row.amount, reverse=True)[:8]
        ],
    }


@router.get("/pipeline")
def sales_pipeline(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "sales.opportunities.view")
    ensure_sales_read(db, user)
    opportunities = list_opportunities(tenant_id=tenant_id, db=db, user=user, limit=10)
    stages = sales_stages(db, tenant_id if is_platform_admin(db, user) and tenant_id else user.tenant_id if not is_platform_admin(db, user) else None)
    rows = []
    for stage in stages:
        stage_code = _norm(stage["code"])
        stage_name = _norm(stage["name"])
        items = [item for item in opportunities if _norm(item.stage) in {stage_code, stage_name}]
        rows.append(
            {
                "stage": stage,
                "count": len(items),
                "amount": sum(item.amount for item in items),
                "weighted_amount": sum(int(item.amount * (item.probability / 100)) for item in items),
                "probability_avg": round(sum(item.probability for item in items) / max(len(items), 1)),
            }
        )
    return {"stages": rows}


@router.get("/kanban")
def sales_kanban(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "sales.opportunities.view")
    ensure_sales_read(db, user)
    opportunities = list_opportunities(tenant_id=tenant_id, db=db, user=user, limit=10)
    stages = sales_stages(db, tenant_id if is_platform_admin(db, user) and tenant_id else user.tenant_id if not is_platform_admin(db, user) else None)
    columns = []
    for stage in stages:
        stage_code = _norm(stage["code"])
        stage_name = _norm(stage["name"])
        items = [
            {
                "id": item.id,
                "name": item.name,
                "amount": item.amount,
                "probability": item.probability,
                "expected_close_date": item.expected_close_date,
                "assigned_user_id": item.assigned_user_id,
                "status": item.status,
            }
            for item in opportunities
            if _norm(item.stage) in {stage_code, stage_name}
        ]
        columns.append({"stage": stage, "count": len(items), "amount": sum(item["amount"] for item in items), "items": items[:20]})
    return {"columns": columns}


@router.get("/leads", response_model=list[LeadOut])
def list_leads(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user), limit: int = Query(default=10, ge=1, le=10)) -> list[Lead]:
    require_permission(db, user, "sales.leads.view")
    ensure_sales_read(db, user)
    query = select(Lead).order_by(Lead.created_at.desc())
    if is_platform(user):
        if tenant_id:
            query = query.where(Lead.tenant_id == tenant_id)
    else:
        query = query.where(Lead.tenant_id == user.tenant_id)
    if sales_assigned_only(db, user):
        query = query.where(Lead.assigned_user_id == user.id)
    return list(db.scalars(query.limit(limit)))


@router.post("/leads", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Lead:
    require_permission(db, user, "sales.leads.create")
    ensure_sales_manage(db, user)
    tenant_id = tenant_from_payload(payload.tenant_id, user)
    assigned_user_id = payload.assigned_user_id or (user.id if sales_assigned_only(db, user) else None)
    validate_sales_project_and_user(db, tenant_id, payload.project_id, assigned_user_id, user)
    lead = Lead(tenant_id=tenant_id, **payload.model_dump(exclude={"tenant_id", "assigned_user_id"}), assigned_user_id=assigned_user_id)
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
    record_audit(db, user, "lead", "update", lead.id, lead.tenant_id, after=updates)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/opportunities", response_model=list[OpportunityOut])
def list_opportunities(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user), limit: int = Query(default=10, ge=1, le=10)) -> list[Opportunity]:
    require_permission(db, user, "sales.opportunities.view")
    ensure_sales_read(db, user)
    query = select(Opportunity).order_by(Opportunity.created_at.desc())
    if is_platform(user):
        if tenant_id:
            query = query.where(Opportunity.tenant_id == tenant_id)
    else:
        query = query.where(Opportunity.tenant_id == user.tenant_id)
    if sales_assigned_only(db, user):
        query = query.where(Opportunity.assigned_user_id == user.id)
    return list(db.scalars(query.limit(limit)))


@router.post("/opportunities", response_model=OpportunityOut, status_code=status.HTTP_201_CREATED)
def create_opportunity(payload: OpportunityCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Opportunity:
    require_permission(db, user, "sales.opportunities.create")
    ensure_sales_manage(db, user)
    tenant_id = tenant_from_payload(payload.tenant_id, user)
    assigned_user_id = payload.assigned_user_id or (user.id if sales_assigned_only(db, user) else None)
    validate_assigned_user(db, tenant_id, assigned_user_id)
    if payload.lead_id:
        lead = lead_for_access(db, payload.lead_id, user)
        if lead.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Lead fuera de la empresa.")
    if payload.customer_id:
        customer = customer_for_access(db, payload.customer_id, user)
        if customer.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente fuera de la empresa.")
    opportunity = Opportunity(tenant_id=tenant_id, **payload.model_dump(exclude={"tenant_id", "assigned_user_id"}), assigned_user_id=assigned_user_id)
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
    record_audit(db, user, "opportunity", "update", opportunity.id, opportunity.tenant_id, after=updates)
    db.commit()
    db.refresh(opportunity)
    return opportunity
