from __future__ import annotations

import csv
import io
import math
import re
import unicodedata
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import (
    CommunicationChannel,
    Customer,
    ImportBatch,
    ManagementActivity,
    Payment,
    PaymentPromise,
    Project,
    Tenant,
    TypificationNode,
    User,
    UserProjectAssignment,
)
from app.schemas.crm import (
    ActivityCreate,
    ActivityOut,
    BIResponse,
    CommunicationChannelCreate,
    CommunicationChannelOut,
    CrmOption,
    CrmOptions,
    CustomerCreate,
    CustomerListResponse,
    CustomerOut,
    DashboardMetrics,
    ImportCustomersRequest,
    ImportCustomersResponse,
    PaymentCreate,
    PaymentOut,
    PromiseCreate,
    PromiseOut,
)
from app.schemas.typification import TypificationOut


router = APIRouter()
MANAGE_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR}
READ_ROLES = {PLATFORM_ADMIN, TENANT_ADMIN, COORDINATOR, QUALITY_SUPERVISOR, AGENT}


def ensure_read_access(user: User) -> None:
    if user.role not in READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol sin acceso al CRM.")


def ensure_manage_access(user: User) -> None:
    if user.role not in MANAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol sin permiso para modificar.")


def is_platform(user: User) -> bool:
    return user.role == PLATFORM_ADMIN


def business_tenant_query(db: Session):
    return select(Tenant).where(Tenant.slug != settings.platform_tenant_slug).order_by(Tenant.name)


def project_for_access(db: Session, project_id: int, user: User) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado.")
    if not is_platform(user) and project.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Proyecto fuera de tu empresa.")
    return project


def customer_for_access(db: Session, customer_id: int, user: User, write: bool = False) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado.")
    if not is_platform(user) and customer.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cliente fuera de tu empresa.")
    if user.role == AGENT and customer.assigned_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cliente no asignado al gestor.")
    if write and user.role == QUALITY_SUPERVISOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Calidad tiene acceso de lectura.")
    return customer


def validate_assigned_user(db: Session, tenant_id: int, assigned_user_id: int | None) -> None:
    if assigned_user_id is None:
        return
    assigned = db.get(User, assigned_user_id)
    if assigned is None or assigned.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El gestor asignado no pertenece a la empresa.")


def risk_from_dpd(dpd: int, balance: int) -> str:
    if dpd >= 60 or balance >= 20_000_000:
        return "Alto"
    if dpd >= 15 or balance >= 5_000_000:
        return "Medio"
    return "Bajo"


def priority_score(dpd: int, balance: int, risk: str, status_value: str) -> int:
    risk_score = {"Alto": 30, "Medio": 18, "Bajo": 8}.get(risk, 12)
    status_score = {"Promesa": 12, "Sin contacto": 10, "Escalado": 14, "Disputa": 12}.get(status_value, 5)
    return min(100, risk_score + min(35, round(dpd / 3)) + min(25, round(balance / 2_000_000)) + status_score)


def next_action_for(status_value: str, risk: str) -> str:
    if status_value == "Promesa":
        return "Confirmar cumplimiento de promesa"
    if status_value == "Escalado":
        return "Seguimiento lider y ruta especializada"
    if status_value == "Disputa":
        return "Solicitar soporte documental y congelar automatizaciones"
    if risk == "Alto":
        return "Contacto prioritario y alternativa de normalizacion"
    return "Programar nueva gestion"


