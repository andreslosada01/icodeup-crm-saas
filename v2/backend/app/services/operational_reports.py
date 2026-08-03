from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date as date_type, datetime, time, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.roles import AGENT, COORDINATOR, QUALITY_SUPERVISOR
from app.models import (
    CallLog,
    Customer,
    CustomerDemographic,
    CustomerObligation,
    ManagementActivity,
    Payment,
    PaymentAgreement,
    PaymentAgreementInstallment,
    PaymentPromise,
    Project,
    Tenant,
    TenantModule,
    TypificationNode,
    User,
    UserProjectAssignment,
)
from app.models.careflow import CareCase
from app.services.access_control import get_profile_role_code, is_company_admin, is_platform_admin, require_module, require_permission, user_has_module
from app.services.collections_self_service import advisor_management_insights, customer_management_insights, score_activity
from app.services.contact_compliance import customer_contact_status, evaluate_contact_rules, normalize_channel


REPORT_PAGE_SIZE = 10
REPORT_EXPORT_LIMIT = 500
ACTIVE_PROMISE_STATUSES = {"Vigente", "vigente", "active", "pending"}
ACTIVE_AGREEMENT_STATUSES = {"active", "vigente", "Vigente"}
CONTACT_RESTRICTED_VALUES = {"restringida", "no contactar", "bloqueado", "baja"}

REPORT_LABELS = {
    "clients": "Clientes",
    "activities": "Gestion",
    "promises": "Promesas",
    "payments": "Pagos",
    "agreements": "Acuerdos",
    "productivity-hourly": "Productividad por hora",
    "productivity-advisor": "Productividad por asesor",
    "demographics": "Demograficos",
    "tasks": "Tareas y agendados",
    "careflow": "CareFlow 360",
}


@dataclass
class OperationalReportFilters:
    tenant_id: int | None = None
    project_id: int | None = None
    user_id: int | None = None
    advisor_id: int | None = None
    leader_id: int | None = None
    date_from: date_type | None = None
    date_to: date_type | None = None
    status: str | None = None
    channel: str | None = None
    result: str | None = None
    risk: str | None = None
    search: str | None = None
    typification: str | None = None
    min_score: int | None = None
    effective: bool | None = None
    min_dpd: int | None = None
    max_dpd: int | None = None
    min_balance: int | None = None
    max_balance: int | None = None
    no_management: bool | None = None
    active_promise: bool | None = None
    contact_restriction: bool | None = None
    overdue: bool | None = None
    fulfilled: bool | None = None
    page: int = 1
    page_size: int = REPORT_PAGE_SIZE

    @property
    def advisor_filter(self) -> int | None:
        return self.advisor_id or self.user_id


def ensure_operational_reports_access(db: Session, user: User, tenant_id: int | None = None) -> None:
    require_permission(db, user, "reports.view")
    profile = get_profile_role_code(db, user)
    if user.role == AGENT or profile == "collections_agent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los reportes operativos completos no estan disponibles para agentes.")
    if not is_platform_admin(db, user):
        require_module(db, user, "bi", tenant_id or user.tenant_id)


def available_reports(db: Session, user: User, tenant_id: int | None = None) -> list[dict[str, Any]]:
    ensure_operational_reports_access(db, user, tenant_id)
    reports = []
    careflow_active = _careflow_module_active(db, user, tenant_id)
    for code, label in REPORT_LABELS.items():
        if code == "careflow" and not careflow_active:
            continue
        reports.append({"code": code, "label": label, "module": "careflow" if code == "careflow" else "collections"})
    return reports


def build_operational_report(db: Session, user: User, report_code: str, filters: OperationalReportFilters, max_page_size: int = REPORT_PAGE_SIZE) -> dict[str, Any]:
    ensure_operational_reports_access(db, user, filters.tenant_id)
    filters.page = max(1, int(filters.page or 1))
    filters.page_size = min(max_page_size, max(1, int(filters.page_size or REPORT_PAGE_SIZE)))
    builders = {
        "clients": clients_report,
        "activities": activities_report,
        "promises": promises_report,
        "payments": payments_report,
        "agreements": agreements_report,
        "productivity-hourly": productivity_hourly_report,
        "productivity-advisor": productivity_advisor_report,
        "demographics": demographics_report,
        "tasks": tasks_report,
        "careflow": careflow_report,
    }
    if report_code not in builders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte operativo no soportado.")
    return builders[report_code](db, user, filters)


def build_operational_report_export(db: Session, user: User, report_code: str, filters: OperationalReportFilters) -> dict[str, Any]:
    filters.page = 1
    filters.page_size = REPORT_EXPORT_LIMIT
    result = build_operational_report(db, user, report_code, filters, max_page_size=REPORT_EXPORT_LIMIT)
    result["note"] = (result.get("note") or "Exportacion CSV acotada a registros visibles y filtros autorizados.")
    return result


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _date_from(value: date_type | None) -> datetime | None:
    return datetime.combine(value, time.min, tzinfo=timezone.utc) if value else None


def _date_to(value: date_type | None) -> datetime | None:
    return datetime.combine(value, time.max, tzinfo=timezone.utc) if value else None


def _page_slice(items: list[dict[str, Any]], page: int, page_size: int) -> tuple[list[dict[str, Any]], int]:
    total = len(items)
    offset = (page - 1) * page_size
    return items[offset:offset + page_size], total


def _count_query(db: Session, query) -> int:
    return db.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0


def _query_page(db: Session, query, page: int, page_size: int) -> tuple[list[Any], int]:
    total = _count_query(db, query)
    items = list(db.scalars(query.offset((page - 1) * page_size).limit(page_size)))
    return items, total


def _response(
    report: str,
    filters: OperationalReportFilters,
    columns: list[dict[str, str]],
    items: list[dict[str, Any]],
    total: int,
    kpis: list[dict[str, Any]] | None = None,
    available: bool = True,
    note: str | None = None,
) -> dict[str, Any]:
    page_size = max(1, int(filters.page_size or REPORT_PAGE_SIZE))
    return {
        "report": report,
        "title": REPORT_LABELS[report],
        "generated_at": _now(),
        "available": available,
        "note": note,
        "columns": columns,
        "kpis": kpis or [],
        "items": items,
        "total": total,
        "page": filters.page,
        "page_size": page_size,
        "total_pages": max(1, math.ceil(total / page_size)),
        "filters": {key: value for key, value in asdict(filters).items() if value not in (None, "")},
    }


