from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.models import AuditLog, Customer, LegalCase, Module, Payment, PaymentPromise, Project, Tenant, TenantModule, TenantSubscription, User
from app.services.access_control import get_current_tenant, is_company_admin, is_platform_admin


def _card(label: str, value: int | str, detail: str, tone: str = "neutral") -> dict:
    return {"label": label, "value": value, "detail": detail, "tone": tone}


def role_dashboard(db: Session, user: User) -> dict:
    if is_platform_admin(db, user):
        return platform_dashboard(db, user)
    if is_company_admin(db, user):
        return company_admin_dashboard(db, user)
    if user.role in {COORDINATOR, QUALITY_SUPERVISOR}:
        return leader_dashboard(db, user)
    return operational_dashboard(db, user)


def platform_dashboard(db: Session, user: User) -> dict:
    tenant_scope = Tenant.slug != settings.platform_tenant_slug
    active_tenants = db.scalar(select(func.count(Tenant.id)).where(tenant_scope, Tenant.status == "active")) or 0
    subscriptions = db.scalar(select(func.count(TenantSubscription.id)).where(TenantSubscription.status.in_(["trial", "active"]))) or 0
    active_users = db.scalar(select(func.count(User.id)).where(User.status == "active")) or 0
    active_modules = db.scalar(select(func.count(TenantModule.id)).where(TenantModule.is_enabled.is_(True), TenantModule.enabled.is_(True))) or 0
    recent_audit = db.scalar(select(func.count(AuditLog.id))) or 0
    return {
        "audience": "platform_admin",
        "title": "Gobierno SaaS Icodeup 360",
        "generated_at": datetime.now(timezone.utc),
        "cards": [
            _card("Empresas activas", active_tenants, "Tenants cliente operativos.", "green"),
            _card("Suscripciones", subscriptions, "Contratos trial o activos.", "blue"),
            _card("Usuarios activos", active_users, "Usuarios disponibles en plataforma.", "neutral"),
            _card("Modulos habilitados", active_modules, "Activaciones por empresa.", "yellow"),
        ],
        "alerts": [
            {"title": "Auditoria disponible", "body": f"{recent_audit} eventos trazados en el log corporativo.", "tone": "green"},
            {"title": "Shared schema activo", "body": "La separacion se controla por tenant_id en las rutas operativas.", "tone": "blue"},
        ],
    }


def company_admin_dashboard(db: Session, user: User) -> dict:
    tenant = get_current_tenant(db, user)
    users = db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant.id)) or 0
    projects = db.scalar(select(func.count(Project.id)).where(Project.tenant_id == tenant.id)) or 0
    customers = db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == tenant.id)) or 0
    modules = db.scalar(select(func.count(TenantModule.id)).where(TenantModule.tenant_id == tenant.id, TenantModule.is_enabled.is_(True), TenantModule.enabled.is_(True))) or 0
    return {
        "audience": "company_admin",
        "title": f"Inicio empresa - {tenant.name}",
        "generated_at": datetime.now(timezone.utc),
        "cards": [
            _card("Usuarios", users, "Usuarios de tu empresa.", "blue"),
            _card("Proyectos", projects, "Workspaces o carteras activas.", "green"),
            _card("Registros operativos", customers, "Clientes/terceros operativos actuales.", "neutral"),
            _card("Modulos activos", modules, "Capacidades habilitadas por licencia.", "yellow"),
        ],
        "alerts": [
            {"title": "Administracion aislada", "body": "Tu administracion se limita a la empresa autenticada.", "tone": "green"},
        ],
    }


def leader_dashboard(db: Session, user: User) -> dict:
    tenant = get_current_tenant(db, user)
    team_ids = [item.id for item in db.scalars(select(User).where(User.tenant_id == tenant.id, User.leader_id == user.id))]
    visible_user_ids = team_ids or [user.id]
    assigned = db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == tenant.id, Customer.assigned_user_id.in_(visible_user_ids))) or 0
    promises = db.scalar(select(func.count(PaymentPromise.id)).where(PaymentPromise.tenant_id == tenant.id, PaymentPromise.user_id.in_(visible_user_ids))) or 0
    payments = db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.tenant_id == tenant.id, Payment.user_id.in_(visible_user_ids))) or 0
    legal = db.scalar(select(func.count(LegalCase.id)).where(LegalCase.tenant_id == tenant.id)) or 0
    return {
        "audience": "operational_leader",
        "title": "Panel lider operativo",
        "generated_at": datetime.now(timezone.utc),
        "cards": [
            _card("Equipo directo", len(team_ids), "Usuarios bajo liderazgo directo.", "blue"),
            _card("Casos asignados", assigned, "Clientes bajo gestion del equipo.", "green"),
            _card("Promesas", promises, "Compromisos creados por el equipo.", "yellow"),
            _card("Recuperado", int(payments), "Pagos registrados por el equipo.", "green"),
        ],
        "alerts": [
            {"title": "Casos juridicos", "body": f"{legal} expedientes juridicos visibles en tu empresa.", "tone": "neutral"},
        ],
    }


def operational_dashboard(db: Session, user: User) -> dict:
    tenant = get_current_tenant(db, user)
    assigned = db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == tenant.id, Customer.assigned_user_id == user.id)) or 0
    promises = db.scalar(select(func.count(PaymentPromise.id)).where(PaymentPromise.tenant_id == tenant.id, PaymentPromise.user_id == user.id, PaymentPromise.status == "Vigente")) or 0
    payments = db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.tenant_id == tenant.id, Payment.user_id == user.id)) or 0
    return {
        "audience": "operational_user",
        "title": "Mi operacion",
        "generated_at": datetime.now(timezone.utc),
        "cards": [
            _card("Mis casos", assigned, "Clientes asignados a tu usuario.", "blue"),
            _card("Promesas vigentes", promises, "Compromisos abiertos.", "yellow"),
            _card("Recuperado", int(payments), "Pagos registrados por tu usuario.", "green"),
        ],
        "alerts": [
            {"title": "Acceso controlado", "body": "Solo ves la operacion permitida por tu rol y empresa.", "tone": "green"},
        ],
    }
