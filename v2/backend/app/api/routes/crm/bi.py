from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import CommunicationChannel, Customer, ManagementActivity, Payment, PaymentPromise, Project, User
from app.schemas.crm import BIResponse
from app.services.access_control import require_permission

from .access import customer_query, ensure_read_access, is_platform, project_for_access
from .utils import activity_is_stale, aging_bucket_label, clamp, next_action_for, recovery_probability, semaphore_status


router = APIRouter()


@router.get("/bi", response_model=BIResponse)
def business_intelligence(
    tenant_id: int | None = None,
    project_id: int | None = None,
    horizon_days: int = Query(default=30, ge=7, le=180),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    require_permission(db, user, "reports.view")
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
        score = int(
            clamp(
                (project_contact * 0.35)
                + ((100 - risk_share) * 0.3)
                + (min(100, (project_recovered / max(project_balance + project_recovered, 1)) * 350) * 0.35),
                0,
                100,
            )
        )
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
    visible_users = list(db.scalars(select(User).where(User.id.in_(assigned_user_ids), User.role == "agent"))) if assigned_user_ids else []
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