def _role_is_leader(db: Session, user: User) -> bool:
    profile = get_profile_role_code(db, user)
    return user.role == COORDINATOR or profile in {"collections_leader", "operational_leader", "sales_leader", "legal_director"}


def _role_is_quality(db: Session, user: User) -> bool:
    profile = get_profile_role_code(db, user)
    return user.role == QUALITY_SUPERVISOR or profile == "tenant_auditor"


def _active_project_ids(db: Session, user: User) -> list[int]:
    return list(
        db.scalars(
            select(UserProjectAssignment.project_id).where(
                UserProjectAssignment.user_id == user.id,
                UserProjectAssignment.is_active.is_(True),
            )
        )
    )


def _team_user_ids(db: Session, user: User) -> list[int]:
    ids = [user.id]
    ids.extend(db.scalars(select(User.id).where(User.tenant_id == user.tenant_id, User.leader_id == user.id, User.status == "active")))
    return list(dict.fromkeys(ids))


def _visible_customer_query(db: Session, user: User, filters: OperationalReportFilters):
    query = select(Customer).where(Customer.tenant_id.is_not(None))
    if is_platform_admin(db, user):
        if filters.tenant_id:
            query = query.where(Customer.tenant_id == filters.tenant_id)
    else:
        query = query.where(Customer.tenant_id == user.tenant_id)
        if is_company_admin(db, user):
            pass
        elif _role_is_leader(db, user):
            project_ids = _active_project_ids(db, user)
            conditions = [Customer.assigned_user_id.in_(_team_user_ids(db, user))]
            if project_ids:
                conditions.append(Customer.project_id.in_(project_ids))
            query = query.where(or_(*conditions))
        elif _role_is_quality(db, user):
            project_ids = _active_project_ids(db, user)
            if project_ids:
                query = query.where(Customer.project_id.in_(project_ids))
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol sin acceso al centro de reportes operativos.")
    if filters.project_id:
        query = query.where(Customer.project_id == filters.project_id)
    if filters.advisor_filter:
        query = query.where(Customer.assigned_user_id == filters.advisor_filter)
    if filters.leader_id:
        leader_users = select(User.id).where(User.tenant_id == Customer.tenant_id, User.leader_id == filters.leader_id)
        leader_obligations = select(CustomerObligation.customer_id).where(
            CustomerObligation.tenant_id == Customer.tenant_id,
            CustomerObligation.assigned_leader_id == filters.leader_id,
        )
        query = query.where(or_(Customer.assigned_user_id.in_(leader_users), Customer.id.in_(leader_obligations)))
    if filters.status:
        query = query.where(Customer.status == filters.status)
    if filters.risk:
        query = query.where(Customer.risk == filters.risk)
    if filters.min_dpd is not None:
        query = query.where(Customer.dpd >= filters.min_dpd)
    if filters.max_dpd is not None:
        query = query.where(Customer.dpd <= filters.max_dpd)
    if filters.min_balance is not None:
        query = query.where(Customer.balance >= filters.min_balance)
    if filters.max_balance is not None:
        query = query.where(Customer.balance <= filters.max_balance)
    if filters.search:
        pattern = f"%{filters.search.strip()}%"
        query = query.where(or_(Customer.name.ilike(pattern), Customer.document.ilike(pattern), Customer.phone.ilike(pattern), Customer.email.ilike(pattern)))
    if filters.no_management:
        managed = select(ManagementActivity.customer_id).where(ManagementActivity.tenant_id == Customer.tenant_id)
        query = query.where(Customer.id.not_in(managed))
    if filters.active_promise:
        active_promises = select(PaymentPromise.customer_id).where(
            PaymentPromise.tenant_id == Customer.tenant_id,
            PaymentPromise.status.in_(list(ACTIVE_PROMISE_STATUSES)),
        )
        query = query.where(Customer.id.in_(active_promises))
    if filters.contact_restriction:
        query = query.where(or_(func.lower(Customer.contactability).in_(CONTACT_RESTRICTED_VALUES), func.lower(Customer.status).like("%no contactar%")))
    return query


def _visible_customer_subquery(db: Session, user: User, filters: OperationalReportFilters):
    return _visible_customer_query(db, user, filters).subquery()


def _tenant_name(db: Session, tenant_id: int | None) -> str:
    tenant = db.get(Tenant, tenant_id) if tenant_id else None
    return tenant.name if tenant else "-"


def _project_name(db: Session, project_id: int | None) -> str:
    project = db.get(Project, project_id) if project_id else None
    return project.name if project else "-"


def _user_name(db: Session, user_id: int | None) -> str:
    user = db.get(User, user_id) if user_id else None
    return user.name if user else "-"


def _obligation_label(db: Session, obligation_id: int | None) -> str:
    obligation = db.get(CustomerObligation, obligation_id) if obligation_id else None
    return obligation.obligation_number if obligation else "-"


def _customer_obligations(db: Session, customer: Customer) -> list[CustomerObligation]:
    return list(db.scalars(select(CustomerObligation).where(CustomerObligation.tenant_id == customer.tenant_id, CustomerObligation.customer_id == customer.id)))


def _customer_balance_and_dpd(db: Session, customer: Customer) -> tuple[int, int, str, int | None]:
    obligations = _customer_obligations(db, customer)
    if not obligations:
        return customer.balance, customer.dpd, customer.risk, None
    balance = sum(item.current_balance for item in obligations)
    dpd = max(item.days_past_due for item in obligations)
    risk = sorted(obligations, key=lambda item: (item.days_past_due, item.current_balance), reverse=True)[0].risk
    leader_id = next((item.assigned_leader_id for item in obligations if item.assigned_leader_id), None)
    return balance, dpd, risk, leader_id


def _last_activity(db: Session, customer_id: int, tenant_id: int) -> ManagementActivity | None:
    return db.scalar(
        select(ManagementActivity)
        .where(ManagementActivity.tenant_id == tenant_id, ManagementActivity.customer_id == customer_id)
        .order_by(ManagementActivity.created_at.desc(), ManagementActivity.id.desc())
        .limit(1)
    )


