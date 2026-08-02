from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AlertRule, Customer, Lead, LegalAction, LegalCase, LegalDeadline, LegalHearing, Opportunity, PaymentAgreement, PaymentAgreementInstallment, PaymentPromise, Tenant, TenantModule, TenantSubscription, User
from app.models.careflow import CareCase
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin, user_has_permission


SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _threshold(db: Session, tenant_id: int, module: str, condition_type: str, default: int) -> int:
    query = (
        select(AlertRule)
        .where(AlertRule.module == module, AlertRule.condition_type == condition_type, AlertRule.is_active.is_(True))
        .where((AlertRule.tenant_id.is_(None)) | (AlertRule.tenant_id == tenant_id))
        .order_by(AlertRule.tenant_id.desc().nullslast(), AlertRule.id.desc())
    )
    rule = db.scalar(query)
    return int(rule.threshold_days if rule and rule.threshold_days is not None else default)


def _alert(
    *,
    tenant_id: int,
    module: str,
    entity_type: str,
    entity_id: int | None,
    title: str,
    message: str,
    severity: str,
    due_at: datetime | None = None,
    assigned_user_id: int | None = None,
    action: str | None = None,
) -> dict[str, Any]:
    return {
        "id": f"{module}:{entity_type}:{entity_id or 'scope'}:{abs(hash((title, due_at))) % 1000000}",
        "tenant_id": tenant_id,
        "module": module,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "title": title,
        "message": message,
        "severity": severity,
        "status": "open",
        "due_at": due_at,
        "assigned_user_id": assigned_user_id,
        "action": action,
    }


def _tenant_ids(db: Session, user: User, tenant_id: int | None = None) -> list[int]:
    if is_platform_admin(db, user):
        if tenant_id:
            return [tenant_id]
        return list(db.scalars(select(Tenant.id).where(Tenant.status == "active").order_by(Tenant.id)))
    return [user.tenant_id]


def _can_view_module(db: Session, user: User, module: str) -> bool:
    if is_platform_admin(db, user):
        return True
    checks = {
        "collections": ("collections.queue.view", "collections.promises.view", "collections.agreements.view"),
        "legal": ("legal.cases.view", "legal.deadlines.view"),
        "sales": ("sales.leads.view", "sales.opportunities.view"),
        "careflow": ("careflow.view", "careflow.reports.view"),
        "administration": ("tenant.settings.view", "users.view", "modules.view", "audit.logs.view"),
    }
    return any(user_has_permission(db, user, code) for code in checks.get(module, ("menu.view",)))


def _assigned_filter_needed(db: Session, user: User, module: str) -> bool:
    if is_platform_admin(db, user) or is_company_admin(db, user):
        return False
    profile_role = get_profile_role_code(db, user)
    if module == "legal":
        return profile_role == "lawyer"
    if module == "sales":
        return profile_role == "sales_advisor"
    if module == "collections":
        return user.role == "agent" or profile_role == "collections_agent"
    return True