def normalize_header(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", normalized.lower()).strip("_")


def pick(record: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        value = record.get(normalize_header(key))
        if value:
            return value.strip()
    return ""


def parse_money(value: str) -> int:
    cleaned = re.sub(r"[^\d.-]", "", value or "")
    try:
        return max(0, round(float(cleaned)))
    except ValueError:
        return 0


def parse_csv_records(csv_text: str) -> list[dict[str, str]]:
    first_line = csv_text.splitlines()[0] if csv_text.splitlines() else ""
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter)
    rows = [row for row in reader if any(cell.strip() for cell in row)]
    if len(rows) < 2:
        return []
    headers = [normalize_header(header) for header in rows[0]]
    return [dict(zip(headers, row, strict=False)) for row in rows[1:]]


def customer_query(db: Session, user: User):
    query = select(Customer)
    if not is_platform(user):
        query = query.where(Customer.tenant_id == user.tenant_id)
    if user.role == AGENT:
        query = query.where(Customer.assigned_user_id == user.id)
    return query


def customer_to_out(db: Session, customer: Customer) -> CustomerOut:
    tenant = db.get(Tenant, customer.tenant_id) if customer.tenant_id else None
    project = db.get(Project, customer.project_id) if customer.project_id else None
    assigned = db.get(User, customer.assigned_user_id) if customer.assigned_user_id else None
    return CustomerOut(
        id=customer.id,
        tenant_id=customer.tenant_id,
        tenant_name=tenant.name if tenant else None,
        project_id=customer.project_id,
        project_name=project.name if project else None,
        assigned_user_id=customer.assigned_user_id,
        assigned_user_name=assigned.name if assigned else None,
        name=customer.name,
        document=customer.document,
        phone=customer.phone,
        email=customer.email,
        city=customer.city,
        segment=customer.segment,
        obligation=customer.obligation,
        balance=customer.balance,
        original_balance=customer.original_balance,
        dpd=customer.dpd,
        status=customer.status,
        risk=customer.risk,
        priority=customer.priority,
        next_action=customer.next_action,
        contactability=customer.contactability,
        notes=customer.notes,
        last_contact_at=customer.last_contact_at,
        next_contact_at=customer.next_contact_at,
        created_at=customer.created_at,
    )


def activity_to_out(db: Session, activity: ManagementActivity) -> ActivityOut:
    user = db.get(User, activity.user_id)
    typification = db.get(TypificationNode, activity.typification_id) if activity.typification_id else None
    return ActivityOut(
        id=activity.id,
        customer_id=activity.customer_id,
        user_id=activity.user_id,
        user_name=user.name if user else None,
        typification_id=activity.typification_id,
        typification_label=typification.label if typification else None,
        channel=activity.channel,
        result=activity.result,
        note=activity.note,
        next_contact_at=activity.next_contact_at,
        created_at=activity.created_at,
    )


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def semaphore_status(score: int) -> str:
    if score >= 75:
        return "green"
    if score >= 45:
        return "yellow"
    return "red"


def recovery_probability(customer: Customer, activities: list[ManagementActivity], promises: list[PaymentPromise]) -> float:
    score = 28.0
    score += {"Bajo": 20, "Medio": 10, "Alto": -8}.get(customer.risk, 0)
    score += {"Alta": 16, "Media": 7, "Baja": -8}.get(customer.contactability, 0)
    score += {"Promesa": 22, "Contactado": 14, "Pago parcial": 18, "Sin contacto": -12, "Escalado": -6, "Disputa": -14}.get(customer.status, 0)
    score -= min(28, customer.dpd * 0.22)
    score += min(14, len(activities) * 3)
    if any(item.status == "Vigente" for item in promises):
        score += 12
    if customer.phone:
        score += 4
    if customer.email:
        score += 3
    return clamp(score, 3, 92) / 100


def activity_is_stale(customer: Customer, now: datetime) -> bool:
    if customer.last_contact_at is None:
        return True
    return customer.last_contact_at < now - timedelta(days=7)


def aging_bucket_label(dpd: int) -> str:
    if dpd <= 15:
        return "0-15"
    if dpd <= 30:
        return "16-30"
    if dpd <= 60:
        return "31-60"
    if dpd <= 90:
        return "61-90"
    return "90+"


@router.get("/options", response_model=CrmOptions)
def options(db: Session = Depends(get_db), user: User = Depends(current_user)) -> CrmOptions:
    ensure_read_access(user)
    tenants = list(db.scalars(business_tenant_query(db))) if is_platform(user) else [db.get(Tenant, user.tenant_id)]
    tenant_ids = [tenant.id for tenant in tenants if tenant]
    projects = list(db.scalars(select(Project).where(Project.tenant_id.in_(tenant_ids)).order_by(Project.name))) if tenant_ids else []
    users = list(db.scalars(select(User).where(User.tenant_id.in_(tenant_ids), User.role != PLATFORM_ADMIN).order_by(User.name))) if tenant_ids else []
    channels = list(db.scalars(select(CommunicationChannel).where(CommunicationChannel.tenant_id.in_(tenant_ids)).order_by(CommunicationChannel.kind, CommunicationChannel.label))) if tenant_ids else []
    return CrmOptions(
        tenants=[CrmOption(id=tenant.id, name=tenant.name) for tenant in tenants if tenant],
        projects=[CrmOption(id=project.id, name=project.name, label=f"{project.code} - {project.name}") for project in projects],
        users=[CrmOption(id=item.id, name=item.name, label=f"{item.name} - {item.role}") for item in users],
        channels=[CommunicationChannelOut.model_validate(channel, from_attributes=True) for channel in channels],
    )


@router.get("/typifications", response_model=list[TypificationOut])
def crm_typifications(
    tenant_id: int | None = None,
    project_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[TypificationNode]:
    ensure_read_access(user)
    query = select(TypificationNode).order_by(TypificationNode.sort_order, TypificationNode.label)
    if is_platform(user):
        if tenant_id:
            query = query.where(TypificationNode.tenant_id == tenant_id)
    else:
        query = query.where(TypificationNode.tenant_id == user.tenant_id)
    if project_id:
        query = query.where((TypificationNode.project_id == project_id) | (TypificationNode.project_id.is_(None)))
    return list(db.scalars(query))


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard(
    tenant_id: int | None = None,
    project_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> DashboardMetrics:
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


@router.get("/bi", response_model=BIResponse)
def business_intelligence(
    tenant_id: int | None = None,
    project_id: int | None = None,
    horizon_days: int = Query(default=30, ge=7, le=180),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    ensure_read_access(user)
    now = datetime.now(timezone.utc)
    query = customer_query(db, user)
    if tenant_id and is_platform(user):
        query = query.where(Customer.tenant_id == tenant_id)
    if project_id:
        project_for_access(db, project_id, user)
        query = query.where(Customer.project_id == project_id)
    customers = list(db.scalars(query))
    customer_ids = [customer.id for customer in customers]
    activities = list(db.scalars(select(ManagementActivity).where(ManagementActivity.customer_id.in_(customer_ids)))) if customer_ids else []
    payments = list(db.scalars(select(Payment).where(Payment.customer_id.in_(customer_ids)))) if customer_ids else []
    promises = list(db.scalars(select(PaymentPromise).where(PaymentPromise.customer_id.in_(customer_ids)))) if customer_ids else []
    tenant_ids = sorted({customer.tenant_id for customer in customers})
    channels = list(db.scalars(select(CommunicationChannel).where(CommunicationChannel.tenant_id.in_(tenant_ids)))) if tenant_ids else []

    activities_by_customer: dict[int, list[ManagementActivity]] = {}
    for activity in activities:
        activities_by_customer.setdefault(activity.customer_id, []).append(activity)
    promises_by_customer: dict[int, list[PaymentPromise]] = {}
    for promise in promises:
        promises_by_customer.setdefault(promise.customer_id, []).append(promise)

    total_balance = sum(customer.balance for customer in customers)
    original_balance = sum(customer.original_balance for customer in customers) or total_balance
    recovered = sum(payment.amount for payment in payments)
    active_promises = [item for item in promises if item.status == "Vigente"]
    overdue_promises = [item for item in active_promises if item.due_date < now]
    contacted = [customer for customer in customers if customer.status != "Sin contacto"]
    high_risk = [customer for customer in customers if customer.risk == "Alto"]
    stale = [customer for customer in customers if activity_is_stale(customer, now)]
    no_contact = [customer for customer in customers if customer.status == "Sin contacto"]
    unassigned = [customer for customer in customers if customer.assigned_user_id is None]
    missing_channel_data = [customer for customer in customers if not customer.phone and not customer.email]

    horizon_factor = clamp(horizon_days / 90, 0.18, 1.35)
    expected_by_customer = {}
    for customer in customers:
        probability = recovery_probability(customer, activities_by_customer.get(customer.id, []), promises_by_customer.get(customer.id, []))
        active_promise_value = sum(item.amount for item in promises_by_customer.get(customer.id, []) if item.status == "Vigente")
        expected = round(min(customer.balance, max(customer.balance * probability * horizon_factor, active_promise_value * 0.72)))
        expected_by_customer[customer.id] = {"probability": round(probability * 100), "expected": expected}

    expected_recovery = sum(item["expected"] for item in expected_by_customer.values())
    contact_rate = round((len(contacted) / max(len(customers), 1)) * 100)
    recovery_rate = round((recovered / max(original_balance, 1)) * 100)
    high_risk_balance = sum(customer.balance for customer in high_risk)
    no_contact_balance = sum(customer.balance for customer in no_contact)
    stale_balance = sum(customer.balance for customer in stale)
    overdue_promise_value = sum(item.amount for item in overdue_promises)
    unassigned_balance = sum(customer.balance for customer in unassigned)
    data_gap_count = len(missing_channel_data) + len(unassigned)

    semaphores = [
        {
            "label": "Velocidad de recuperacion",
            "score": int(clamp(recovery_rate * 2.5, 0, 100)),
            "detail": f"Recuperacion acumulada sobre cartera original: {recovery_rate}%.",
        },
        {
            "label": "Contacto efectivo",
            "score": contact_rate,
            "detail": f"{len(contacted)} de {len(customers)} clientes tienen gestion efectiva.",
        },
        {
            "label": "Riesgo controlado",
            "score": int(clamp(100 - ((high_risk_balance / max(total_balance, 1)) * 100), 0, 100)),
            "detail": f"Exposicion alto riesgo: {high_risk_balance}.",
        },
        {
            "label": "Promesas saludables",
            "score": int(clamp(100 - ((len(overdue_promises) / max(len(active_promises), 1)) * 100), 0, 100)),
            "detail": f"{len(overdue_promises)} promesas vencidas de {len(active_promises)} vigentes.",
        },
        {
            "label": "Calidad de datos",
            "score": int(clamp(100 - ((data_gap_count / max(len(customers) * 2, 1)) * 100), 0, 100)),
            "detail": f"{len(missing_channel_data)} sin datos de contacto y {len(unassigned)} sin gestor.",
        },
        {
            "label": "Preparacion omnicanal",
            "score": 100 if len(channels) >= 3 else 70 if channels else 25,
            "detail": f"{len(channels)} canales configurados para empresas visibles.",
        },
    ]
    for item in semaphores:
        item["status"] = semaphore_status(item["score"])

    alerts = []
    if overdue_promises:
        alerts.append(
            {
                "severity": "red",
                "title": "Promesas vencidas",
                "body": f"{len(overdue_promises)} promesas vencidas suman valor en riesgo.",
                "value": overdue_promise_value,
                "action": "Priorizar llamadas humanas y bloquear automatizaciones masivas para estos casos.",
            }
        )
    if high_risk_balance / max(total_balance, 1) >= 0.35:
        alerts.append(
            {
                "severity": "red",
                "title": "Alta concentracion de riesgo",
                "body": "La cartera en alto riesgo supera el umbral recomendado.",
                "value": high_risk_balance,
                "action": "Asignar lider especializado y revisar estrategia por proyecto.",
            }
        )
    if no_contact_balance:
        alerts.append(
            {
                "severity": "yellow",
                "title": "Cartera sin contacto",
                "body": f"{len(no_contact)} clientes no tienen contacto efectivo registrado.",
                "value": no_contact_balance,
                "action": "Activar enriquecimiento de datos y alternar WhatsApp, correo y llamada.",
            }
        )
    if stale_balance:
        alerts.append(
            {
                "severity": "yellow",
                "title": "Casos sin gestion reciente",
                "body": f"{len(stale)} clientes llevan mas de 7 dias sin gestion util.",
                "value": stale_balance,
                "action": "Rebalancear cola y subir prioridad automaticamente.",
            }
        )
    if unassigned:
        alerts.append(
            {
                "severity": "yellow",
                "title": "Clientes sin gestor",
                "body": f"{len(unassigned)} clientes no tienen responsable operativo.",
                "value": unassigned_balance,
                "action": "Asignar gestores antes de ejecutar campanas o reporteria de productividad.",
            }
        )
    if not channels:
        alerts.append(
            {
                "severity": "yellow",
                "title": "Omnicanalidad incompleta",
                "body": "No hay canales configurados para WhatsApp, email o telefonia.",
                "value": 0,
                "action": "Configurar al menos un canal principal por empresa.",
            }
        )

    aging_template = {label: {"label": label, "customers": 0, "balance": 0, "expected_recovery": 0} for label in ["0-15", "16-30", "31-60", "61-90", "90+"]}
    for customer in customers:
        bucket = aging_template[aging_bucket_label(customer.dpd)]
        bucket["customers"] += 1
        bucket["balance"] += customer.balance
        bucket["expected_recovery"] += expected_by_customer.get(customer.id, {}).get("expected", 0)

    project_performance = []
    for project in db.scalars(select(Project).order_by(Project.name)):
        project_customers = [customer for customer in customers if customer.project_id == project.id]
        if not project_customers:
            continue
        project_ids = [customer.id for customer in project_customers]
        project_recovered = sum(payment.amount for payment in payments if payment.customer_id in project_ids)
        project_balance = sum(customer.balance for customer in project_customers)
        project_contact = round((len([customer for customer in project_customers if customer.status != "Sin contacto"]) / max(len(project_customers), 1)) * 100)
        project_expected = sum(expected_by_customer[customer.id]["expected"] for customer in project_customers)
        risk_share = round((sum(customer.balance for customer in project_customers if customer.risk == "Alto") / max(project_balance, 1)) * 100)
        score = int(clamp((project_contact * 0.35) + ((100 - risk_share) * 0.3) + (min(100, (project_recovered / max(project_balance + project_recovered, 1)) * 350) * 0.35), 0, 100))
        project_performance.append(
            {
                "project": project.name,
                "customers": len(project_customers),
                "balance": project_balance,
                "recovered": project_recovered,
                "expected_recovery": project_expected,
                "contact_rate": project_contact,
                "risk_share": risk_share,
                "score": score,
                "status": semaphore_status(score),
            }
        )

    agent_productivity = []
    assigned_user_ids = {customer.assigned_user_id for customer in customers if customer.assigned_user_id}
    visible_users = list(db.scalars(select(User).where(User.id.in_(assigned_user_ids)))) if assigned_user_ids else []
    for agent in visible_users:
        assigned = [customer for customer in customers if customer.assigned_user_id == agent.id]
        if not assigned:
            continue
        assigned_ids = [customer.id for customer in assigned]
        agent_activities = [activity for activity in activities if activity.customer_id in assigned_ids]
        agent_payments = [payment for payment in payments if payment.customer_id in assigned_ids]
        agent_promises = [promise for promise in promises if promise.customer_id in assigned_ids and promise.status == "Vigente"]
        contact = round((len([customer for customer in assigned if customer.status != "Sin contacto"]) / max(len(assigned), 1)) * 100)
        expected = sum(expected_by_customer[customer.id]["expected"] for customer in assigned)
        agent_productivity.append(
            {
                "agent": agent.name,
                "assigned": len(assigned),
                "activities": len(agent_activities),
                "promises": len(agent_promises),
                "recovered": sum(payment.amount for payment in agent_payments),
                "expected_recovery": expected,
                "contact_rate": contact,
                "score": int(clamp((contact * 0.4) + (min(100, len(agent_activities) * 8) * 0.25) + (min(100, sum(payment.amount for payment in agent_payments) / max(expected, 1) * 100) * 0.35), 0, 100)),
            }
        )
    agent_productivity.sort(key=lambda item: item["score"], reverse=True)

    paid_customer_ids = {payment.customer_id for payment in payments}
    promise_customer_ids = {promise.customer_id for promise in promises}
    funnel = [
        {"label": "Asignados", "value": len(customers), "balance": total_balance},
        {"label": "Contactados", "value": len(contacted), "balance": sum(customer.balance for customer in contacted)},
        {"label": "Con promesa", "value": len(promise_customer_ids), "balance": sum(customer.balance for customer in customers if customer.id in promise_customer_ids)},
        {"label": "Con pago", "value": len(paid_customer_ids), "balance": sum(customer.balance for customer in customers if customer.id in paid_customer_ids)},
    ]

    top_opportunities = sorted(
        [
            {
                "customer_id": customer.id,
                "customer": customer.name,
                "project": (db.get(Project, customer.project_id).name if customer.project_id else "-"),
                "balance": customer.balance,
                "probability": expected_by_customer[customer.id]["probability"],
                "expected_recovery": expected_by_customer[customer.id]["expected"],
                "next_action": customer.next_action or next_action_for(customer.status, customer.risk),
            }
            for customer in customers
        ],
        key=lambda item: item["expected_recovery"],
        reverse=True,
    )[:10]

    high_risk_cases = sorted(
        [
            {
                "customer_id": customer.id,
                "customer": customer.name,
                "balance": customer.balance,
                "dpd": customer.dpd,
                "status": customer.status,
                "priority": customer.priority,
                "stale": activity_is_stale(customer, now),
            }
            for customer in high_risk
        ],
        key=lambda item: (item["priority"], item["balance"]),
        reverse=True,
    )[:10]

    insights = [
        {
            "title": "Recuperacion esperada",
            "body": f"El motor proyecta recuperacion probable a {horizon_days} dias con base en promesas, contacto, riesgo, mora y actividad.",
            "impact_value": expected_recovery,
            "confidence": 78 if customers else 30,
            "action": "Convertir esta proyeccion en meta por lider y cartera.",
        },
        {
            "title": "Valor que requiere intervencion",
            "body": "La cartera sin contacto o sin gestion reciente debe salir de cola pasiva y entrar a estrategia de choque.",
            "impact_value": no_contact_balance + stale_balance,
            "confidence": 74,
            "action": "Ejecutar bloque de priorizacion y alternar canales.",
        },
        {
            "title": "Oportunidad por promesas",
            "body": "Las promesas vigentes son la fuente de recuperacion mas cercana, pero las vencidas erosionan conversion.",
            "impact_value": sum(item.amount for item in active_promises),
            "confidence": 82,
            "action": "Crear tablero diario de promesas por vencer y vencidas.",
        },
    ]

    return {
        "generated_at": now,
        "horizon_days": horizon_days,
        "kpis": [
            {"key": "expected_recovery", "label": "Recuperacion esperada", "value": expected_recovery, "detail": f"Proyeccion a {horizon_days} dias", "status": "green" if expected_recovery > 0 else "yellow"},
            {"key": "risk_value", "label": "Valor alto riesgo", "value": high_risk_balance, "detail": f"{len(high_risk)} clientes en alto riesgo", "status": "red" if high_risk_balance / max(total_balance, 1) >= 0.35 else "yellow"},
            {"key": "no_contact_value", "label": "Valor sin contacto", "value": no_contact_balance, "detail": f"{len(no_contact)} clientes sin contacto", "status": "red" if no_contact_balance else "green"},
            {"key": "overdue_promise_value", "label": "Promesas vencidas", "value": overdue_promise_value, "detail": f"{len(overdue_promises)} promesas vencidas", "status": "red" if overdue_promises else "green"},
            {"key": "contact_rate", "label": "Contacto efectivo", "value": f"{contact_rate}%", "detail": "Porcentaje de clientes gestionados", "status": semaphore_status(contact_rate)},
            {"key": "recovery_rate", "label": "Recuperacion acumulada", "value": f"{recovery_rate}%", "detail": "Pagos sobre cartera original", "status": semaphore_status(int(clamp(recovery_rate * 2.5)))},
        ],
        "semaphores": semaphores,
        "alerts": alerts,
        "insights": insights,
        "prediction": {
            "expected_recovery": expected_recovery,
            "expected_recovery_low": round(expected_recovery * 0.78),
            "expected_recovery_high": round(expected_recovery * 1.18),
            "leakage_risk_value": round((no_contact_balance + stale_balance + overdue_promise_value) * 0.18),
            "horizon_days": horizon_days,
            "model": "scoring_operativo_v2",
        },
        "aging_buckets": list(aging_template.values()),
        "project_performance": project_performance,
        "agent_productivity": agent_productivity,
        "funnel": funnel,
        "top_opportunities": top_opportunities,
        "high_risk_cases": high_risk_cases,
    }


@router.get("/customers", response_model=CustomerListResponse)
def list_customers(
    q: str | None = None,
    tenant_id: int | None = None,
    project_id: int | None = None,
    assigned_user_id: int | None = None,
    status_value: str | None = Query(default=None, alias="status"),
    risk: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> CustomerListResponse:
    ensure_read_access(user)
    page = max(1, page)
    page_size = min(10, max(1, page_size))
    query = customer_query(db, user)
    if tenant_id and is_platform(user):
        query = query.where(Customer.tenant_id == tenant_id)
    if project_id:
        query = query.where(Customer.project_id == project_id)
    if assigned_user_id and user.role != AGENT:
        query = query.where(Customer.assigned_user_id == assigned_user_id)
    if status_value:
        query = query.where(Customer.status == status_value)
    if risk:
        query = query.where(Customer.risk == risk)
    if q:
        pattern = f"%{q.lower()}%"
        query = query.where(func.lower(Customer.name).like(pattern) | func.lower(Customer.document).like(pattern) | func.lower(Customer.phone).like(pattern))
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(db.scalars(query.order_by(Customer.priority.desc(), Customer.dpd.desc()).offset((page - 1) * page_size).limit(page_size)))
    return CustomerListResponse(
        items=[customer_to_out(db, item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.post("/customers", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CustomerOut:
    ensure_manage_access(user)
    project = project_for_access(db, payload.project_id, user)
    tenant_id = project.tenant_id
    validate_assigned_user(db, tenant_id, payload.assigned_user_id)
    risk = payload.risk or risk_from_dpd(payload.dpd, payload.balance)
    customer = Customer(
        tenant_id=tenant_id,
        project_id=project.id,
        assigned_user_id=payload.assigned_user_id,
        name=payload.name.strip(),
        document=payload.document.strip(),
        phone=payload.phone,
        email=payload.email,
        city=payload.city,
        segment=payload.segment,
        obligation=payload.obligation,
        balance=payload.balance,
        original_balance=payload.original_balance or payload.balance,
        dpd=payload.dpd,
        status=payload.status,
        risk=risk,
        priority=priority_score(payload.dpd, payload.balance, risk, payload.status),
        next_action=next_action_for(payload.status, risk),
        contactability=payload.contactability,
        notes=payload.notes,
        next_contact_at=payload.next_contact_at,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer_to_out(db, customer)


@router.post("/customers/import", response_model=ImportCustomersResponse)
def import_customers(payload: ImportCustomersRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ImportCustomersResponse:
    ensure_manage_access(user)
    project = project_for_access(db, payload.project_id, user)
    validate_assigned_user(db, project.tenant_id, payload.assigned_user_id)
    imported = updated = skipped = 0
    for record in parse_csv_records(payload.csv_text):
        name = pick(record, ["nombre", "cliente", "name"])
        document = pick(record, ["documento", "cedula", "nit", "identificacion", "id"])
        if not name or not document:
            skipped += 1
            continue
        balance = parse_money(pick(record, ["saldo", "saldo_vencido", "balance", "valor"]))
        original_balance = parse_money(pick(record, ["saldo_original", "obligacion_total", "capital", "original_balance"])) or balance
        dpd_raw = pick(record, ["mora", "dpd", "dias_mora", "diasdemora"])
        try:
            dpd = int(float(dpd_raw or 0))
        except ValueError:
            dpd = 0
        risk = risk_from_dpd(dpd, balance)
        existing = db.scalar(
            select(Customer).where(
                Customer.tenant_id == project.tenant_id,
                Customer.project_id == project.id,
                Customer.document == document.strip(),
            )
        )
        target = existing or Customer(tenant_id=project.tenant_id, project_id=project.id, document=document.strip())
        target.assigned_user_id = payload.assigned_user_id
        target.name = name.strip()
        target.phone = pick(record, ["telefono", "celular", "movil", "phone"]) or None
        target.email = pick(record, ["email", "correo"]) or None
        target.city = pick(record, ["ciudad", "municipio"]) or None
        target.segment = pick(record, ["segmento", "producto", "tipo_producto"]) or "General"
        target.obligation = pick(record, ["obligacion", "cuenta", "credito", "account"]) or "Obligacion principal"
        target.balance = balance
        target.original_balance = original_balance
        target.dpd = dpd
        target.status = existing.status if existing else "Sin contacto"
        target.risk = risk
        target.priority = priority_score(dpd, balance, risk, target.status)
        target.next_action = next_action_for(target.status, risk)
        target.contactability = existing.contactability if existing else "Media"
        if existing:
            updated += 1
        else:
            db.add(target)
            imported += 1
    batch = ImportBatch(
        tenant_id=project.tenant_id,
        project_id=project.id,
        user_id=user.id,
        file_name=payload.file_name,
        imported_count=imported,
        updated_count=updated,
        skipped_count=skipped,
    )
    db.add(batch)
    db.commit()
    return ImportCustomersResponse(imported_count=imported, updated_count=updated, skipped_count=skipped, batch_id=batch.id)


@router.get("/customers/{customer_id}/activities", response_model=list[ActivityOut])
def list_activities(customer_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ActivityOut]:
    ensure_read_access(user)
    customer_for_access(db, customer_id, user)
    activities = list(db.scalars(select(ManagementActivity).where(ManagementActivity.customer_id == customer_id).order_by(ManagementActivity.created_at.desc()).limit(10)))
    return [activity_to_out(db, item) for item in activities]


@router.post("/customers/{customer_id}/activities", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(customer_id: int, payload: ActivityCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ActivityOut:
    ensure_read_access(user)
    customer = customer_for_access(db, customer_id, user, write=True)
    typification = db.get(TypificationNode, payload.typification_id) if payload.typification_id else None
    if typification and typification.tenant_id != customer.tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tipificacion fuera de la empresa.")
    result = typification.next_status if typification and typification.next_status else payload.result
    activity = ManagementActivity(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        user_id=user.id,
        typification_id=payload.typification_id,
        channel=payload.channel,
        result=result,
        note=payload.note,
        next_contact_at=payload.next_contact_at,
    )
    now = datetime.now(timezone.utc)
    customer.status = result
    customer.last_contact_at = now
    customer.next_contact_at = payload.next_contact_at
    customer.next_action = next_action_for(result, customer.risk)
    customer.priority = priority_score(customer.dpd, customer.balance, customer.risk, result)
    db.add(activity)
    if payload.promise_amount and payload.promise_due_date:
        db.add(
            PaymentPromise(
                tenant_id=customer.tenant_id,
                project_id=customer.project_id,
                customer_id=customer.id,
                user_id=user.id,
                amount=payload.promise_amount,
                due_date=payload.promise_due_date,
                channel=payload.channel,
            )
        )
        customer.status = "Promesa"
        customer.next_action = "Confirmar cumplimiento de promesa"
    db.commit()
    db.refresh(activity)
    return activity_to_out(db, activity)


@router.get("/promises", response_model=list[PromiseOut])
def list_promises(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[PromiseOut]:
    ensure_read_access(user)
    customers = list(db.scalars(customer_query(db, user)))
    customer_map = {customer.id: customer for customer in customers}
    promises = list(db.scalars(select(PaymentPromise).where(PaymentPromise.customer_id.in_(customer_map.keys())).order_by(PaymentPromise.due_date.desc()))) if customer_map else []
    return [
        PromiseOut(
            id=item.id,
            customer_id=item.customer_id,
            customer_name=customer_map[item.customer_id].name if item.customer_id in customer_map else None,
            amount=item.amount,
            due_date=item.due_date,
            channel=item.channel,
            status=item.status,
            created_at=item.created_at,
        )
        for item in promises
    ]


@router.post("/promises", response_model=PromiseOut, status_code=status.HTTP_201_CREATED)
def create_promise(payload: PromiseCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PromiseOut:
    customer = customer_for_access(db, payload.customer_id, user, write=True)
    promise = PaymentPromise(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        user_id=user.id,
        amount=payload.amount,
        due_date=payload.due_date,
        channel=payload.channel,
    )
    customer.status = "Promesa"
    customer.next_action = "Confirmar cumplimiento de promesa"
    db.add(promise)
    db.commit()
    db.refresh(promise)
    return PromiseOut(id=promise.id, customer_id=customer.id, customer_name=customer.name, amount=promise.amount, due_date=promise.due_date, channel=promise.channel, status=promise.status, created_at=promise.created_at)


@router.patch("/promises/{promise_id}/complete", response_model=PromiseOut)
def complete_promise(promise_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PromiseOut:
    promise = db.get(PaymentPromise, promise_id)
    if promise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promesa no encontrada.")
    customer = customer_for_access(db, promise.customer_id, user, write=True)
    promise.status = "Cumplida"
    db.add(ManagementActivity(tenant_id=customer.tenant_id, project_id=customer.project_id, customer_id=customer.id, user_id=user.id, channel="manual", result="Promesa cumplida", note="Promesa marcada como cumplida."))
    db.commit()
    return PromiseOut(id=promise.id, customer_id=customer.id, customer_name=customer.name, amount=promise.amount, due_date=promise.due_date, channel=promise.channel, status=promise.status, created_at=promise.created_at)


@router.get("/payments", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[PaymentOut]:
    ensure_read_access(user)
    customers = list(db.scalars(customer_query(db, user)))
    customer_map = {customer.id: customer for customer in customers}
    payments = list(db.scalars(select(Payment).where(Payment.customer_id.in_(customer_map.keys())).order_by(Payment.paid_at.desc()))) if customer_map else []
    return [
        PaymentOut(id=item.id, customer_id=item.customer_id, customer_name=customer_map[item.customer_id].name if item.customer_id in customer_map else None, amount=item.amount, paid_at=item.paid_at, method=item.method, reference=item.reference, created_at=item.created_at)
        for item in payments
    ]


@router.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PaymentOut:
    customer = customer_for_access(db, payload.customer_id, user, write=True)
    payment = Payment(
        tenant_id=customer.tenant_id,
        project_id=customer.project_id,
        customer_id=customer.id,
        user_id=user.id,
        amount=payload.amount,
        paid_at=payload.paid_at,
        method=payload.method,
        reference=payload.reference,
    )
    customer.balance = max(0, customer.balance - payload.amount)
    customer.status = "Pagado" if customer.balance == 0 else "Pago parcial"
    customer.next_action = "Cerrar caso" if customer.balance == 0 else "Confirmar saldo restante"
    db.add(payment)
    db.add(ManagementActivity(tenant_id=customer.tenant_id, project_id=customer.project_id, customer_id=customer.id, user_id=user.id, channel="payment", result=customer.status, note=f"Pago registrado por {payload.amount}."))
    db.commit()
    db.refresh(payment)
    return PaymentOut(id=payment.id, customer_id=customer.id, customer_name=customer.name, amount=payment.amount, paid_at=payment.paid_at, method=payment.method, reference=payment.reference, created_at=payment.created_at)


@router.get("/channels", response_model=list[CommunicationChannelOut])
def list_channels(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[CommunicationChannelOut]:
    ensure_read_access(user)
    query = select(CommunicationChannel).order_by(CommunicationChannel.kind, CommunicationChannel.label)
    if not is_platform(user):
        query = query.where(CommunicationChannel.tenant_id == user.tenant_id)
    channels = list(db.scalars(query))
    return [CommunicationChannelOut.model_validate(item, from_attributes=True) for item in channels]


@router.post("/channels", response_model=CommunicationChannelOut, status_code=status.HTTP_201_CREATED)
def create_channel(payload: CommunicationChannelCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CommunicationChannelOut:
    ensure_manage_access(user)
    tenant_id = payload.tenant_id if is_platform(user) and payload.tenant_id else user.tenant_id
    tenant = db.get(Tenant, tenant_id)
    if tenant is None or tenant.slug == settings.platform_tenant_slug:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Selecciona una empresa cliente.")
    if payload.project_id:
        project = project_for_access(db, payload.project_id, user)
        if project.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Proyecto fuera de la empresa.")
    if payload.is_default:
        existing = db.scalars(select(CommunicationChannel).where(CommunicationChannel.tenant_id == tenant_id, CommunicationChannel.kind == payload.kind))
        for item in existing:
            item.is_default = False
    channel = CommunicationChannel(
        tenant_id=tenant_id,
        project_id=payload.project_id,
        kind=payload.kind,
        label=payload.label,
        value=payload.value,
        provider=payload.provider,
        is_default=payload.is_default,
        status=payload.status,
        config_json=payload.config_json,
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return CommunicationChannelOut.model_validate(channel, from_attributes=True)
