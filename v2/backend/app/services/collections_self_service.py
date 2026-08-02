from __future__ import annotations

import json
from datetime import datetime, time, timedelta, timezone
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.roles import AGENT, COORDINATOR
from app.models import (
    AlertRule,
    BusinessRule,
    Customer,
    CustomerObligation,
    GeneratedAlert,
    ManagementActivity,
    Payment,
    PaymentAgreement,
    PaymentPromise,
    Project,
    TenantModule,
    User,
    UserProjectAssignment,
)
from app.schemas.self_service import (
    AdvisorManagementInsightsOut,
    CustomerManagementInsightsOut,
    ManagementScoreOut,
    ScoringRuleOut,
    SessionPriorityOut,
    SessionSummaryOut,
)
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin


PRIORITY_LIMIT = 10
SCORING_RULE_TYPES = {"management_scoring", "activity_scoring", "scoring"}
ALERT_DEFAULTS = {
    "max_days_without_management": 30,
    "min_effective_score": 60,
    "promise_due_in_days": 3,
    "min_critical_balance": 500000,
    "min_critical_dpd": 60,
}
NEGATIVE_RESULT_TERMS = ("sin contacto", "no contesta", "fallida", "ocupado", "no ubicado", "telefono errado")
EFFECTIVE_RESULT_TERMS = ("contactado", "contacto efectivo", "promesa", "pago", "acuerdo", "negociacion", "normalizado")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _month_start(value: datetime | None = None) -> datetime:
    current = value or _now()
    return datetime(current.year, current.month, 1, tzinfo=timezone.utc)


def _previous_month_start(value: datetime | None = None) -> datetime:
    current = _month_start(value)
    previous_day = current - timedelta(days=1)
    return datetime(previous_day.year, previous_day.month, 1, tzinfo=timezone.utc)


def _day_start(value: datetime | None = None) -> datetime:
    current = value or _now()
    return datetime.combine(current.date(), time.min, tzinfo=timezone.utc)


def _parse_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _lower(value: Any) -> str:
    return str(value or "").strip().lower()


def _is_effective_text(result: str | None) -> bool:
    text = _lower(result)
    if any(term in text for term in NEGATIVE_RESULT_TERMS):
        return False
    return any(term in text for term in EFFECTIVE_RESULT_TERMS)


def _score_label(score: int) -> str:
    if score >= 85:
        return "excelente"
    if score >= 65:
        return "alta"
    if score >= 40:
        return "media"
    return "baja"


def alert_settings_for_tenant(db: Session, tenant_id: int | None) -> dict[str, int]:
    settings = dict(ALERT_DEFAULTS)
    if tenant_id is None:
        return settings
    rules = db.scalars(
        select(AlertRule).where(
            AlertRule.is_active.is_(True),
            AlertRule.module.in_(["collections", "crm"]),
            or_(AlertRule.tenant_id.is_(None), AlertRule.tenant_id == tenant_id),
        )
    ).all()
    for rule in rules:
        code = rule.code or rule.condition_type
        if code in settings and rule.threshold_days > 0:
            settings[code] = int(rule.threshold_days)
        if rule.condition_type in settings and rule.threshold_days > 0:
            settings[rule.condition_type] = int(rule.threshold_days)
    return settings