def _active_promise(db: Session, customer_id: int, tenant_id: int) -> PaymentPromise | None:
    return db.scalar(
        select(PaymentPromise)
        .where(PaymentPromise.tenant_id == tenant_id, PaymentPromise.customer_id == customer_id, PaymentPromise.status.in_(list(ACTIVE_PROMISE_STATUSES)))
        .order_by(PaymentPromise.due_date.asc())
        .limit(1)
    )


def _active_agreement(db: Session, customer_id: int, tenant_id: int) -> PaymentAgreement | None:
    return db.scalar(
        select(PaymentAgreement)
        .where(PaymentAgreement.tenant_id == tenant_id, PaymentAgreement.customer_id == customer_id, PaymentAgreement.status.in_(list(ACTIVE_AGREEMENT_STATUSES)))
        .order_by(PaymentAgreement.created_at.desc())
        .limit(1)
    )


def _agreement_installments(db: Session, agreement_id: int) -> list[PaymentAgreementInstallment]:
    return list(db.scalars(select(PaymentAgreementInstallment).where(PaymentAgreementInstallment.agreement_id == agreement_id).order_by(PaymentAgreementInstallment.due_date)))


def _date_filters(query, column, filters: OperationalReportFilters):
    start = _date_from(filters.date_from)
    end = _date_to(filters.date_to)
    if start:
        query = query.where(column >= start)
    if end:
        query = query.where(column <= end)
    return query


def _effective_bool(value: bool | None, score_is_effective: bool) -> bool:
    return value is None or bool(value) == score_is_effective


def _safe_score(db: Session, activity: ManagementActivity):
    try:
        return score_activity(db, activity)
    except Exception:
        return None


def _activity_compliance(db: Session, user: User, activity: ManagementActivity, customer: Customer | None) -> dict[str, Any]:
    if not customer:
        return {"status": "sin_cliente", "allowed": True, "reason": "Cliente no disponible para evaluar cumplimiento."}
    channel = normalize_channel(activity.channel)
    if channel not in {"phone", "whatsapp", "email", "sms"}:
        return {"status": "no_aplica", "allowed": True, "reason": "Canal no sujeto a regla de contacto."}
    decision = evaluate_contact_rules(db, user=user, customer=customer, obligation=None, channel=channel, current_at=activity.created_at, source="operational_reports", audit=False)
    return {"status": "permitido" if decision["allowed"] else "bloqueado", "allowed": decision["allowed"], "reason": decision["reason"]}


def clients_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    query = _visible_customer_query(db, user, filters).order_by(Customer.priority.desc(), Customer.dpd.desc(), Customer.balance.desc())
    customers, total = _query_page(db, query, filters.page, filters.page_size)
    scope = query.order_by(None).subquery()
    total_balance = db.scalar(select(func.coalesce(func.sum(scope.c.balance), 0))) or 0
    no_management = db.scalar(
        select(func.count()).select_from(scope).where(
            scope.c.id.not_in(select(ManagementActivity.customer_id).where(ManagementActivity.tenant_id == scope.c.tenant_id))
        )
    ) or 0
    rows = []
    for customer in customers:
        balance, dpd, risk, obligation_leader_id = _customer_balance_and_dpd(db, customer)
        assigned = db.get(User, customer.assigned_user_id) if customer.assigned_user_id else None
        leader_id = obligation_leader_id or assigned.leader_id if assigned else obligation_leader_id
        last = _last_activity(db, customer.id, customer.tenant_id)
        promise = _active_promise(db, customer.id, customer.tenant_id)
        agreement = _active_agreement(db, customer.id, customer.tenant_id)
        insights = customer_management_insights(db, customer)
        contact = customer_contact_status(db, user, customer)
        rows.append(
            {
                "tenant": _tenant_name(db, customer.tenant_id),
                "project": _project_name(db, customer.project_id),
                "customer": customer.name,
                "document": customer.document,
                "status": customer.status,
                "total_balance": balance,
                "dpd": dpd,
                "risk": risk,
                "advisor": assigned.name if assigned else "-",
                "leader": _user_name(db, leader_id),
                "last_activity": last.created_at if last else None,
                "best_month": insights.best_current_month.result if insights.best_current_month else "-",
                "best_historical": insights.best_historical.result if insights.best_historical else "-",
                "active_promise": "Si" if promise else "No",
                "active_agreement": "Si" if agreement else "No",
                "contact_restriction": contact["status"] if contact else "sin_reglas",
            }
        )
    return _response(
        "clients",
        filters,
        [
            {"key": "tenant", "label": "Empresa"},
            {"key": "project", "label": "Cartera"},
            {"key": "customer", "label": "Cliente"},
            {"key": "document", "label": "Documento"},
            {"key": "status", "label": "Estado"},
            {"key": "total_balance", "label": "Saldo", "type": "money"},
            {"key": "dpd", "label": "Mora"},
            {"key": "risk", "label": "Riesgo"},
            {"key": "advisor", "label": "Asesor"},
            {"key": "leader", "label": "Lider"},
            {"key": "last_activity", "label": "Ultima gestion", "type": "date"},
            {"key": "best_month", "label": "Mejor mes"},
            {"key": "best_historical", "label": "Mejor historica"},
            {"key": "active_promise", "label": "Promesa"},
            {"key": "active_agreement", "label": "Acuerdo"},
            {"key": "contact_restriction", "label": "Contacto"},
        ],
        rows,
        total,
        [
            {"key": "customers", "label": "Clientes", "value": total, "tone": "blue"},
            {"key": "balance", "label": "Saldo visible", "value": int(total_balance), "tone": "green"},
            {"key": "no_management", "label": "Sin gestion", "value": no_management, "tone": "yellow"},
        ],
    )


