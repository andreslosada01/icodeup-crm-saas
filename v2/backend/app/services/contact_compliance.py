from __future__ import annotations

import json
import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import BusinessRule, Customer, CustomerObligation, ManagementActivity, User
from app.services.audit_service import record_audit


CONTACT_RULE_MODULE = "collections"
CONTACT_RULE_TYPE = "contact_compliance"
CONTACT_PAGE_SIZE = 10
DEFAULT_CONTACT_CHANNELS = ["phone", "whatsapp", "email", "sms", "presencial", "web"]
DAY_CODES = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
CHANNEL_ALIASES = {
    "call": "phone",
    "llamada": "phone",
    "telefono": "phone",
    "telefonia": "phone",
    "telephony": "phone",
    "phone": "phone",
    "whatsapp": "whatsapp",
    "email": "email",
    "correo": "email",
    "sms": "sms",
    "presencial": "presencial",
    "web": "web",
    "manual": "manual",
}


def normalize_channel(channel: str | None) -> str:
    value = str(channel or "").strip().lower()
    return CHANNEL_ALIASES.get(value, value or "manual")


def json_dict(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def json_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [value]


def json_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value).strip()
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None


def parse_clock(value: Any) -> time | None:
    if not value:
        return None
    match = re.match(r"^(\d{1,2}):(\d{2})", str(value).strip())
    if not match:
        return None
    hour = min(23, max(0, int(match.group(1))))
    minute = min(59, max(0, int(match.group(2))))
    return time(hour=hour, minute=minute)


def severity_value(rule: BusinessRule, action: dict[str, Any]) -> str:
    raw = str(action.get("severity") or rule.severity or "warning").strip().lower()
    aliases = {
        "informativa": "info",
        "information": "info",
        "low": "info",
        "medium": "warning",
        "advertencia": "warning",
        "warn": "warning",
        "high": "warning",
        "bloqueo": "block",
        "blocked": "block",
        "critical": "block",
        "critica": "block",
    }
    return aliases.get(raw, raw if raw in {"info", "warning", "block"} else "warning")


def priority_value(condition: dict[str, Any], action: dict[str, Any]) -> int:
    return json_int(action.get("priority")) or json_int(condition.get("priority")) or 100


def rule_condition(rule: BusinessRule) -> dict[str, Any]:
    return json_dict(rule.condition_json)


def rule_action(rule: BusinessRule) -> dict[str, Any]:
    return json_dict(rule.action_json)


def contact_rule_to_dict(rule: BusinessRule) -> dict[str, Any]:
    condition = rule_condition(rule)
    action = rule_action(rule)
    return {
        "id": rule.id,
        "tenant_id": rule.tenant_id,
        "project_id": json_int(condition.get("project_id")),
        "code": rule.code,
        "name": rule.name,
        "description": rule.description,
        "channels": [normalize_channel(item) for item in json_list(condition.get("channels"))],
        "blocked_channels": [normalize_channel(item) for item in json_list(condition.get("blocked_channels"))],
        "allowed_days": [str(item).strip().lower() for item in json_list(condition.get("allowed_days"))],
        "start_time": condition.get("start_time"),
        "end_time": condition.get("end_time"),
        "max_attempts_per_day": json_int(condition.get("max_attempts_per_day")),
        "max_attempts_per_week": json_int(condition.get("max_attempts_per_week")),
        "max_attempts_per_channel_day": json_int(condition.get("max_attempts_per_channel_day")),
        "blocked_customer_ids": [int(item) for item in json_list(condition.get("blocked_customer_ids")) if str(item).isdigit()],
        "blocked_obligation_ids": [int(item) for item in json_list(condition.get("blocked_obligation_ids")) if str(item).isdigit()],
        "restricted_contactability_values": [str(item) for item in json_list(condition.get("restricted_contactability_values"))],
        "requires_consent": bool(condition.get("requires_consent", False)),
        "consent_granted": condition.get("consent_granted"),
        "valid_from": condition.get("valid_from"),
        "valid_until": condition.get("valid_until"),
        "severity": severity_value(rule, action),
        "priority": priority_value(condition, action),
        "recommended_action": action.get("recommended_action"),
        "is_active": rule.is_active,
        "condition": condition,
        "action": action,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
    }