def _collection_alerts(db: Session, user: User, tenant_ids: list[int]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    now = _now()
    for tenant_id in tenant_ids:
        stale_days = _threshold(db, tenant_id, "collections", "customer_without_activity", 7)
        stale_limit = now - timedelta(days=stale_days)
        query = select(Customer).where(Customer.tenant_id == tenant_id)
        if _assigned_filter_needed(db, user, "collections"):
            query = query.where(Customer.assigned_user_id == user.id)
        for customer in db.scalars(query.limit(200)):
            last_contact = customer.last_contact_at or customer.created_at
            if last_contact and last_contact < stale_limit:
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="collections",
                        entity_type="customer",
                        entity_id=customer.id,
                        title=f"Cliente sin gestion: {customer.name}",
                        message=f"Sin contacto registrado hace mas de {stale_days} dias. Prioridad {customer.priority}.",
                        severity="high" if customer.risk.lower().startswith("alto") else "medium",
                        due_at=customer.next_contact_at,
                        assigned_user_id=customer.assigned_user_id,
                        action="Programar gestion y actualizar resultado.",
                    )
                )
            if customer.risk.lower().startswith("alto") and not customer.next_action:
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="collections",
                        entity_type="customer",
                        entity_id=customer.id,
                        title=f"Alto riesgo sin siguiente accion",
                        message=f"{customer.name} concentra riesgo alto y no tiene accion definida.",
                        severity="critical",
                        assigned_user_id=customer.assigned_user_id,
                        action="Definir siguiente accion de recuperacion.",
                    )
                )
        promise_window = _threshold(db, tenant_id, "collections", "promise_due_soon", 2)
        promise_query = select(PaymentPromise).where(PaymentPromise.tenant_id == tenant_id, PaymentPromise.status.in_(["Vigente", "active", "open"]))
        if _assigned_filter_needed(db, user, "collections"):
            promise_query = promise_query.where(PaymentPromise.user_id == user.id)
        for promise in db.scalars(promise_query.limit(200)):
            if promise.due_date < now:
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="collections",
                        entity_type="payment_promise",
                        entity_id=promise.id,
                        title="Promesa vencida",
                        message=f"Promesa por {promise.amount:,} vencida.",
                        severity="critical",
                        due_at=promise.due_date,
                        assigned_user_id=promise.user_id,
                        action="Contactar cliente y actualizar compromiso.",
                    )
                )
            elif promise.due_date <= now + timedelta(days=promise_window):
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="collections",
                        entity_type="payment_promise",
                        entity_id=promise.id,
                        title="Promesa proxima a vencer",
                        message=f"Promesa por {promise.amount:,} requiere confirmacion.",
                        severity="medium",
                        due_at=promise.due_date,
                        assigned_user_id=promise.user_id,
                        action="Confirmar pago antes del vencimiento.",
                    )
                )
        agreements = select(PaymentAgreement).where(PaymentAgreement.tenant_id == tenant_id, PaymentAgreement.status.in_(["active", "open"]))
        if _assigned_filter_needed(db, user, "collections"):
            agreements = agreements.where(PaymentAgreement.user_id == user.id)
        agreement_ids = [item.id for item in db.scalars(agreements.limit(200))]
        if agreement_ids:
            installments = db.scalars(
                select(PaymentAgreementInstallment)
                .where(PaymentAgreementInstallment.agreement_id.in_(agreement_ids), PaymentAgreementInstallment.due_date < now)
                .where(PaymentAgreementInstallment.paid_amount < PaymentAgreementInstallment.amount)
                .limit(200)
            )
            for installment in installments:
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="collections",
                        entity_type="payment_agreement_installment",
                        entity_id=installment.id,
                        title="Cuota de acuerdo vencida",
                        message=f"Cuota por {installment.amount:,} con pago pendiente.",
                        severity="high",
                        due_at=installment.due_date,
                        action="Gestionar cumplimiento del acuerdo.",
                    )
                )
    return alerts


def _legal_alerts(db: Session, user: User, tenant_ids: list[int]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    now = _now()
    for tenant_id in tenant_ids:
        due_window = _threshold(db, tenant_id, "legal", "legal_deadline_due_soon", 7)
        cases_query = select(LegalCase).where(LegalCase.tenant_id == tenant_id)
        if _assigned_filter_needed(db, user, "legal"):
            cases_query = cases_query.where(LegalCase.assigned_lawyer_id == user.id)
        cases = list(db.scalars(cases_query.limit(200)))
        case_ids = [item.id for item in cases]
        for case in cases:
            last_action_at = db.scalar(select(func.max(LegalAction.action_date)).where(LegalAction.legal_case_id == case.id)) or case.created_at
            action_count = db.scalar(select(func.count()).select_from(LegalAction).where(LegalAction.legal_case_id == case.id)) or 0
            inactive_days = _threshold(db, tenant_id, "legal", "legal_case_without_action", 10)
            if action_count == 0 and case.created_at < now - timedelta(days=inactive_days):
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="legal",
                        entity_type="legal_case",
                        entity_id=case.id,
                        title=f"Caso sin actuacion: {case.case_number or case.id}",
                        message=f"El expediente lleva mas de {inactive_days} dias sin movimiento registrado.",
                        severity="high",
                        due_at=last_action_at,
                        assigned_user_id=case.assigned_lawyer_id,
                        action="Registrar actuacion o actualizar etapa.",
                    )
                )
            if (case.risk or "").lower() in {"alto", "high", "critical"}:
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="legal",
                        entity_type="legal_case",
                        entity_id=case.id,
                        title="Caso juridico de riesgo alto",
                        message=f"Revisar estrategia procesal para {case.case_number or case.id}.",
                        severity="critical",
                        due_at=case.next_deadline_at,
                        assigned_user_id=case.assigned_lawyer_id,
                        action="Validar proxima actuacion y documentos.",
                    )
                )
        if case_ids:
            for deadline in db.scalars(select(LegalDeadline).where(LegalDeadline.legal_case_id.in_(case_ids), LegalDeadline.status.in_(["open", "pending"])).limit(200)):
                if deadline.due_at < now:
                    severity = "critical"
                    title = "Vencimiento juridico vencido"
                elif deadline.due_at <= now + timedelta(days=due_window):
                    severity = "high"
                    title = "Vencimiento juridico proximo"
                else:
                    continue
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="legal",
                        entity_type="legal_deadline",
                        entity_id=deadline.id,
                        title=title,
                        message=deadline.title,
                        severity=severity,
                        due_at=deadline.due_at,
                        action="Revisar expediente y cerrar vencimiento.",
                    )
                )
            hearing_window = _threshold(db, tenant_id, "legal", "legal_hearing_due_soon", 5)
            for hearing in db.scalars(select(LegalHearing).where(LegalHearing.legal_case_id.in_(case_ids), LegalHearing.status.in_(["scheduled", "open"])).limit(200)):
                if now <= hearing.scheduled_at <= now + timedelta(days=hearing_window):
                    alerts.append(
                        _alert(
                            tenant_id=tenant_id,
                            module="legal",
                            entity_type="legal_hearing",
                            entity_id=hearing.id,
                            title="Audiencia proxima",
                            message=f"{hearing.hearing_type} programada en {hearing.location or 'ubicacion por confirmar'}.",
                            severity="high",
                            due_at=hearing.scheduled_at,
                            action="Confirmar agenda, documentos y responsable.",
                        )
                    )
    return alerts