def _activities_query(db: Session, user: User, filters: OperationalReportFilters):
    visible = _visible_customer_subquery(db, user, filters)
    query = select(ManagementActivity).where(
        ManagementActivity.customer_id.in_(select(visible.c.id)),
        ManagementActivity.tenant_id.in_(select(visible.c.tenant_id)),
    )
    query = _date_filters(query, ManagementActivity.created_at, filters)
    if filters.project_id:
        query = query.where(ManagementActivity.project_id == filters.project_id)
    if filters.advisor_filter:
        query = query.where(ManagementActivity.user_id == filters.advisor_filter)
    if filters.channel:
        query = query.where(ManagementActivity.channel == filters.channel)
    if filters.result or filters.status:
        query = query.where(ManagementActivity.result.ilike(f"%{(filters.result or filters.status).strip()}%"))
    if filters.typification:
        typification_ids = select(TypificationNode.id).where(TypificationNode.label.ilike(f"%{filters.typification.strip()}%"))
        query = query.where(ManagementActivity.typification_id.in_(typification_ids))
    if filters.search:
        pattern = f"%{filters.search.strip()}%"
        query = query.where(or_(ManagementActivity.result.ilike(pattern), ManagementActivity.note.ilike(pattern)))
    return query.order_by(ManagementActivity.created_at.desc(), ManagementActivity.id.desc())


def _activity_row(db: Session, user: User, activity: ManagementActivity, scored=None) -> dict[str, Any]:
    customer = db.get(Customer, activity.customer_id)
    assigned = db.get(User, activity.user_id)
    typification = db.get(TypificationNode, activity.typification_id) if activity.typification_id else None
    scored = scored or _safe_score(db, activity)
    compliance = _activity_compliance(db, user, activity, customer)
    promise = _active_promise(db, activity.customer_id, activity.tenant_id)
    return {
        "created_at": activity.created_at,
        "customer": customer.name if customer else "-",
        "obligation": _obligation_label(db, activity.obligation_id),
        "advisor": assigned.name if assigned else "-",
        "leader": _user_name(db, assigned.leader_id if assigned else None),
        "project": _project_name(db, activity.project_id),
        "channel": activity.channel,
        "typification": typification.label if typification else "-",
        "result": activity.result,
        "summary": activity.note or "-",
        "score": scored.score if scored else 0,
        "effective": "Si" if scored and scored.is_effective else "No",
        "next_date": activity.next_contact_at,
        "promise": promise.due_date if promise else None,
        "contact_compliance": compliance["status"],
    }


def activities_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    query = _activities_query(db, user, filters)
    if filters.min_score is not None or filters.effective is not None:
        scored_rows = []
        for activity in db.scalars(query):
            scored = _safe_score(db, activity)
            if filters.min_score is not None and (not scored or scored.score < filters.min_score):
                continue
            if scored and not _effective_bool(filters.effective, scored.is_effective):
                continue
            scored_rows.append(_activity_row(db, user, activity, scored))
        rows, total = _page_slice(scored_rows, filters.page, filters.page_size)
    else:
        activities, total = _query_page(db, query, filters.page, filters.page_size)
        rows = [_activity_row(db, user, item) for item in activities]
    avg_score = round(sum(int(item.get("score") or 0) for item in rows) / max(len(rows), 1))
    return _response(
        "activities",
        filters,
        [
            {"key": "created_at", "label": "Fecha", "type": "date"},
            {"key": "customer", "label": "Cliente"},
            {"key": "obligation", "label": "Obligacion"},
            {"key": "advisor", "label": "Asesor"},
            {"key": "leader", "label": "Lider"},
            {"key": "project", "label": "Cartera"},
            {"key": "channel", "label": "Canal"},
            {"key": "typification", "label": "Tipificacion"},
            {"key": "result", "label": "Resultado"},
            {"key": "summary", "label": "Resumen"},
            {"key": "score", "label": "Score"},
            {"key": "effective", "label": "Efectiva"},
            {"key": "next_date", "label": "Proxima fecha", "type": "date"},
            {"key": "promise", "label": "Promesa asociada", "type": "date"},
            {"key": "contact_compliance", "label": "Cumplimiento"},
        ],
        rows,
        total,
        [
            {"key": "activities", "label": "Gestiones", "value": total, "tone": "blue"},
            {"key": "avg_score", "label": "Score promedio", "value": avg_score, "tone": "green" if avg_score >= 65 else "yellow"},
        ],
    )


def promises_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    visible = _visible_customer_subquery(db, user, filters)
    query = select(PaymentPromise).where(PaymentPromise.customer_id.in_(select(visible.c.id)), PaymentPromise.tenant_id.in_(select(visible.c.tenant_id)))
    query = _date_filters(query, PaymentPromise.due_date, filters)
    if filters.project_id:
        query = query.where(PaymentPromise.project_id == filters.project_id)
    if filters.advisor_filter:
        query = query.where(PaymentPromise.user_id == filters.advisor_filter)
    if filters.status:
        query = query.where(PaymentPromise.status == filters.status)
    now = _now()
    if filters.overdue is not None:
        query = query.where(PaymentPromise.due_date < now if filters.overdue else PaymentPromise.due_date >= now)
    if filters.fulfilled is not None:
        complete_statuses = {"Cumplida", "completed", "paid"}
        query = query.where(PaymentPromise.status.in_(list(complete_statuses)) if filters.fulfilled else PaymentPromise.status.not_in(list(complete_statuses)))
    query = query.order_by(PaymentPromise.due_date.asc(), PaymentPromise.id.desc())
    promises, total = _query_page(db, query, filters.page, filters.page_size)
    rows = []
    for promise in promises:
        customer = db.get(Customer, promise.customer_id)
        payment = db.scalar(
            select(Payment)
            .where(Payment.tenant_id == promise.tenant_id, Payment.customer_id == promise.customer_id, Payment.paid_at >= promise.created_at)
            .order_by(Payment.paid_at.desc())
            .limit(1)
        )
        overdue_days = max(0, (_now().date() - promise.due_date.date()).days)
        rows.append(
            {
                "customer": customer.name if customer else "-",
                "obligation": _obligation_label(db, promise.obligation_id),
                "advisor": _user_name(db, promise.user_id),
                "project": _project_name(db, promise.project_id),
                "promise_date": promise.due_date,
                "amount": promise.amount,
                "status": promise.status,
                "overdue": "Si" if promise.due_date < now else "No",
                "fulfilled": "Si" if promise.status in {"Cumplida", "completed", "paid"} or payment else "No",
                "payment": payment.reference if payment else "-",
                "overdue_days": overdue_days,
            }
        )
    promise_scope = query.order_by(None).subquery()
    amount_total = db.scalar(select(func.coalesce(func.sum(promise_scope.c.amount), 0))) or 0
    return _response(
        "promises",
        filters,
        [
            {"key": "customer", "label": "Cliente"},
            {"key": "obligation", "label": "Obligacion"},
            {"key": "advisor", "label": "Asesor"},
            {"key": "project", "label": "Cartera"},
            {"key": "promise_date", "label": "Fecha promesa", "type": "date"},
            {"key": "amount", "label": "Valor", "type": "money"},
            {"key": "status", "label": "Estado"},
            {"key": "overdue", "label": "Vencida"},
            {"key": "fulfilled", "label": "Cumplida"},
            {"key": "payment", "label": "Pago asociado"},
            {"key": "overdue_days", "label": "Dias vencimiento"},
        ],
        rows,
        total,
        [{"key": "amount", "label": "Valor promesas", "value": int(amount_total), "tone": "green"}],
    )


