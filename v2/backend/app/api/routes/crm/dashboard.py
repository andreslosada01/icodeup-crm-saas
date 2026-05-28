from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Customer, Payment, PaymentPromise, Project, User
from app.schemas.crm import DashboardMetrics
from app.services.access_control import require_permission

from .access import customer_query, ensure_read_access, is_platform


router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard(
    tenant_id: int | None = None,
    project_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> DashboardMetrics:
    require_permission(db, user, "crm.dashboard.view")
    ensure_read_access(user)
    query = customer_query(db, user)
    if tenant_id and is_platform(user):
        query = query.where(Customer.tenant_id == tenant_id)
    if project_id:
        query = query.where(Customer.project_id == project_id)
    customers = list(db.scalars(query))
    customer_ids = [customer.id for customer in customers]
    payments = list(db.scalars(select(Payment).where(Payment.customer_id.in_(customer_ids)))) if customer_ids else []
    promises = list(db.scalars(select(PaymentPromise).where(PaymentPromise.customer_id.in_(customer_ids)))) if customer_ids else []
    now = datetime.now(timezone.utc)
    active_promises = [item for item in promises if item.status == "Vigente"]
    overdue_promises = [item for item in active_promises if item.due_date < now]
    due_today = [item for item in customers if item.next_contact_at and item.next_contact_at.date() <= now.date()]
    risk_distribution = {risk: len([item for item in customers if item.risk == risk]) for risk in ["Alto", "Medio", "Bajo"]}
    statuses = sorted({item.status for item in customers})
    status_distribution = {status_value: len([item for item in customers if item.status == status_value]) for status_value in statuses}
    project_rows = []
    for project in db.scalars(select(Project).order_by(Project.name)):
        project_customers = [item for item in customers if item.project_id == project.id]
        if project_customers:
            project_payments = [item for item in payments if item.project_id == project.id]
            project_rows.append(
                {
                    "project": project.name,
                    "customers": len(project_customers),
                    "balance": sum(item.balance for item in project_customers),
                    "recovered": sum(item.amount for item in project_payments),
                }
            )
    return DashboardMetrics(
        customers=len(customers),
        total_balance=sum(item.balance for item in customers),
        recovered=sum(item.amount for item in payments),
        active_promises=len(active_promises),
        promise_value=sum(item.amount for item in active_promises),
        contact_rate=round((len([item for item in customers if item.status != "Sin contacto"]) / max(len(customers), 1)) * 100),
        high_risk=len([item for item in customers if item.risk == "Alto"]),
        overdue_promises=len(overdue_promises),
        due_today=len(due_today),
        risk_distribution=risk_distribution,
        status_distribution=status_distribution,
        recovery_by_project=project_rows,
    )