def _sales_alerts(db: Session, user: User, tenant_ids: list[int]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    now = _now()
    for tenant_id in tenant_ids:
        stale_days = _threshold(db, tenant_id, "sales", "lead_without_followup", 5)
        lead_query = select(Lead).where(Lead.tenant_id == tenant_id, Lead.status.notin_(["won", "lost", "closed"]))
        opportunity_query = select(Opportunity).where(Opportunity.tenant_id == tenant_id, Opportunity.status.in_(["open", "active"]))
        if _assigned_filter_needed(db, user, "sales"):
            lead_query = lead_query.where(Lead.assigned_user_id == user.id)
            opportunity_query = opportunity_query.where(Opportunity.assigned_user_id == user.id)
        for lead in db.scalars(lead_query.limit(200)):
            if lead.created_at < now - timedelta(days=stale_days):
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="sales",
                        entity_type="lead",
                        entity_id=lead.id,
                        title=f"Lead sin seguimiento: {lead.name}",
                        message=f"Lead en estado {lead.status} sin avance reciente.",
                        severity="medium",
                        assigned_user_id=lead.assigned_user_id,
                        action="Registrar contacto o convertir a oportunidad.",
                    )
                )
        close_window = _threshold(db, tenant_id, "sales", "opportunity_close_due_soon", 7)
        for opportunity in db.scalars(opportunity_query.limit(200)):
            if opportunity.expected_close_date and opportunity.expected_close_date <= now + timedelta(days=close_window):
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="sales",
                        entity_type="opportunity",
                        entity_id=opportunity.id,
                        title="Oportunidad proxima a cierre",
                        message=f"{opportunity.name} por {opportunity.amount:,} requiere accion comercial.",
                        severity="high" if opportunity.amount >= 10_000_000 else "medium",
                        due_at=opportunity.expected_close_date,
                        assigned_user_id=opportunity.assigned_user_id,
                        action="Actualizar etapa, probabilidad y siguiente paso.",
                    )
                )
            if opportunity.amount >= 20_000_000 and opportunity.probability < 50:
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="sales",
                        entity_type="opportunity",
                        entity_id=opportunity.id,
                        title="Oportunidad de alto valor con baja probabilidad",
                        message=f"{opportunity.name} necesita estrategia comercial.",
                        severity="high",
                        assigned_user_id=opportunity.assigned_user_id,
                        action="Revisar objeciones y plan de cierre.",
                    )
                )
    return alerts


def _careflow_module_active(db: Session, tenant_id: int) -> bool:
    module = db.scalar(select(TenantModule).where(TenantModule.tenant_id == tenant_id, TenantModule.module_code == "careflow"))
    return bool(module and module.enabled and module.is_enabled)