def scoring_rules_for_tenant(db: Session, tenant_id: int | None) -> list[ScoringRuleOut]:
    query = select(BusinessRule).where(
        BusinessRule.is_active.is_(True),
        BusinessRule.module.in_(["collections", "crm"]),
        BusinessRule.rule_type.in_(SCORING_RULE_TYPES),
    )
    if tenant_id is None:
        query = query.where(BusinessRule.tenant_id.is_(None))
    else:
        query = query.where(or_(BusinessRule.tenant_id.is_(None), BusinessRule.tenant_id == tenant_id))
    rules = list(db.scalars(query.order_by(BusinessRule.code, BusinessRule.tenant_id.desc().nullslast())))
    if tenant_id is not None:
        prioritized: dict[str, BusinessRule] = {}
        for item in sorted(rules, key=lambda rule: (0 if rule.tenant_id == tenant_id else 1, rule.code)):
            prioritized.setdefault(item.code, item)
        rules = list(prioritized.values())
    if rules:
        return [
            ScoringRuleOut(
                id=item.id,
                code=item.code,
                name=item.name,
                description=item.description,
                source="business_rules",
                condition=_parse_json(item.condition_json),
                action=_parse_json(item.action_json),
                severity=item.severity,
                is_active=item.is_active,
            )
            for item in rules
        ]
    return [
        ScoringRuleOut(
            code="fallback_effective_contact",
            name="Base configurable pendiente",
            description="Se usa solo cuando el tenant aun no tiene reglas activas en business_rules.",
            source="fallback",
            condition={"result_contains_any": list(EFFECTIVE_RESULT_TERMS)},
            action={"score_hint": 65},
        )
    ]


def _rule_matches(rule: ScoringRuleOut, activity: ManagementActivity, customer: Customer | None, obligation: CustomerObligation | None) -> bool:
    condition = rule.condition or {}
    result = _lower(activity.result)
    channel = _lower(activity.channel)
    note = _lower(activity.note)
    balance = int(obligation.current_balance if obligation else customer.balance if customer else 0)
    dpd = int(obligation.days_past_due if obligation else customer.dpd if customer else 0)
    risk = _lower(obligation.risk if obligation else customer.risk if customer else "")

    if "channel" in condition and channel != _lower(condition["channel"]):
        return False
    if "channel_any" in condition and channel not in {_lower(item) for item in condition.get("channel_any") or []}:
        return False
    if "result_contains" in condition and _lower(condition["result_contains"]) not in result:
        return False
    if "result_contains_any" in condition and not any(_lower(item) in result for item in condition.get("result_contains_any") or []):
        return False
    if "note_contains" in condition and _lower(condition["note_contains"]) not in note:
        return False
    if "has_obligation" in condition and bool(activity.obligation_id) != bool(condition["has_obligation"]):
        return False
    if "min_balance" in condition and balance < int(condition["min_balance"] or 0):
        return False
    if "min_dpd" in condition and dpd < int(condition["min_dpd"] or 0):
        return False
    if "risk_any" in condition and risk not in {_lower(item) for item in condition.get("risk_any") or []}:
        return False
    return True


def _fallback_score(activity: ManagementActivity, customer: Customer | None, obligation: CustomerObligation | None) -> int:
    score = 20
    result = _lower(activity.result)
    if _is_effective_text(result):
        score += 35
    if "promesa" in result or "acuerdo" in result:
        score += 20
    if activity.channel in {"phone", "whatsapp"}:
        score += 10
    if activity.next_contact_at:
        score += 10
    balance = int(obligation.current_balance if obligation else customer.balance if customer else 0)
    dpd = int(obligation.days_past_due if obligation else customer.dpd if customer else 0)
    if balance >= ALERT_DEFAULTS["min_critical_balance"] or dpd >= ALERT_DEFAULTS["min_critical_dpd"]:
        score += 10
    return min(score, 100)


