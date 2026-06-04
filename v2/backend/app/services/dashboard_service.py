from __future__ import annotations

from datetime import datetime, time, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.models import AuditLog, Customer, CustomerObligation, Document, Lead, LegalCase, ManagementActivity, Opportunity, Payment, PaymentAgreement, PaymentPromise, Project, Tenant, TenantModule, TenantSubscription, User
from app.services.access_control import get_current_tenant, get_profile_role_code, is_company_admin, is_platform_admin


def _card(label: str, value: int | str, detail: str, tone: str = "neutral") -> dict:
    return {"label": label, "value": value, "detail": detail, "tone": tone}


def role_dashboard(db: Session, user: User) -> dict:
    if is_platform_admin(db, user):
        return platform_dashboard(db, user)
    if is_company_admin(db, user):
        return company_admin_dashboard(db, user)
    profile_role = get_profile_role_code(db, user)
    if profile_role in {"legal_director", "lawyer"}:
        return legal_profile_dashboard(db, user, profile_role)
    if profile_role in {"sales_leader", "sales_advisor"}:
        return sales_profile_dashboard(db, user, profile_role)
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
    today_start = datetime.combine(datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc)
    month_start = datetime(datetime.now(timezone.utc).year, datetime.now(timezone.utc).month, 1, tzinfo=timezone.utc)
    customer_ids = select(Customer.id).where(Customer.tenant_id == tenant.id, Customer.assigned_user_id.in_(visible_user_ids))
    assigned = db.scalar(select(func.count(Customer.id)).where(Customer.id.in_(customer_ids))) or 0
    obligation_query = select(CustomerObligation).where(
        CustomerObligation.tenant_id == tenant.id,
        (
            CustomerObligation.assigned_user_id.in_(visible_user_ids)
            | (CustomerObligation.assigned_leader_id == user.id)
            | CustomerObligation.customer_id.in_(customer_ids)
        ),
    )
    obligation_scope = obligation_query.subquery()
    obligations = db.scalar(select(func.count()).select_from(obligation_scope)) or 0
    balance = db.scalar(select(func.coalesce(func.sum(obligation_scope.c.current_balance), 0))) or 0
    activities_today = db.scalar(select(func.count(ManagementActivity.id)).where(ManagementActivity.tenant_id == tenant.id, ManagementActivity.user_id.in_(visible_user_ids), ManagementActivity.created_at >= today_start)) or 0
    promises = db.scalar(select(func.count(PaymentPromise.id)).where(PaymentPromise.tenant_id == tenant.id, PaymentPromise.user_id.in_(visible_user_ids), PaymentPromise.status == "Vigente")) or 0
    overdue_promises = db.scalar(select(func.count(PaymentPromise.id)).where(PaymentPromise.tenant_id == tenant.id, PaymentPromise.user_id.in_(visible_user_ids), PaymentPromise.status == "Vencida")) or 0
    payments = db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.tenant_id == tenant.id, Payment.user_id.in_(visible_user_ids), Payment.paid_at >= month_start)) or 0
    agreements = db.scalar(select(func.count(PaymentAgreement.id)).where(PaymentAgreement.tenant_id == tenant.id, PaymentAgreement.user_id.in_(visible_user_ids), PaymentAgreement.status.in_(["active", "vigente", "al dia"]))) or 0
    legal = db.scalar(select(func.count(LegalCase.id)).where(LegalCase.tenant_id == tenant.id)) or 0
    return {
        "audience": "operational_leader",
        "title": "Panel de equipo",
        "generated_at": datetime.now(timezone.utc),
        "cards": [
            _card("Equipo directo", len(team_ids), "Usuarios bajo liderazgo directo.", "blue"),
            _card("Clientes equipo", assigned, "Clientes bajo gestion del equipo.", "green"),
            _card("Obligaciones equipo", obligations, f"Saldo visible {int(balance):,}".replace(",", "."), "blue"),
            _card("Gestiones hoy", activities_today, "Contactos y seguimientos registrados hoy.", "neutral"),
            _card("Promesas vigentes", promises, f"{overdue_promises} promesas vencidas requieren seguimiento.", "yellow"),
            _card("Pagos mes", int(payments), "Recaudo registrado por el equipo en el mes.", "green"),
            _card("Acuerdos activos", agreements, "Compromisos estructurados del equipo.", "blue"),
        ],
        "alerts": [
            {"title": "Casos juridicos", "body": f"{legal} expedientes juridicos visibles en tu empresa.", "tone": "neutral"},
            {"title": "Alcance de liderazgo", "body": "El panel se limita a tus agentes directos, obligaciones asignadas y carteras autorizadas.", "tone": "green"},
        ],
    }