def payments_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    visible = _visible_customer_subquery(db, user, filters)
    query = select(Payment).where(Payment.customer_id.in_(select(visible.c.id)), Payment.tenant_id.in_(select(visible.c.tenant_id)))
    query = _date_filters(query, Payment.paid_at, filters)
    if filters.project_id:
        query = query.where(Payment.project_id == filters.project_id)
    if filters.advisor_filter:
        query = query.where(Payment.user_id == filters.advisor_filter)
    if filters.search:
        query = query.where(or_(Payment.reference.ilike(f"%{filters.search.strip()}%"), Payment.method.ilike(f"%{filters.search.strip()}%")))
    query = query.order_by(Payment.paid_at.desc(), Payment.id.desc())
    payments, total = _query_page(db, query, filters.page, filters.page_size)
    rows = []
    for payment in payments:
        customer = db.get(Customer, payment.customer_id)
        promise = db.scalar(select(PaymentPromise).where(PaymentPromise.tenant_id == payment.tenant_id, PaymentPromise.customer_id == payment.customer_id).order_by(PaymentPromise.created_at.desc()).limit(1))
        agreement = db.scalar(select(PaymentAgreement).where(PaymentAgreement.tenant_id == payment.tenant_id, PaymentAgreement.customer_id == payment.customer_id).order_by(PaymentAgreement.created_at.desc()).limit(1))
        rows.append(
            {
                "customer": customer.name if customer else "-",
                "obligation": _obligation_label(db, payment.obligation_id),
                "advisor": _user_name(db, payment.user_id),
                "project": _project_name(db, payment.project_id),
                "paid_at": payment.paid_at,
                "amount": payment.amount,
                "origin": payment.method,
                "validation_status": "Registrado",
                "reference": payment.reference or "-",
                "relation": promise.status if promise else agreement.status if agreement else "-",
            }
        )
    payment_scope = query.order_by(None).subquery()
    amount_total = db.scalar(select(func.coalesce(func.sum(payment_scope.c.amount), 0))) or 0
    return _response(
        "payments",
        filters,
        [
            {"key": "customer", "label": "Cliente"},
            {"key": "obligation", "label": "Obligacion"},
            {"key": "advisor", "label": "Asesor"},
            {"key": "project", "label": "Cartera"},
            {"key": "paid_at", "label": "Fecha pago", "type": "date"},
            {"key": "amount", "label": "Valor", "type": "money"},
            {"key": "origin", "label": "Origen"},
            {"key": "validation_status", "label": "Validacion"},
            {"key": "reference", "label": "Referencia"},
            {"key": "relation", "label": "Promesa/acuerdo"},
        ],
        rows,
        total,
        [{"key": "amount", "label": "Valor pagos", "value": int(amount_total), "tone": "green"}],
    )


def agreements_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    visible = _visible_customer_subquery(db, user, filters)
    query = select(PaymentAgreement).where(PaymentAgreement.customer_id.in_(select(visible.c.id)), PaymentAgreement.tenant_id.in_(select(visible.c.tenant_id)))
    query = _date_filters(query, PaymentAgreement.start_date, filters)
    if filters.project_id:
        query = query.where(PaymentAgreement.project_id == filters.project_id)
    if filters.advisor_filter:
        query = query.where(PaymentAgreement.user_id == filters.advisor_filter)
    if filters.status:
        query = query.where(PaymentAgreement.status == filters.status)
    query = query.order_by(PaymentAgreement.created_at.desc(), PaymentAgreement.id.desc())
    agreements, total = _query_page(db, query, filters.page, filters.page_size)
    rows = []
    now = _now()
    for agreement in agreements:
        customer = db.get(Customer, agreement.customer_id)
        installments = _agreement_installments(db, agreement.id)
        paid = [item for item in installments if item.status == "paid" or item.paid_amount >= item.amount]
        overdue = [item for item in installments if item.status != "paid" and item.due_date < now]
        next_due = next((item for item in installments if item.status != "paid" and item.due_date >= now), None)
        rows.append(
            {
                "customer": customer.name if customer else "-",
                "obligation": _obligation_label(db, agreement.obligation_id),
                "advisor": _user_name(db, agreement.user_id),
                "project": _project_name(db, agreement.project_id),
                "agreement_date": agreement.start_date,
                "total_amount": agreement.total_amount,
                "installments": agreement.installment_count,
                "paid_installments": len(paid),
                "overdue_installments": len(overdue),
                "status": agreement.status,
                "next_due": next_due.due_date if next_due else None,
            }
        )
    agreement_scope = query.order_by(None).subquery()
    total_amount = db.scalar(select(func.coalesce(func.sum(agreement_scope.c.total_amount), 0))) or 0
    return _response(
        "agreements",
        filters,
        [
            {"key": "customer", "label": "Cliente"},
            {"key": "obligation", "label": "Obligacion"},
            {"key": "advisor", "label": "Asesor"},
            {"key": "project", "label": "Cartera"},
            {"key": "agreement_date", "label": "Fecha acuerdo", "type": "date"},
            {"key": "total_amount", "label": "Valor total", "type": "money"},
            {"key": "installments", "label": "Cuotas"},
            {"key": "paid_installments", "label": "Pagadas"},
            {"key": "overdue_installments", "label": "Vencidas"},
            {"key": "status", "label": "Estado"},
            {"key": "next_due", "label": "Proximo vencimiento", "type": "date"},
        ],
        rows,
        total,
        [{"key": "amount", "label": "Valor acuerdos", "value": int(total_amount), "tone": "green"}],
    )