def score_activity(db: Session, activity: ManagementActivity) -> ManagementScoreOut:
    customer = db.get(Customer, activity.customer_id)
    obligation = db.get(CustomerObligation, activity.obligation_id) if activity.obligation_id else None
    user = db.get(User, activity.user_id)
    rules = scoring_rules_for_tenant(db, activity.tenant_id)
    configured_rules = [rule for rule in rules if rule.source == "business_rules"]
    score = 0
    source = "business_rules"
    for rule in configured_rules:
        if _rule_matches(rule, activity, customer, obligation):
            action = rule.action or {}
            score += int(action.get("score", action.get("points", 0)) or 0)
    if not configured_rules:
        score = _fallback_score(activity, customer, obligation)
        source = "fallback"
    score = max(0, min(score, 100))
    min_effective = alert_settings_for_tenant(db, activity.tenant_id)["min_effective_score"]
    return ManagementScoreOut(
        activity_id=activity.id,
        customer_id=activity.customer_id,
        customer_name=customer.name if customer else None,
        project_id=activity.project_id,
        obligation_id=activity.obligation_id,
        obligation_number=obligation.obligation_number if obligation else None,
        user_id=activity.user_id,
        user_name=user.name if user else None,
        channel=activity.channel,
        result=activity.result,
        note=activity.note,
        created_at=activity.created_at,
        score=score,
        label=_score_label(score),
        is_effective=score >= min_effective or _is_effective_text(activity.result),
        scoring_source=source,
    )


def _best(items: list[ManagementScoreOut]) -> ManagementScoreOut | None:
    if not items:
        return None
    return sorted(items, key=lambda item: (item.score, item.created_at), reverse=True)[0]


def customer_management_insights(db: Session, customer: Customer) -> CustomerManagementInsightsOut:
    month_start = _month_start()
    previous_start = _previous_month_start()
    activities = list(
        db.scalars(
            select(ManagementActivity)
            .where(ManagementActivity.customer_id == customer.id, ManagementActivity.tenant_id == customer.tenant_id)
            .order_by(ManagementActivity.created_at.desc())
            .limit(120)
        )
    )
    scored = [score_activity(db, item) for item in activities]
    current = [item for item in scored if item.created_at >= month_start]
    previous = [item for item in scored if previous_start <= item.created_at < month_start]
    return CustomerManagementInsightsOut(
        customer_id=customer.id,
        customer_name=customer.name,
        best_current_month=_best(current),
        best_previous_month=_best(previous),
        best_historical=_best(scored),
        recent=scored[:10],
    )


def advisor_management_insights(db: Session, target: User) -> AdvisorManagementInsightsOut:
    today_start = _day_start()
    month_start = _month_start()
    activities = list(
        db.scalars(
            select(ManagementActivity)
            .where(ManagementActivity.tenant_id == target.tenant_id, ManagementActivity.user_id == target.id, ManagementActivity.created_at >= month_start)
            .order_by(ManagementActivity.created_at.desc())
            .limit(150)
        )
    )
    scored = [score_activity(db, item) for item in activities]
    historical = [
        score_activity(db, item)
        for item in db.scalars(
            select(ManagementActivity)
            .where(ManagementActivity.tenant_id == target.tenant_id, ManagementActivity.user_id == target.id)
            .order_by(ManagementActivity.created_at.desc())
            .limit(150)
        )
    ]
    return AdvisorManagementInsightsOut(
        user_id=target.id,
        user_name=target.name,
        activities_today=sum(1 for item in activities if item.created_at >= today_start),
        activities_month=len(activities),
        effective_month=sum(1 for item in scored if item.is_effective),
        promises_created_month=db.scalar(select(func.count(PaymentPromise.id)).where(PaymentPromise.tenant_id == target.tenant_id, PaymentPromise.user_id == target.id, PaymentPromise.created_at >= month_start)) or 0,
        payments_month=int(db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.tenant_id == target.tenant_id, Payment.user_id == target.id, Payment.paid_at >= month_start)) or 0),
        agreements_created_month=db.scalar(select(func.count(PaymentAgreement.id)).where(PaymentAgreement.tenant_id == target.tenant_id, PaymentAgreement.user_id == target.id, PaymentAgreement.created_at >= month_start)) or 0,
        best_current_month=_best(scored),
        best_historical=_best(historical),
    )


def _active_project_ids(db: Session, user: User) -> list[int]:
    return list(
        db.scalars(
            select(UserProjectAssignment.project_id).where(
                UserProjectAssignment.user_id == user.id,
                UserProjectAssignment.is_active.is_(True),
            )
        )
    )


