from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.models import MenuItem, Tenant, User
from app.services.access_control import get_current_tenant, is_company_admin, is_platform_admin, user_has_module, user_has_permission


AUDIENCE_BY_ROLE = {
    PLATFORM_ADMIN: "platform_admin",
    TENANT_ADMIN: "company_admin",
    COORDINATOR: "operational_leader",
    QUALITY_SUPERVISOR: "operational_leader",
    AGENT: "operational_user",
}


def user_audience(user: User) -> str:
    return AUDIENCE_BY_ROLE.get(user.role, "operational_user")


def _audience_allowed(item_audience: str, user: User, db: Session) -> bool:
    if is_platform_admin(db, user):
        return item_audience == "platform_admin"
    if is_company_admin(db, user):
        return item_audience == "company_admin"
    if user.role in {COORDINATOR, QUALITY_SUPERVISOR}:
        return item_audience == "operational_leader"
    return item_audience == "operational_user"


def build_menu(db: Session, user: User) -> dict:
    tenant = get_current_tenant(db, user)
    items = list(db.scalars(select(MenuItem).where(MenuItem.is_active.is_(True)).order_by(MenuItem.order, MenuItem.label)))
    visible_items = []
    seen_sections = set()
    for item in items:
        if item.route_name in seen_sections:
            continue
        if not _audience_allowed(item.audience, user, db):
            continue
        if item.module_code and not user_has_module(db, user, item.module_code, tenant.id):
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
            "name": "Icodeup 360",
            "tagline": "Plataforma Inteligente de Operaciones Empresariales",
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
            "audience": user_audience(user),
            "is_platform_admin": is_platform_admin(db, user),
            "is_company_admin": is_company_admin(db, user),
        },
        "items": visible_items,
    }


def public_branding(db: Session, slug: str | None = None) -> dict:
    tenant: Tenant | None = None
    if slug:
        tenant = db.scalar(select(Tenant).where(Tenant.slug == slug))
    return {
        "product_name": "Icodeup 360",
        "headline": "Plataforma Inteligente de Operaciones Empresariales",
        "subheadline": "Operacion, datos, modulos y decisiones en una experiencia SaaS segura.",
        "tenant_name": tenant.name if tenant else None,
        "logo_url": tenant.logo_url if tenant else None,
        "primary_color": tenant.primary_color if tenant else "#15956f",
        "secondary_color": tenant.secondary_color if tenant else "#2563eb",
    }