def contact_rule_condition(payload: Any) -> dict[str, Any]:
    return {
        "project_id": payload.project_id,
        "channels": [normalize_channel(item) for item in payload.channels],
        "blocked_channels": [normalize_channel(item) for item in payload.blocked_channels],
        "allowed_days": [str(item).strip().lower() for item in payload.allowed_days],
        "start_time": payload.start_time,
        "end_time": payload.end_time,
        "max_attempts_per_day": payload.max_attempts_per_day,
        "max_attempts_per_week": payload.max_attempts_per_week,
        "max_attempts_per_channel_day": payload.max_attempts_per_channel_day,
        "blocked_customer_ids": payload.blocked_customer_ids,
        "blocked_obligation_ids": payload.blocked_obligation_ids,
        "restricted_contactability_values": payload.restricted_contactability_values,
        "requires_consent": payload.requires_consent,
        "consent_granted": payload.consent_granted,
        "valid_from": payload.valid_from,
        "valid_until": payload.valid_until,
        "priority": payload.priority,
    }


def contact_rule_action(payload: Any) -> dict[str, Any]:
    return {
        "severity": payload.severity,
        "recommended_action": payload.recommended_action,
        "priority": payload.priority,
    }


def active_contact_rules(db: Session, tenant_id: int, include_inactive: bool = False) -> list[BusinessRule]:
    query = select(BusinessRule).where(
        BusinessRule.module == CONTACT_RULE_MODULE,
        BusinessRule.rule_type == CONTACT_RULE_TYPE,
        or_(BusinessRule.tenant_id.is_(None), BusinessRule.tenant_id == tenant_id),
    )
    if not include_inactive:
        query = query.where(BusinessRule.is_active.is_(True))
    rules = list(db.scalars(query.order_by(BusinessRule.tenant_id.desc().nullslast(), BusinessRule.severity.desc(), BusinessRule.name)))
    return sorted(rules, key=lambda rule: priority_value(rule_condition(rule), rule_action(rule)))


def rule_scope_matches(rule: BusinessRule, project_id: int | None, current_at: datetime) -> bool:
    condition = rule_condition(rule)
    scoped_project = json_int(condition.get("project_id"))
    scoped_projects = [int(item) for item in json_list(condition.get("project_ids")) if str(item).isdigit()]
    if scoped_project and scoped_project != project_id:
        return False
    if scoped_projects and project_id not in scoped_projects:
        return False
    valid_from = parse_date(condition.get("valid_from"))
    valid_until = parse_date(condition.get("valid_until"))
    current_date = current_at.date()
    if valid_from and current_date < valid_from:
        return False
    if valid_until and current_date > valid_until:
        return False
    return True


def channel_variants(channel: str) -> set[str]:
    normalized = normalize_channel(channel)
    variants = {normalized}
    if normalized == "phone":
        variants.update({"call", "llamada", "telefono", "telefonia", "telephony"})
    return variants


def attempt_counts(db: Session, customer: Customer, channel: str, current_at: datetime) -> tuple[int, int, dict[str, int]]:
    day_start = datetime.combine(current_at.date(), time.min, tzinfo=current_at.tzinfo or timezone.utc)
    week_start = day_start - timedelta(days=day_start.weekday())
    open_channels = DEFAULT_CONTACT_CHANNELS + ["manual"]
    today = db.scalar(
        select(func.count(ManagementActivity.id)).where(
            ManagementActivity.tenant_id == customer.tenant_id,
            ManagementActivity.customer_id == customer.id,
            ManagementActivity.created_at >= day_start,
        )
    ) or 0
    week = db.scalar(
        select(func.count(ManagementActivity.id)).where(
            ManagementActivity.tenant_id == customer.tenant_id,
            ManagementActivity.customer_id == customer.id,
            ManagementActivity.created_at >= week_start,
        )
    ) or 0
    by_channel: dict[str, int] = {}
    for item in open_channels:
        variants = channel_variants(item)
        by_channel[item] = db.scalar(
            select(func.count(ManagementActivity.id)).where(
                ManagementActivity.tenant_id == customer.tenant_id,
                ManagementActivity.customer_id == customer.id,
                ManagementActivity.created_at >= day_start,
                ManagementActivity.channel.in_(list(variants)),
            )
        ) or 0
    normalized = normalize_channel(channel)
    if normalized not in by_channel:
        by_channel[normalized] = 0
    return today, week, by_channel


def outside_time_window(condition: dict[str, Any], current_at: datetime) -> tuple[bool, str | None]:
    start = parse_clock(condition.get("start_time"))
    end = parse_clock(condition.get("end_time"))
    if not start and not end:
        return False, None
    current = current_at.timetz().replace(tzinfo=None)
    if start and end:
        inside = start <= current <= end if start <= end else current >= start or current <= end
        return (not inside), f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
    if start and current < start:
        return True, start.strftime("%H:%M")
    if end and current > end:
        return True, None
    return False, None