def productivity_hourly_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    activities = list(db.scalars(_activities_query(db, user, filters)))
    groups: dict[tuple[str, int, int, int | None], dict[str, Any]] = {}
    for activity in activities:
        key = (activity.created_at.date().isoformat(), activity.created_at.hour, activity.user_id, activity.project_id)
        row = groups.setdefault(
            key,
            {
                "date": activity.created_at.date().isoformat(),
                "hour": activity.created_at.hour,
                "advisor": _user_name(db, activity.user_id),
                "project": _project_name(db, activity.project_id),
                "activities": 0,
                "calls": 0,
                "whatsapp": 0,
                "email": 0,
                "promises": 0,
                "payments": 0,
                "agreements": 0,
                "effective_contacts": 0,
                "_scores": [],
            },
        )
        row["activities"] += 1
        channel = normalize_channel(activity.channel)
        if channel == "phone":
            row["calls"] += 1
        if channel == "whatsapp":
            row["whatsapp"] += 1
        if channel == "email":
            row["email"] += 1
        scored = _safe_score(db, activity)
        if scored:
            row["_scores"].append(scored.score)
            if scored.is_effective:
                row["effective_contacts"] += 1
    _append_hourly_counts(db, user, filters, groups, PaymentPromise, PaymentPromise.created_at, "promises")
    _append_hourly_counts(db, user, filters, groups, Payment, Payment.paid_at, "payments")
    _append_hourly_counts(db, user, filters, groups, PaymentAgreement, PaymentAgreement.created_at, "agreements")
    _append_call_log_counts(db, user, filters, groups)
    rows = []
    for row in groups.values():
        scores = row.pop("_scores")
        row["avg_score"] = round(sum(scores) / max(len(scores), 1))
        rows.append(row)
    rows.sort(key=lambda item: (item["date"], item["hour"], item["advisor"]), reverse=True)
    page_rows, total = _page_slice(rows, filters.page, filters.page_size)
    return _response(
        "productivity-hourly",
        filters,
        [
            {"key": "date", "label": "Fecha"},
            {"key": "hour", "label": "Hora"},
            {"key": "advisor", "label": "Asesor"},
            {"key": "project", "label": "Cartera"},
            {"key": "activities", "label": "Gestiones"},
            {"key": "calls", "label": "Llamadas"},
            {"key": "whatsapp", "label": "WhatsApp"},
            {"key": "email", "label": "Email"},
            {"key": "promises", "label": "Promesas"},
            {"key": "payments", "label": "Pagos"},
            {"key": "agreements", "label": "Acuerdos"},
            {"key": "effective_contacts", "label": "Contactos efectivos"},
            {"key": "avg_score", "label": "Score promedio"},
        ],
        page_rows,
        total,
        [{"key": "hours", "label": "Horas con gestion", "value": total, "tone": "blue"}],
    )


def _append_hourly_counts(db: Session, user: User, filters: OperationalReportFilters, groups: dict, model: Any, date_column: Any, field: str) -> None:
    visible = _visible_customer_subquery(db, user, filters)
    query = select(model).where(model.customer_id.in_(select(visible.c.id)), model.tenant_id.in_(select(visible.c.tenant_id)))
    query = _date_filters(query, date_column, filters)
    if filters.project_id:
        query = query.where(model.project_id == filters.project_id)
    if filters.advisor_filter:
        query = query.where(model.user_id == filters.advisor_filter)
    for item in db.scalars(query):
        value = getattr(item, "paid_at", None) or getattr(item, "created_at", None)
        if value is None:
            continue
        key = (value.date().isoformat(), value.hour, item.user_id, item.project_id)
        row = groups.setdefault(
            key,
            {
                "date": value.date().isoformat(),
                "hour": value.hour,
                "advisor": _user_name(db, item.user_id),
                "project": _project_name(db, item.project_id),
                "activities": 0,
                "calls": 0,
                "whatsapp": 0,
                "email": 0,
                "promises": 0,
                "payments": 0,
                "agreements": 0,
                "effective_contacts": 0,
                "_scores": [],
            },
        )
        row[field] += 1


def _append_call_log_counts(db: Session, user: User, filters: OperationalReportFilters, groups: dict) -> None:
    visible = _visible_customer_subquery(db, user, filters)
    query = select(CallLog).where(CallLog.customer_id.in_(select(visible.c.id)), CallLog.tenant_id.in_(select(visible.c.tenant_id)))
    query = _date_filters(query, CallLog.started_at, filters)
    if filters.project_id:
        query = query.where(CallLog.project_id == filters.project_id)
    if filters.advisor_filter:
        query = query.where(CallLog.user_id == filters.advisor_filter)
    for call in db.scalars(query):
        key = (call.started_at.date().isoformat(), call.started_at.hour, call.user_id, call.project_id)
        row = groups.setdefault(
            key,
            {
                "date": call.started_at.date().isoformat(),
                "hour": call.started_at.hour,
                "advisor": _user_name(db, call.user_id),
                "project": _project_name(db, call.project_id),
                "activities": 0,
                "calls": 0,
                "whatsapp": 0,
                "email": 0,
                "promises": 0,
                "payments": 0,
                "agreements": 0,
                "effective_contacts": 0,
                "_scores": [],
            },
        )
        row["calls"] += 1