def _team_user_ids(db: Session, leader: User) -> list[int]:
    ids = []
    if leader.role == AGENT:
        ids.append(leader.id)
    ids.extend(db.scalars(select(User.id).where(User.tenant_id == leader.tenant_id, User.leader_id == leader.id, User.role == AGENT, User.status == "active")))
    return list(dict.fromkeys(ids))


def _visible_customer_query(db: Session, user: User, tenant_id: int):
    query = select(Customer).where(Customer.tenant_id == tenant_id)
    if is_platform_admin(db, user) or is_company_admin(db, user):
        return query
    profile = get_profile_role_code(db, user)
    if user.role == COORDINATOR or profile in {"collections_leader", "operational_leader"}:
        conditions = [Customer.assigned_user_id.in_(_team_user_ids(db, user))]
        project_ids = _active_project_ids(db, user)
        if project_ids:
            conditions.append(Customer.project_id.in_(project_ids))
        return query.where(or_(*conditions))
    return query.where(Customer.assigned_user_id == user.id)


def _priority(
    role_group: str,
    key: str,
    title: str,
    message: str,
    severity: str,
    value: Any = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
) -> SessionPriorityOut:
    return SessionPriorityOut(
        id=f"{role_group}:{key}",
        role_group=role_group,
        title=title,
        message=message,
        severity=severity,
        value=str(value) if value is not None else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
    )


def _role_group(db: Session, user: User) -> str:
    profile = get_profile_role_code(db, user)
    if is_platform_admin(db, user):
        return "platform_admin"
    if is_company_admin(db, user):
        return "tenant_admin"
    if user.role == COORDINATOR or profile in {"collections_leader", "operational_leader"}:
        return "leader"
    if user.role == AGENT or profile == "collections_agent":
        return "advisor"
    return "operational"


def _tenant_for_summary(db: Session, user: User, tenant_id: int | None) -> int:
    if is_platform_admin(db, user) and tenant_id:
        return tenant_id
    return user.tenant_id


def _append_advisor_priorities(db: Session, user: User, tenant_id: int, settings: dict[str, int], priorities: list[SessionPriorityOut]) -> None:
    now = _now()
    month_start = _month_start(now)
    previous_start = _previous_month_start(now)
    visible_customers = _visible_customer_query(db, user, tenant_id).subquery()
    managed_this_month = select(ManagementActivity.customer_id).where(ManagementActivity.tenant_id == tenant_id, ManagementActivity.created_at >= month_start)
    stale_count = db.scalar(
        select(func.count()).select_from(visible_customers).where(
            visible_customers.c.assigned_user_id == user.id,
            visible_customers.c.id.not_in(managed_this_month),
        )
    ) or 0
    if stale_count:
        priorities.append(_priority("advisor", "without_management_month", "Clientes sin gestion este mes", "Hay clientes asignados que aun no tienen gestion registrada en el mes actual.", "high", stale_count, "Abrir cola de gestion"))

    due_until = now + timedelta(days=settings["promise_due_in_days"])
    promises_count = db.scalar(
        select(func.count(PaymentPromise.id)).where(
            PaymentPromise.tenant_id == tenant_id,
            PaymentPromise.user_id == user.id,
            PaymentPromise.status.in_(["Vigente", "Vencida", "pending", "active"]),
            PaymentPromise.due_date <= due_until,
        )
    ) or 0
    if promises_count:
        priorities.append(_priority("advisor", "due_promises", "Promesas por confirmar", "Revisa promesas vencidas o proximas a vencer para evitar perdida de acuerdos.", "high", promises_count, "Ver promesas"))

    critical_count = db.scalar(
        select(func.count()).select_from(visible_customers).where(
            visible_customers.c.assigned_user_id == user.id,
            visible_customers.c.balance >= settings["min_critical_balance"],
            or_(visible_customers.c.last_contact_at.is_(None), visible_customers.c.last_contact_at < now - timedelta(days=settings["max_days_without_management"])),
        )
    ) or 0
    if critical_count:
        priorities.append(_priority("advisor", "critical_without_contact", "Saldo alto sin contacto efectivo", "Prioriza clientes de alto valor que no tienen contacto reciente.", "critical", critical_count, "Gestionar casos criticos"))

    previous_best = list(
        db.scalars(
            select(ManagementActivity)
            .where(
                ManagementActivity.tenant_id == tenant_id,
                ManagementActivity.user_id == user.id,
                ManagementActivity.created_at >= previous_start,
                ManagementActivity.created_at < month_start,
            )
            .order_by(ManagementActivity.created_at.desc())
            .limit(80)
        )
    )
    current_customers = set(
        db.scalars(
            select(ManagementActivity.customer_id).where(
                ManagementActivity.tenant_id == tenant_id,
                ManagementActivity.user_id == user.id,
                ManagementActivity.created_at >= month_start,
            )
        )
    )
    pending_best = {item.customer_id for item in previous_best if item.customer_id not in current_customers and score_activity(db, item).is_effective}
    if pending_best:
        priorities.append(_priority("advisor", "previous_best_not_current", "Buenas gestiones sin continuidad", "Clientes con buena gestion el mes pasado aun no tienen seguimiento efectivo este mes.", "medium", len(pending_best), "Retomar seguimiento"))