def channels_available_from_rules(rules: list[BusinessRule], project_id: int | None, current_at: datetime) -> list[str]:
    configured: set[str] = set()
    blocked: set[str] = set()
    for rule in rules:
        if not rule_scope_matches(rule, project_id, current_at):
            continue
        condition = rule_condition(rule)
        configured.update(normalize_channel(item) for item in json_list(condition.get("channels")) if normalize_channel(item) != "manual")
        blocked.update(normalize_channel(item) for item in json_list(condition.get("blocked_channels")))
    channels = configured or set(DEFAULT_CONTACT_CHANNELS)
    return sorted(channel for channel in channels if channel not in blocked)


def evaluate_contact_rules(
    db: Session,
    *,
    user: User,
    customer: Customer,
    obligation: CustomerObligation | None,
    channel: str,
    current_at: datetime | None = None,
    source: str | None = None,
    audit: bool = False,
    request: Any | None = None,
) -> dict[str, Any]:
    now = current_at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    normalized_channel = normalize_channel(channel)
    project_id = obligation.project_id if obligation and obligation.project_id else customer.project_id
    rules = active_contact_rules(db, customer.tenant_id)
    attempts_today, attempts_week, attempts_by_channel = attempt_counts(db, customer, normalized_channel, now)
    matched: list[dict[str, Any]] = []
    highest = "info"
    reasons: list[str] = []
    recommended_action: str | None = None
    next_window: str | None = None

    severity_rank = {"info": 0, "warning": 1, "block": 2}

    for rule in rules:
        if not rule_scope_matches(rule, project_id, now):
            continue
        condition = rule_condition(rule)
        action = rule_action(rule)
        severity = severity_value(rule, action)
        priority = priority_value(condition, action)
        rule_reasons: list[str] = []
        channels = [normalize_channel(item) for item in json_list(condition.get("channels"))]
        blocked_channels = [normalize_channel(item) for item in json_list(condition.get("blocked_channels"))]
        if channels and normalized_channel not in channels:
            rule_reasons.append("Canal no permitido por la regla configurada.")
        if normalized_channel in blocked_channels:
            rule_reasons.append("Canal bloqueado por regla de cumplimiento.")
        allowed_days = [str(item).strip().lower() for item in json_list(condition.get("allowed_days"))]
        day_code = DAY_CODES[now.weekday()]
        if allowed_days and day_code not in allowed_days:
            rule_reasons.append("Dia no habilitado para contacto.")
        outside_window, window_text = outside_time_window(condition, now)
        if outside_window:
            rule_reasons.append("Fuera del horario permitido de contacto.")
            if window_text:
                next_window = f"Proxima ventana configurada: {window_text}"
        max_day = json_int(condition.get("max_attempts_per_day"))
        max_week = json_int(condition.get("max_attempts_per_week"))
        max_channel = json_int(condition.get("max_attempts_per_channel_day"))
        if max_day is not None and attempts_today >= max_day:
            rule_reasons.append("Maximo de intentos diarios alcanzado.")
        if max_week is not None and attempts_week >= max_week:
            rule_reasons.append("Maximo de intentos semanales alcanzado.")
        if max_channel is not None and attempts_by_channel.get(normalized_channel, 0) >= max_channel:
            rule_reasons.append("Maximo de intentos diarios por canal alcanzado.")
        blocked_customers = [int(item) for item in json_list(condition.get("blocked_customer_ids")) if str(item).isdigit()]
        blocked_obligations = [int(item) for item in json_list(condition.get("blocked_obligation_ids")) if str(item).isdigit()]
        if customer.id in blocked_customers:
            rule_reasons.append("Cliente con restriccion especial activa.")
        if obligation and obligation.id in blocked_obligations:
            rule_reasons.append("Obligacion con restriccion especial activa.")
        restricted_contactability = [str(item).strip().lower() for item in json_list(condition.get("restricted_contactability_values"))]
        if restricted_contactability and str(customer.contactability or "").strip().lower() in restricted_contactability:
            rule_reasons.append("Cliente marcado con contactabilidad restringida.")
        if bool(condition.get("requires_consent")) and condition.get("consent_granted") is False:
            rule_reasons.append("La regla exige consentimiento y no hay autorizacion configurada.")

        if not rule_reasons:
            continue
        if severity_rank[severity] > severity_rank[highest]:
            highest = severity
        if not recommended_action:
            recommended_action = action.get("recommended_action") or "Validar excepcion operativa o programar contacto en ventana permitida."
        reasons.extend(rule_reasons)
        matched.append(
            {
                "id": rule.id,
                "code": rule.code,
                "name": rule.name,
                "severity": severity,
                "decision": "bloqueo" if severity == "block" else "advertencia" if severity == "warning" else "informativa",
                "reason": "; ".join(rule_reasons),
                "priority": priority,
            }
        )

    if not matched:
        reason = "Contacto permitido. No hay restricciones activas para este contexto."
    else:
        reason = "Contacto restringido por regla de cumplimiento" if highest == "block" else "; ".join(dict.fromkeys(reasons))
    decision = {
        "allowed": highest != "block",
        "severity": highest,
        "reason": reason,
        "matched_rules": matched,
        "recommended_action": recommended_action or ("Continuar gestion normal." if highest == "info" else "Revisar reglas de cumplimiento antes de contactar."),
        "channels_available": channels_available_from_rules(rules, project_id, now),
        "attempts_today": attempts_today,
        "attempts_week": attempts_week,
        "attempts_by_channel_today": attempts_by_channel,
        "next_window": next_window,
    }
    if audit:
        action = "contact_blocked" if not decision["allowed"] else "contact_warning" if decision["severity"] == "warning" else "contact_allowed"
        record_audit(
            db,
            user,
            "contact_compliance",
            action,
            entity_id=customer.id,
            tenant_id=customer.tenant_id,
            module="collections",
            object_type="customer",
            object_id=customer.id,
            after={
                "customer_id": customer.id,
                "project_id": project_id,
                "obligation_id": obligation.id if obligation else None,
                "channel": normalized_channel,
                "source": source,
                "allowed": decision["allowed"],
                "severity": decision["severity"],
                "reason": decision["reason"],
                "matched_rule_codes": [item["code"] for item in matched],
            },
            request=request,
        )
    return decision