def productivity_advisor_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    visible = _visible_customer_subquery(db, user, filters)
    advisor_ids = set(db.scalars(select(visible.c.assigned_user_id).where(visible.c.assigned_user_id.is_not(None))))
    activity_user_ids = set(db.scalars(select(ManagementActivity.user_id).where(ManagementActivity.customer_id.in_(select(visible.c.id)), ManagementActivity.tenant_id.in_(select(visible.c.tenant_id)))))
    advisor_ids.update(activity_user_ids)
    if filters.advisor_filter:
        advisor_ids = {filters.advisor_filter}
    today = datetime.combine(_now().date(), time.min, tzinfo=timezone.utc)
    month_start = datetime(_now().year, _now().month, 1, tzinfo=timezone.utc)
    rows = []
    for advisor_id in sorted(advisor_ids):
        advisor = db.get(User, advisor_id)
        if not advisor or advisor.status != "active" or advisor.role != AGENT:
            continue
        assignments = list(
            db.scalars(
                select(UserProjectAssignment).where(
                    UserProjectAssignment.user_id == advisor.id,
                    UserProjectAssignment.is_active.is_(True),
                    UserProjectAssignment.role_in_project == "agent",
                )
            )
        )
        if not assignments:
            continue
        project_ids = [item.project_id for item in assignments]
        activities = list(
            db.scalars(
                select(ManagementActivity).where(
                    ManagementActivity.tenant_id == advisor.tenant_id,
                    ManagementActivity.user_id == advisor.id,
                    ManagementActivity.created_at >= month_start,
                    ManagementActivity.customer_id.in_(select(visible.c.id)),
                )
            )
        )
        scored = [_safe_score(db, item) for item in activities]
        scored = [item for item in scored if item]
        effective = sum(1 for item in scored if item.is_effective)
        insights = advisor_management_insights(db, advisor)
        rows.append(
            {
                "advisor": advisor.name,
                "project": ", ".join(_project_name(db, project_id) for project_id in project_ids[:2]) or "-",
                "activities_day": sum(1 for item in activities if item.created_at >= today),
                "activities_month": len(activities),
                "effective_contacts": effective,
                "promises": db.scalar(select(func.count(PaymentPromise.id)).where(PaymentPromise.tenant_id == advisor.tenant_id, PaymentPromise.user_id == advisor.id, PaymentPromise.created_at >= month_start)) or 0,
                "payments": db.scalar(select(func.count(Payment.id)).where(Payment.tenant_id == advisor.tenant_id, Payment.user_id == advisor.id, Payment.paid_at >= month_start)) or 0,
                "agreements": db.scalar(select(func.count(PaymentAgreement.id)).where(PaymentAgreement.tenant_id == advisor.tenant_id, PaymentAgreement.user_id == advisor.id, PaymentAgreement.created_at >= month_start)) or 0,
                "best_month": insights.best_current_month.result if insights.best_current_month else "-",
                "best_historical": insights.best_historical.result if insights.best_historical else "-",
                "avg_score": round(sum(item.score for item in scored) / max(len(scored), 1)),
                "effectiveness": f"{round((effective / max(len(activities), 1)) * 100)}%",
            }
        )
    rows.sort(key=lambda item: (item["activities_month"], item["effective_contacts"], item["avg_score"]), reverse=True)
    page_rows, total = _page_slice(rows, filters.page, filters.page_size)
    return _response(
        "productivity-advisor",
        filters,
        [
            {"key": "advisor", "label": "Asesor"},
            {"key": "project", "label": "Cartera"},
            {"key": "activities_day", "label": "Gestiones dia"},
            {"key": "activities_month", "label": "Gestiones mes"},
            {"key": "effective_contacts", "label": "Contactos efectivos"},
            {"key": "promises", "label": "Promesas"},
            {"key": "payments", "label": "Pagos"},
            {"key": "agreements", "label": "Acuerdos"},
            {"key": "best_month", "label": "Mejor mes"},
            {"key": "best_historical", "label": "Mejor historica"},
            {"key": "avg_score", "label": "Score promedio"},
            {"key": "effectiveness", "label": "Efectividad"},
        ],
        page_rows,
        total,
        [{"key": "advisors", "label": "Asesores operativos", "value": total, "tone": "blue"}],
    )


def demographics_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    visible = _visible_customer_subquery(db, user, filters)
    query = select(CustomerDemographic).where(
        CustomerDemographic.customer_id.in_(select(visible.c.id)),
        CustomerDemographic.tenant_id.in_(select(visible.c.tenant_id)),
        CustomerDemographic.is_active.is_(True),
    )
    if filters.status:
        query = query.where(CustomerDemographic.contactability == filters.status)
    if filters.search:
        pattern = f"%{filters.search.strip()}%"
        query = query.where(or_(CustomerDemographic.phone.ilike(pattern), CustomerDemographic.email.ilike(pattern), CustomerDemographic.address.ilike(pattern)))
    query = query.order_by(CustomerDemographic.priority.desc(), CustomerDemographic.score.desc(), CustomerDemographic.id.desc())
    demographics, total = _query_page(db, query, filters.page, filters.page_size)
    rows = []
    for demographic in demographics:
        customer = db.get(Customer, demographic.customer_id)
        last = _last_activity(db, demographic.customer_id, demographic.tenant_id)
        recommended = "WhatsApp / llamada" if demographic.phone or (customer and customer.phone) else "Email" if demographic.email or (customer and customer.email) else "Validar datos"
        contact = customer_contact_status(db, user, customer) if customer else None
        rows.append(
            {
                "customer": customer.name if customer else f"Cliente {demographic.customer_id}",
                "phones": demographic.phone or customer.phone if customer else demographic.phone or "-",
                "emails": demographic.email or customer.email if customer else demographic.email or "-",
                "addresses": demographic.address or "-",
                "contactability": demographic.contactability,
                "priority": demographic.priority,
                "valid_until": demographic.valid_until,
                "last_channel": last.channel if last else "-",
                "recommended_channel": recommended,
                "restrictions": contact["status"] if contact else "sin_reglas",
            }
        )
    return _response(
        "demographics",
        filters,
        [
            {"key": "customer", "label": "Cliente"},
            {"key": "phones", "label": "Telefonos"},
            {"key": "emails", "label": "Emails"},
            {"key": "addresses", "label": "Direcciones"},
            {"key": "contactability", "label": "Contactabilidad"},
            {"key": "priority", "label": "Prioridad"},
            {"key": "valid_until", "label": "Vigencia", "type": "date"},
            {"key": "last_channel", "label": "Ultimo canal"},
            {"key": "recommended_channel", "label": "Canal recomendado"},
            {"key": "restrictions", "label": "Restricciones"},
        ],
        rows,
        total,
        [{"key": "demographics", "label": "Datos contactabilidad", "value": total, "tone": "blue"}],
    )