def _careflow_alerts(db: Session, user: User, tenant_ids: list[int]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    now = _now()
    for tenant_id in tenant_ids:
        if not _careflow_module_active(db, tenant_id):
            continue
        query = select(CareCase).where(
            CareCase.tenant_id == tenant_id,
            CareCase.status.in_(["nuevo", "asignado", "en_proceso", "pendiente_cliente", "pendiente_interno"]),
        )
        if _assigned_filter_needed(db, user, "careflow"):
            query = query.where((CareCase.assigned_user_id == user.id) | (CareCase.created_by_id == user.id))
        for item in db.scalars(query.limit(200)):
            if item.due_at and item.due_at < now:
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="careflow",
                        entity_type="care_case",
                        entity_id=item.id,
                        title=f"CareFlow vencido: {item.case_number}",
                        message=item.title,
                        severity="critical",
                        due_at=item.due_at,
                        assigned_user_id=item.assigned_user_id,
                        action="Actualizar estado, reasignar o cerrar caso.",
                    )
                )
            elif item.due_at and item.due_at <= now + timedelta(days=2):
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="careflow",
                        entity_type="care_case",
                        entity_id=item.id,
                        title=f"CareFlow proximo a SLA: {item.case_number}",
                        message=item.title,
                        severity="high",
                        due_at=item.due_at,
                        assigned_user_id=item.assigned_user_id,
                        action="Registrar avance antes del vencimiento.",
                    )
                )
            if item.priority == "critica":
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="careflow",
                        entity_type="care_case",
                        entity_id=item.id,
                        title=f"Caso critico CareFlow: {item.case_number}",
                        message=item.title,
                        severity="critical",
                        due_at=item.due_at,
                        assigned_user_id=item.assigned_user_id,
                        action="Priorizar seguimiento de atencion al cliente.",
                    )
                )
            if item.assigned_user_id is None and (is_platform_admin(db, user) or is_company_admin(db, user)):
                alerts.append(
                    _alert(
                        tenant_id=tenant_id,
                        module="careflow",
                        entity_type="care_case",
                        entity_id=item.id,
                        title=f"CareFlow sin responsable: {item.case_number}",
                        message=item.title,
                        severity="high",
                        due_at=item.due_at,
                        action="Asignar responsable del caso.",
                    )
                )
    return alerts


def _administration_alerts(db: Session, user: User, tenant_ids: list[int]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    if not (is_platform_admin(db, user) or is_company_admin(db, user)):
        return alerts
    for tenant_id in tenant_ids:
        tenant = db.get(Tenant, tenant_id)
        if not tenant:
            continue
        subscription = db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id, TenantSubscription.status == "active"))
        if subscription is None:
            alerts.append(
                _alert(
                    tenant_id=tenant_id,
                    module="administration",
                    entity_type="tenant",
                    entity_id=tenant_id,
                    title="Tenant sin plan activo",
                    message=f"{tenant.name} no tiene suscripcion activa registrada.",
                    severity="critical",
                    action="Asignar plan o revisar estado comercial.",
                )
            )
        active_modules = list(db.scalars(select(TenantModule).where(TenantModule.tenant_id == tenant_id, TenantModule.is_enabled.is_(True))))
        for module in active_modules:
            if module.module_code in {"core", "administration"}:
                continue
            # Senal comercial simple: modulo activo sin permisos configurados para usuarios tenant.
            alerts.append(
                _alert(
                    tenant_id=tenant_id,
                    module="administration",
                    entity_type="tenant_module",
                    entity_id=module.id,
                    title=f"Modulo activo: {module.module_code}",
                    message="Revisar adopcion, usuarios con acceso y configuracion funcional.",
                    severity="low",
                    action="Validar roles y tablero de uso.",
                )
            )
    return alerts


def collect_alerts(
    db: Session,
    user: User,
    *,
    module: str | None = None,
    severity: str | None = None,
    status: str | None = "open",
    tenant_id: int | None = None,
    assigned_to_me: bool = False,
    limit: int = 50,
) -> list[dict[str, Any]]:
    tenant_ids = _tenant_ids(db, user, tenant_id)
    modules = [module] if module else ["collections", "legal", "sales", "careflow", "administration"]
    alerts: list[dict[str, Any]] = []
    if "collections" in modules and _can_view_module(db, user, "collections"):
        alerts.extend(_collection_alerts(db, user, tenant_ids))
    if "legal" in modules and _can_view_module(db, user, "legal"):
        alerts.extend(_legal_alerts(db, user, tenant_ids))
    if "sales" in modules and _can_view_module(db, user, "sales"):
        alerts.extend(_sales_alerts(db, user, tenant_ids))
    if "careflow" in modules and _can_view_module(db, user, "careflow"):
        alerts.extend(_careflow_alerts(db, user, tenant_ids))
    if "administration" in modules and _can_view_module(db, user, "administration"):
        alerts.extend(_administration_alerts(db, user, tenant_ids))
    if severity:
        alerts = [item for item in alerts if item["severity"] == severity]
    if status:
        alerts = [item for item in alerts if item["status"] == status]
    if assigned_to_me:
        alerts = [item for item in alerts if item.get("assigned_user_id") in {None, user.id}]
    alerts.sort(key=lambda item: (-SEVERITY_ORDER.get(item["severity"], 0), item.get("due_at") or _now()))
    return alerts[: max(1, min(limit, 200))]


def summarize_alerts(alerts: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {"total": len(alerts), "critical": 0, "high": 0, "medium": 0, "low": 0, "by_module": {}}
    for item in alerts:
        severity = item.get("severity", "medium")
        if severity in summary:
            summary[severity] += 1
        module = item.get("module", "core")
        summary["by_module"][module] = summary["by_module"].get(module, 0) + 1
    return summary