def customer_contact_status(db: Session, user: User, customer: Customer) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    rules = active_contact_rules(db, customer.tenant_id)
    project_id = customer.project_id
    attempts_today, attempts_week, attempts_by_channel = attempt_counts(db, customer, "phone", now)
    channel_decisions = {
        channel: evaluate_contact_rules(db, user=user, customer=customer, obligation=None, channel=channel, current_at=now, audit=False)
        for channel in DEFAULT_CONTACT_CHANNELS
    }
    blocked = [decision for decision in channel_decisions.values() if not decision["allowed"]]
    warnings = [decision for decision in channel_decisions.values() if decision["severity"] == "warning"]
    allowed = [decision for decision in channel_decisions.values() if decision["allowed"]]
    status_value = "bloqueado" if blocked and not allowed else "advertencia" if blocked or warnings else "permitido"
    severity = "block" if blocked and not allowed else "warning" if blocked or warnings else "info"
    reason = (
        blocked[0]["reason"] if blocked and not allowed
        else "Algunos canales tienen restricciones activas." if blocked
        else warnings[0]["reason"] if warnings
        else "Contacto permitido segun reglas activas."
    )
    active_restrictions: list[dict[str, Any]] = []
    for decision in channel_decisions.values():
        active_restrictions.extend(decision["matched_rules"])
    by_code: dict[str, dict[str, Any]] = {}
    for item in active_restrictions:
        by_code.setdefault(item["code"], item)
    last_contact_by_channel: dict[str, str | None] = {}
    for channel in DEFAULT_CONTACT_CHANNELS:
        variants = channel_variants(channel)
        last_contact = db.scalar(
            select(ManagementActivity.created_at)
            .where(
                ManagementActivity.tenant_id == customer.tenant_id,
                ManagementActivity.customer_id == customer.id,
                ManagementActivity.channel.in_(list(variants)),
            )
            .order_by(ManagementActivity.created_at.desc())
            .limit(1)
        )
        last_contact_by_channel[channel] = last_contact.isoformat() if last_contact else None
    return {
        "customer_id": customer.id,
        "tenant_id": customer.tenant_id,
        "project_id": project_id,
        "status": status_value,
        "severity": severity,
        "reason": reason,
        "channels_enabled": channels_available_from_rules(rules, project_id, now),
        "last_contact_by_channel": last_contact_by_channel,
        "attempts_today": attempts_today,
        "attempts_week": attempts_week,
        "attempts_by_channel_today": attempts_by_channel,
        "active_restrictions": list(by_code.values()),
        "next_window": next((decision["next_window"] for decision in channel_decisions.values() if decision.get("next_window")), None),
    }
