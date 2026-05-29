from __future__ import annotations

import math
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Customer, Document, Project, SaasPlan, TenantSubscription, User
from app.services.audit_service import record_audit


ACTIVE_SUBSCRIPTION_STATUSES = {"trial", "active"}


def get_active_subscription(db: Session, tenant_id: int) -> TenantSubscription | None:
    return db.scalar(
        select(TenantSubscription)
        .where(
            TenantSubscription.tenant_id == tenant_id,
            TenantSubscription.status.in_(ACTIVE_SUBSCRIPTION_STATUSES),
        )
        .order_by(TenantSubscription.created_at.desc())
    )


def get_active_plan(db: Session, tenant_id: int) -> SaasPlan | None:
    subscription = get_active_subscription(db, tenant_id)
    if not subscription:
        return None
    return db.get(SaasPlan, subscription.plan_id)


def get_tenant_usage(db: Session, tenant_id: int) -> dict[str, int]:
    storage_bytes = db.scalar(select(func.coalesce(func.sum(Document.size_bytes), 0)).where(Document.tenant_id == tenant_id)) or 0
    return {
        "users": db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant_id)) or 0,
        "projects": db.scalar(select(func.count(Project.id)).where(Project.tenant_id == tenant_id)) or 0,
        "customers": db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == tenant_id)) or 0,
        "storage_mb": math.ceil(storage_bytes / (1024 * 1024)) if storage_bytes else 0,
    }


def _legacy_allow(db: Session, tenant_id: int, limit_type: str, user: User | None) -> bool:
    if user:
        record_audit(
            db,
            user,
            "plan_limit",
            "legacy_allow",
            tenant_id,
            tenant_id,
            module="subscriptions",
            after={"limit_type": limit_type, "reason": "tenant_without_active_subscription_or_plan"},
        )
    return True


def enforce_or_allow_legacy(db: Session, tenant_id: int, limit_type: str, user: User | None = None) -> SaasPlan | None:
    plan = get_active_plan(db, tenant_id)
    if plan is None:
        _legacy_allow(db, tenant_id, limit_type, user)
        return None
    return plan


def _check_limit(limit_value: int, current_value: int, increment: int, label: str) -> None:
    if limit_value == 0:
        return
    if current_value + increment > limit_value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Limite de plan excedido para {label}: {current_value + increment}/{limit_value}.",
        )


def _safe_increment(value: int | float) -> int:
    return max(0, math.ceil(value))


def check_user_limit(db: Session, tenant_id: int, increment: int = 1, user: User | None = None) -> bool:
    plan = enforce_or_allow_legacy(db, tenant_id, "users", user)
    if not plan:
        return True
    usage = get_tenant_usage(db, tenant_id)
    _check_limit(plan.max_users, usage["users"], _safe_increment(increment), "usuarios")
    return True


def check_project_limit(db: Session, tenant_id: int, increment: int = 1, user: User | None = None) -> bool:
    plan = enforce_or_allow_legacy(db, tenant_id, "projects", user)
    if not plan:
        return True
    usage = get_tenant_usage(db, tenant_id)
    _check_limit(plan.max_projects, usage["projects"], _safe_increment(increment), "proyectos")
    return True


def check_customer_limit(db: Session, tenant_id: int, increment: int = 1, user: User | None = None) -> bool:
    plan = enforce_or_allow_legacy(db, tenant_id, "customers", user)
    if not plan:
        return True
    usage = get_tenant_usage(db, tenant_id)
    effective_limit = plan.max_customers or plan.max_records
    _check_limit(effective_limit, usage["customers"], _safe_increment(increment), "clientes")
    return True


def check_storage_limit(db: Session, tenant_id: int, additional_mb: int | float = 0, user: User | None = None) -> bool:
    plan = enforce_or_allow_legacy(db, tenant_id, "storage_mb", user)
    if not plan:
        return True
    usage = get_tenant_usage(db, tenant_id)
    _check_limit(plan.max_storage_mb, usage["storage_mb"], _safe_increment(additional_mb), "almacenamiento MB")
    return True


def plan_limit_snapshot(db: Session, tenant_id: int) -> dict[str, Any]:
    plan = get_active_plan(db, tenant_id)
    usage = get_tenant_usage(db, tenant_id)
    return {
        "tenant_id": tenant_id,
        "plan": plan.code if plan else None,
        "limits": {
            "max_users": plan.max_users if plan else None,
            "max_projects": plan.max_projects if plan else None,
            "max_customers": plan.max_customers if plan else None,
            "max_records": plan.max_records if plan else None,
            "max_storage_mb": plan.max_storage_mb if plan else None,
        },
        "usage": usage,
        "legacy_allowed": plan is None,
    }
