from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.models import MenuItem, Tenant, TenantModule, User
from app.services.access_control import get_current_tenant, get_profile_role_code, is_company_admin, is_platform_admin, user_has_module, user_has_permission


AUDIENCE_BY_ROLE = {
    PLATFORM_ADMIN: "platform_admin",
    TENANT_ADMIN: "company_admin",
    COORDINATOR: "operational_leader",
    QUALITY_SUPERVISOR: "operational_leader",
    AGENT: "operational_user",
}

AUDIENCE_BY_PROFILE_ROLE = {
    "legal_director": "operational_leader",
    "lawyer": "operational_leader",
    "sales_leader": "operational_leader",
    "sales_advisor": "operational_leader",
    "collections_leader": "operational_leader",
    "collections_agent": "operational_user",
    "tenant_auditor": "operational_leader",
}

OPERATIONAL_SUPPORT_AUDIENCES = {"company_admin", "operational_leader", "operational_user"}


def user_audience(db: Session, user: User) -> str:
    profile_role_code = get_profile_role_code(db, user)
    if profile_role_code in AUDIENCE_BY_PROFILE_ROLE:
        return AUDIENCE_BY_PROFILE_ROLE[profile_role_code]
    return AUDIENCE_BY_ROLE.get(user.role, "operational_user")


def _audience_allowed(item_audience: str, user: User, db: Session, effective_audience: str | None = None) -> bool:
    if effective_audience:
        return item_audience == effective_audience
    if is_platform_admin(db, user):
        return item_audience == "platform_admin"
    if is_company_admin(db, user):
        return item_audience == "company_admin"
    if user_audience(db, user) == "operational_leader":
        return item_audience == "operational_leader"
    return item_audience == "operational_user"


def _support_tenant(db: Session, tenant_id: int | None) -> Tenant | None:
    if not tenant_id:
        return None
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa operativa no encontrada.")
    if tenant.slug == settings.platform_tenant_slug:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Selecciona una empresa cliente para entrar a operacion.")
    return tenant


def _support_module_allowed(db: Session, tenant_id: int, module_code: str) -> bool:
    if module_code in {"core", "administration"}:
        return True
    module_count = db.scalar(select(func.count(TenantModule.id)).where(TenantModule.tenant_id == tenant_id)) or 0
    if module_count == 0:
        return True
    module = db.scalar(select(TenantModule).where(TenantModule.tenant_id == tenant_id, TenantModule.module_code == module_code))
    return bool(module and module.is_enabled and module.enabled)


def build_menu(db: Session, user: User, operational_tenant_id: int | None = None, operational_audience: str | None = None) -> dict:
    tenant = get_current_tenant(db, user)
    support_mode = False
    support_audience: str | None = None
    if is_platform_admin(db, user) and operational_tenant_id:
        tenant = _support_tenant(db, operational_tenant_id)
        support_audience = operational_audience if operational_audience in OPERATIONAL_SUPPORT_AUDIENCES else "company_admin"
        support_mode = True
    items = list(db.scalars(select(MenuItem).where(MenuItem.is_active.is_(True)).order_by(MenuItem.order, MenuItem.label)))
    visible_items = []
    seen_sections = set()
    audience = support_audience or user_audience(db, user)
    for item in items:
        if item.route_name in seen_sections:
            continue
        if audience == "operational_user" and item.route_name in {"recordings", "uploads", "integrations"}:
            continue
        if not _audience_allowed(item.audience, user, db, support_audience):
            continue
        if item.module_code and support_mode and not _support_module_allowed(db, tenant.id, item.module_code):
            continue
        if item.module_code and not support_mode and not user_has_module(db, user, item.module_code, tenant.id):
            continue
        required_permission = item.required_permission or item.required_permission_code
        if required_permission and not user_has_permission(db, user, required_permission):
            continue
        visible_items.append(
            {
                "id": item.id,
                "label": item.label,
                "section": item.route_name,
                "url": item.url or f"#{item.route_name}",
                "icon": item.icon,
                "module_code": item.module_code,
                "audience": item.audience,
                "order": item.order,
            }
        )
        seen_sections.add(item.route_name)
    return {
        "product": {
            "name": "IEP",
            "tagline": "Icodeup Enterprise Platform",
        },
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "is_platform": tenant.slug == settings.platform_tenant_slug,
            "logo_url": tenant.logo_url,
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color,
            "timezone": tenant.timezone,
        },
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "profile_role": get_profile_role_code(db, user),
            "audience": audience,
            "base_audience": user_audience(db, user),
            "is_platform_admin": is_platform_admin(db, user),
            "is_company_admin": is_company_admin(db, user),
        },
        "items": visible_items,
        "support_context": {
            "enabled": support_mode,
            "tenant_id": tenant.id if support_mode else None,
            "tenant_name": tenant.name if support_mode else None,
            "audience": audience if support_mode else None,
            "base_role": user.role,
        },
    }


def public_branding(db: Session, slug: str | None = None) -> dict:
    tenant: Tenant | None = None
    if slug:
        tenant = db.scalar(select(Tenant).where(Tenant.slug == slug))
    return {
        "product_name": "IEP",
        "headline": "Icodeup Enterprise Platform",
        "subheadline": "Suite inteligente para operar empresas, datos, procesos y decisiones.",
        "tenant_name": tenant.name if tenant else None,
        "logo_url": tenant.logo_url if tenant else None,
        "primary_color": tenant.primary_color if tenant else "#15956f",
        "secondary_color": tenant.secondary_color if tenant else "#2563eb",
    }