def _append_leader_priorities(db: Session, user: User, tenant_id: int, settings: dict[str, int], priorities: list[SessionPriorityOut]) -> None:
    now = _now()
    today_start = _day_start(now)
    month_start = _month_start(now)
    team_ids = _team_user_ids(db, user)
    low_productivity = 0
    for agent_id in team_ids:
        activities_today = db.scalar(select(func.count(ManagementActivity.id)).where(ManagementActivity.tenant_id == tenant_id, ManagementActivity.user_id == agent_id, ManagementActivity.created_at >= today_start)) or 0
        if activities_today == 0:
            low_productivity += 1
    if low_productivity:
        priorities.append(_priority("leader", "low_productivity_advisors", "Gestores sin actividad hoy", "Hay usuarios del equipo sin gestiones registradas durante la jornada.", "high", low_productivity, "Revisar ranking"))

    project_ids = _active_project_ids(db, user)
    if project_ids:
        managed_customers = select(ManagementActivity.customer_id).where(ManagementActivity.tenant_id == tenant_id, ManagementActivity.created_at >= month_start)
        project_stale = db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == tenant_id, Customer.project_id.in_(project_ids), Customer.id.not_in(managed_customers))) or 0
        if project_stale:
            priorities.append(_priority("leader", "portfolio_low_progress", "Cartera con avance bajo", "Existen clientes de carteras asignadas sin gestion en el mes.", "medium", project_stale, "Ajustar reparto"))
        unassigned = db.scalar(select(func.count(Customer.id)).where(Customer.tenant_id == tenant_id, Customer.project_id.in_(project_ids), Customer.assigned_user_id.is_(None))) or 0
        if unassigned:
            priorities.append(_priority("leader", "unassigned_customers", "Clientes sin gestor", "La cartera tiene clientes sin responsable operativo asignado.", "critical", unassigned, "Asignar gestores"))

    due_until = now + timedelta(days=settings["promise_due_in_days"])
    overdue_promises = db.scalar(
        select(func.count(PaymentPromise.id)).where(
            PaymentPromise.tenant_id == tenant_id,
            PaymentPromise.user_id.in_(team_ids or [-1]),
            PaymentPromise.due_date <= due_until,
            PaymentPromise.status.in_(["Vigente", "Vencida", "pending", "active"]),
        )
    ) or 0
    if overdue_promises:
        priorities.append(_priority("leader", "team_due_promises", "Promesas del equipo por vencer", "Coordina seguimiento de promesas vencidas o proximas.", "high", overdue_promises, "Abrir promesas"))