def tasks_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    visible = _visible_customer_subquery(db, user, filters)
    query = select(ManagementActivity).where(
        ManagementActivity.customer_id.in_(select(visible.c.id)),
        ManagementActivity.tenant_id.in_(select(visible.c.tenant_id)),
        ManagementActivity.next_contact_at.is_not(None),
    )
    query = _date_filters(query, ManagementActivity.next_contact_at, filters)
    if filters.project_id:
        query = query.where(ManagementActivity.project_id == filters.project_id)
    if filters.advisor_filter:
        query = query.where(ManagementActivity.user_id == filters.advisor_filter)
    query = query.order_by(ManagementActivity.next_contact_at.asc(), ManagementActivity.id.desc())
    tasks, total = _query_page(db, query, filters.page, filters.page_size)
    now = _now()
    rows = []
    for task in tasks:
        customer = db.get(Customer, task.customer_id)
        rows.append(
            {
                "customer": customer.name if customer else "-",
                "advisor": _user_name(db, task.user_id),
                "project": _project_name(db, task.project_id),
                "scheduled_at": task.next_contact_at,
                "task_type": "Seguimiento",
                "status": "Vencida" if task.next_contact_at and task.next_contact_at < now else "Programada",
                "origin": task.channel,
                "overdue": "Si" if task.next_contact_at and task.next_contact_at < now else "No",
            }
        )
    return _response(
        "tasks",
        filters,
        [
            {"key": "customer", "label": "Cliente"},
            {"key": "advisor", "label": "Asesor"},
            {"key": "project", "label": "Cartera"},
            {"key": "scheduled_at", "label": "Fecha programada", "type": "date"},
            {"key": "task_type", "label": "Tipo tarea"},
            {"key": "status", "label": "Estado"},
            {"key": "origin", "label": "Origen"},
            {"key": "overdue", "label": "Vencida"},
        ],
        rows,
        total,
        [{"key": "tasks", "label": "Tareas visibles", "value": total, "tone": "yellow" if total else "green"}],
        note="Este reporte usa management_activities.next_contact_at como fuente operativa hasta formalizar un modelo de tareas.",
    )


def _tenant_module_active(db: Session, tenant_id: int, module_code: str) -> bool:
    module_count = db.scalar(select(func.count(TenantModule.id)).where(TenantModule.tenant_id == tenant_id)) or 0
    if module_count == 0:
        return True
    module = db.scalar(select(TenantModule).where(TenantModule.tenant_id == tenant_id, TenantModule.module_code == module_code))
    return bool(module and module.enabled and module.is_enabled)


def _careflow_module_active(db: Session, user: User, tenant_id: int | None) -> bool:
    if is_platform_admin(db, user):
        return _tenant_module_active(db, tenant_id, "careflow") if tenant_id else True
    return user_has_module(db, user, "careflow", user.tenant_id)


def _visible_care_case_query(db: Session, user: User, filters: OperationalReportFilters):
    query = select(CareCase).where(CareCase.tenant_id.is_not(None))
    if is_platform_admin(db, user):
        if filters.tenant_id:
            query = query.where(CareCase.tenant_id == filters.tenant_id)
    else:
        query = query.where(CareCase.tenant_id == user.tenant_id)
        if is_company_admin(db, user) or _role_is_quality(db, user):
            pass
        elif _role_is_leader(db, user):
            project_ids = _active_project_ids(db, user)
            team_ids = _team_user_ids(db, user)
            conditions = [CareCase.assigned_user_id.in_(team_ids), CareCase.created_by_id == user.id, CareCase.assigned_user_id.is_(None)]
            if project_ids:
                conditions.append(CareCase.project_id.in_(project_ids))
            query = query.where(or_(*conditions))
    if filters.project_id:
        query = query.where(CareCase.project_id == filters.project_id)
    query = _date_filters(query, CareCase.created_at, filters)
    return query


def careflow_report(db: Session, user: User, filters: OperationalReportFilters) -> dict[str, Any]:
    if not _careflow_module_active(db, user, filters.tenant_id):
        return _response(
            "careflow",
            filters,
            [{"key": "dimension", "label": "Dimension"}, {"key": "value", "label": "Valor"}, {"key": "cases", "label": "Casos"}],
            [],
            0,
            available=False,
            note="CareFlow 360 no esta activo para la empresa seleccionada.",
        )
    query = _visible_care_case_query(db, user, filters)
    cases = list(db.scalars(query))
    now = _now()
    rows = []
    for dimension, field in [("Estado", "status"), ("Prioridad", "priority"), ("Canal", "channel"), ("Responsable", "assigned_user_id")]:
        grouped: dict[str, int] = {}
        for item in cases:
            raw = getattr(item, field)
            label = _user_name(db, raw) if field == "assigned_user_id" else str(raw or "Sin asignar")
            grouped[label] = grouped.get(label, 0) + 1
        rows.extend({"dimension": dimension, "value": label, "cases": count} for label, count in grouped.items())
    resolved = [item for item in cases if item.resolved_at and item.created_at]
    avg_hours = round(sum((item.resolved_at - item.created_at).total_seconds() / 3600 for item in resolved) / max(len(resolved), 1), 1)
    page_rows, total = _page_slice(rows, filters.page, filters.page_size)
    return _response(
        "careflow",
        filters,
        [{"key": "dimension", "label": "Dimension"}, {"key": "value", "label": "Valor"}, {"key": "cases", "label": "Casos"}],
        page_rows,
        total,
        [
            {"key": "cases", "label": "Casos CareFlow", "value": len(cases), "tone": "blue"},
            {"key": "overdue", "label": "Vencidos SLA", "value": len([item for item in cases if item.due_at and item.due_at < now and item.status not in {"resuelto", "cerrado", "cancelado"}]), "tone": "yellow"},
            {"key": "avg_resolution", "label": "Resolucion promedio", "value": f"{avg_hours} h", "tone": "green"},
        ],
    )