def legal_profile_dashboard(db: Session, user: User, profile_role: str | None) -> dict:
    tenant = get_current_tenant(db, user)
    case_query = select(func.count(LegalCase.id)).where(LegalCase.tenant_id == tenant.id)
    if profile_role == "lawyer":
        case_query = case_query.where(LegalCase.assigned_lawyer_id == user.id)
    cases = db.scalar(case_query) or 0
    deadlines = db.scalar(
        select(func.count(LegalCase.id)).where(
            LegalCase.tenant_id == tenant.id,
            LegalCase.next_deadline_at.is_not(None),
            *( [LegalCase.assigned_lawyer_id == user.id] if profile_role == "lawyer" else [] ),
        )
    ) or 0
    documents = db.scalar(
        select(func.count(Document.id))
        .join(LegalCase, Document.legal_case_id == LegalCase.id)
        .where(
            Document.tenant_id == tenant.id,
            *( [LegalCase.assigned_lawyer_id == user.id] if profile_role == "lawyer" else [] ),
        )
    ) or 0
    return {
        "audience": "operational_leader",
        "title": "Panel juridico operativo",
        "generated_at": datetime.now(timezone.utc),
        "cards": [
            _card("Casos juridicos", cases, "Expedientes disponibles segun asignacion y permisos.", "blue"),
            _card("Vencimientos", deadlines, "Casos con proxima fecha procesal registrada.", "yellow"),
            _card("Documentos", documents, "Soportes documentales vinculados a expedientes.", "green"),
        ],
        "alerts": [
            {"title": "Acceso especializado", "body": "Tu vista se concentra en juridico, documentos y clientes relacionados.", "tone": "green"},
        ],
    }


def sales_profile_dashboard(db: Session, user: User, profile_role: str | None) -> dict:
    tenant = get_current_tenant(db, user)
    lead_query = select(func.count(Lead.id)).where(Lead.tenant_id == tenant.id)
    opportunity_query = select(func.count(Opportunity.id)).where(Opportunity.tenant_id == tenant.id)
    expected_query = select(func.coalesce(func.sum(Opportunity.amount), 0)).where(Opportunity.tenant_id == tenant.id)
    if profile_role == "sales_advisor":
        lead_query = lead_query.where(Lead.assigned_user_id == user.id)
        opportunity_query = opportunity_query.where(Opportunity.assigned_user_id == user.id)
        expected_query = expected_query.where(Opportunity.assigned_user_id == user.id)
    leads = db.scalar(lead_query) or 0
    opportunities = db.scalar(opportunity_query) or 0
    expected = db.scalar(expected_query) or 0
    return {
        "audience": "operational_leader",
        "title": "Panel comercial operativo",
        "generated_at": datetime.now(timezone.utc),
        "cards": [
            _card("Leads", leads, "Prospectos visibles para tu rol comercial.", "blue"),
            _card("Oportunidades", opportunities, "Negocios abiertos o historicos del pipeline.", "green"),
            _card("Pipeline", int(expected), "Valor potencial registrado en oportunidades.", "yellow"),
        ],
        "alerts": [
            {"title": "Acceso especializado", "body": "Tu vista se concentra en ventas, oportunidades y clientes en lectura.", "tone": "green"},
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