def _append_admin_priorities(db: Session, tenant_id: int, settings: dict[str, int], priorities: list[SessionPriorityOut]) -> None:
    projects = list(db.scalars(select(Project).where(Project.tenant_id == tenant_id).order_by(Project.name).limit(80)))
    without_leader = 0
    without_agent = 0
    for project in projects:
        leader_count = db.scalar(select(func.count(UserProjectAssignment.id)).where(UserProjectAssignment.project_id == project.id, UserProjectAssignment.is_active.is_(True), UserProjectAssignment.role_in_project.in_(["leader", "coordinator"]))) or 0
        agent_count = db.scalar(select(func.count(UserProjectAssignment.id)).where(UserProjectAssignment.project_id == project.id, UserProjectAssignment.is_active.is_(True), UserProjectAssignment.role_in_project == "agent")) or 0
        if not leader_count:
            without_leader += 1
        if not agent_count:
            without_agent += 1
    if without_leader:
        priorities.append(_priority("tenant_admin", "portfolios_without_leader", "Carteras sin lider", "Configura lideres para sostener gobierno operativo por cartera.", "critical", without_leader, "Abrir equipos y carteras"))
    if without_agent:
        priorities.append(_priority("tenant_admin", "portfolios_without_agent", "Carteras sin gestores", "Hay proyectos sin agentes activos asignados.", "high", without_agent, "Asignar usuarios"))

    assigned_users = select(UserProjectAssignment.user_id).where(UserProjectAssignment.tenant_id == tenant_id, UserProjectAssignment.is_active.is_(True))
    users_without_assignment = db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant_id, User.status == "active", User.id.not_in(assigned_users))) or 0
    if users_without_assignment:
        priorities.append(_priority("tenant_admin", "users_without_assignment", "Usuarios sin cartera", "Hay usuarios activos que aun no tienen alcance por cartera.", "medium", users_without_assignment, "Completar asignaciones"))

    disabled_modules = db.scalar(select(func.count(TenantModule.id)).where(TenantModule.tenant_id == tenant_id, or_(TenantModule.enabled.is_(False), TenantModule.is_enabled.is_(False)))) or 0
    if disabled_modules:
        priorities.append(_priority("tenant_admin", "modules_pending_config", "Modulos pendientes de configuracion", "Revisa modulos contratados o parametrizaciones incompletas.", "medium", disabled_modules, "Validar modulos"))

    critical_alerts = db.scalar(select(func.count(GeneratedAlert.id)).where(GeneratedAlert.tenant_id == tenant_id, GeneratedAlert.status == "open", GeneratedAlert.severity.in_(["critical", "high"]))) or 0
    if critical_alerts:
        priorities.append(_priority("tenant_admin", "critical_alerts", "Alertas criticas activas", "Existen alertas operativas abiertas que requieren seguimiento administrativo.", "high", critical_alerts, "Revisar alertas"))

    if not projects:
        priorities.append(_priority("tenant_admin", "no_portfolios", "Sin carteras configuradas", "Crea o activa una cartera para iniciar la operacion de Collects 360.", "critical", 0, "Crear cartera"))


def build_session_summary(db: Session, user: User, tenant_id: int | None = None) -> SessionSummaryOut:
    target_tenant_id = _tenant_for_summary(db, user, tenant_id)
    settings = alert_settings_for_tenant(db, target_tenant_id)
    role_group = _role_group(db, user)
    priorities: list[SessionPriorityOut] = []
    if role_group in {"advisor", "operational"}:
        _append_advisor_priorities(db, user, target_tenant_id, settings, priorities)
    elif role_group == "leader":
        _append_leader_priorities(db, user, target_tenant_id, settings, priorities)
    elif role_group in {"tenant_admin", "platform_admin"}:
        _append_admin_priorities(db, target_tenant_id, settings, priorities)
    priorities = sorted(priorities, key=lambda item: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(item.severity, 2))[:PRIORITY_LIMIT]
    return SessionSummaryOut(role_group=role_group, generated_at=_now(), priorities=priorities, settings=settings)
