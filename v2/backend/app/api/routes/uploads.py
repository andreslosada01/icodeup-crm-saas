from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from io import StringIO
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.routes.crm.utils import next_action_for, priority_score, risk_from_dpd
from app.db.session import get_db
from app.models import Customer, CustomerDemographic, CustomerObligation, ManagementActivity, Payment, Project, UploadBatch, User, UserProjectAssignment
from app.schemas.collection_ops import CustomerDemographicCreate, CustomerDemographicOut, UploadBatchOut, UploadConfirmRequest, UploadPreviewRequest, UploadPreviewResponse
from app.services.access_control import is_platform_admin, require_permission, require_tenant, user_has_permission
from app.services.audit_service import record_audit
from app.services.plan_limits import check_customer_limit


router = APIRouter()

PREVIEW_LIMIT = 20

FIELD_SYNONYMS: dict[str, list[str]] = {
    "document": ["document", "documento", "cedula", "identificacion", "nit", "id_cliente", "numero_documento"],
    "name": ["name", "nombre", "cliente", "deudor", "razon_social", "nombre_cliente"],
    "phone": ["phone", "telefono", "celular", "movil", "telefono_1", "tel1"],
    "email": ["email", "correo", "correo_electronico", "mail"],
    "city": ["city", "ciudad", "municipio"],
    "address": ["address", "direccion", "direccion_residencia"],
    "state": ["state", "departamento", "estado", "region"],
    "segment": ["segment", "segmento", "cartera", "portafolio"],
    "obligation": ["obligation", "obligacion", "producto", "credito"],
    "obligation_number": ["obligation_number", "numero_obligacion", "obligacion", "credito", "pagare", "referencia_obligacion"],
    "product_type": ["product_type", "producto", "tipo_producto", "linea"],
    "portfolio_name": ["portfolio_name", "cartera", "portafolio", "campana"],
    "purchase_number": ["purchase_number", "compra", "numero_compra"],
    "balance": ["balance", "saldo", "saldo_total", "saldo_actual", "valor"],
    "original_balance": ["original_balance", "saldo_original", "valor_original"],
    "current_balance": ["current_balance", "saldo_actual", "saldo", "capital"],
    "capital_amount": ["capital_amount", "capital"],
    "interest_amount": ["interest_amount", "intereses", "interes"],
    "fees_amount": ["fees_amount", "gastos", "honorarios", "costos"],
    "dpd": ["dpd", "mora", "dias_mora", "dias_de_mora"],
    "days_past_due": ["days_past_due", "mora", "dias_mora", "dias_de_mora"],
    "status": ["status", "estado", "estado_cliente", "estado_obligacion"],
    "risk": ["risk", "riesgo"],
    "priority": ["priority", "prioridad"],
    "next_action": ["next_action", "siguiente_accion", "proxima_accion"],
    "contactability": ["contactability", "contactabilidad"],
    "notes": ["notes", "nota", "observacion", "observaciones"],
    "assigned_user_email": ["assigned_user_email", "gestor_email", "email_gestor", "asesor_email"],
    "assigned_user_id": ["assigned_user_id", "gestor_id", "asesor_id"],
    "assigned_user_name": ["assigned_user_name", "gestor", "asesor", "nombre_gestor"],
    "assigned_leader_email": ["assigned_leader_email", "lider_email", "email_lider", "coordinador_email"],
    "assigned_leader_id": ["assigned_leader_id", "lider_id", "coordinador_id"],
    "assigned_leader_name": ["assigned_leader_name", "lider", "coordinador", "nombre_lider"],
    "project_code": ["project_code", "codigo_proyecto", "codigo_cartera", "cartera_codigo"],
    "project_name": ["project_name", "proyecto", "cartera", "campana"],
    "source": ["source", "fuente", "origen"],
    "employer": ["employer", "empresa", "empleador"],
    "job_title": ["job_title", "cargo", "ocupacion"],
    "reference_name": ["reference_name", "referencia", "nombre_referencia"],
    "reference_phone": ["reference_phone", "telefono_referencia", "tel_referencia"],
    "score": ["score", "puntaje", "score_contactabilidad"],
    "amount": ["amount", "valor_pago", "pago", "monto", "valor"],
    "paid_at": ["paid_at", "fecha_pago", "fecha", "fecha_recaudo"],
    "method": ["method", "metodo", "medio_pago", "canal_pago"],
    "reference": ["reference", "referencia", "referencia_pago", "comprobante"],
    "channel": ["channel", "canal", "medio"],
    "result": ["result", "resultado", "novedad", "gestion"],
    "next_contact_at": ["next_contact_at", "proxima_gestion", "siguiente_fecha"],
}

UPLOAD_TYPE_CONFIG: dict[str, dict[str, Any]] = {
    "clientes": {
        "label": "Clientes",
        "permission": "uploads.manage",
        "required": ["document", "name"],
        "optional": ["phone", "email", "city", "address", "segment", "balance", "dpd", "status", "risk", "assigned_user_email", "project_code"],
        "template": ["documento", "cliente", "telefono", "email", "ciudad", "segmento", "saldo", "dias_mora", "estado", "riesgo", "gestor_email", "codigo_cartera"],
    },
    "obligaciones": {
        "label": "Obligaciones",
        "permission": "uploads.repartos.manage",
        "required": ["document", "obligation_number"],
        "optional": ["name", "product_type", "portfolio_name", "current_balance", "original_balance", "days_past_due", "risk", "assigned_user_email", "assigned_leader_email", "project_code"],
        "template": ["documento", "cliente", "numero_obligacion", "producto", "cartera", "saldo_actual", "saldo_original", "dias_mora", "riesgo", "gestor_email", "lider_email", "codigo_cartera"],
    },
    "reparto_cartera": {
        "label": "Reparto de cartera",
        "permission": "uploads.repartos.manage",
        "required": ["document"],
        "optional": ["name", "obligation_number", "portfolio_name", "current_balance", "days_past_due", "assigned_user_email", "assigned_leader_email", "project_code"],
        "template": ["documento", "cliente", "numero_obligacion", "cartera", "saldo_actual", "dias_mora", "gestor_email", "lider_email", "codigo_cartera"],
    },
    "demograficos": {
        "label": "Demograficos",
        "permission": "uploads.demographics.manage",
        "required": ["document"],
        "optional": ["phone", "email", "address", "city", "state", "employer", "job_title", "reference_name", "reference_phone", "source", "score"],
        "template": ["documento", "telefono", "email", "direccion", "ciudad", "departamento", "empleador", "cargo", "referencia", "telefono_referencia", "fuente", "score"],
    },
    "telefonos_emails_direcciones": {
        "label": "Telefonos, emails y direcciones",
        "permission": "uploads.demographics.manage",
        "required": ["document"],
        "optional": ["phone", "email", "address", "city", "state", "source", "score"],
        "template": ["documento", "telefono", "email", "direccion", "ciudad", "departamento", "fuente", "score"],
    },
    "pagos": {
        "label": "PayControl 360",
        "permission": "uploads.manage",
        "required": ["document", "amount"],
        "optional": ["obligation_number", "paid_at", "method", "reference"],
        "template": ["documento", "numero_obligacion", "valor_pago", "fecha_pago", "metodo", "referencia_pago"],
    },
    "novedades_operativas": {
        "label": "Novedades operativas",
        "permission": "uploads.manage",
        "required": ["document", "result"],
        "optional": ["obligation_number", "channel", "notes", "next_contact_at"],
        "template": ["documento", "numero_obligacion", "canal", "resultado", "observacion", "proxima_gestion"],
    },
}


def _normalize(value: str | None) -> str:
    from app.api.routes.crm.utils import normalize_header

    return normalize_header(value or "")


def _detect_delimiter(text: str) -> str:
    first_line = next((line for line in text.splitlines() if line.strip()), "")
    return ";" if first_line.count(";") > first_line.count(",") else ","


def _parse_csv(text: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(StringIO(text), delimiter=_detect_delimiter(text))
    columns = list(reader.fieldnames or [])
    rows = []
    for row in reader:
        clean = {key: (value or "").strip() for key, value in row.items() if key is not None}
        if any(clean.values()):
            rows.append(clean)
    return columns, rows


def _suggest_mapping(columns: list[str]) -> dict[str, str]:
    normalized_to_original = {_normalize(column): column for column in columns}
    mapping: dict[str, str] = {}
    for field, synonyms in FIELD_SYNONYMS.items():
        for synonym in synonyms:
            source = normalized_to_original.get(_normalize(synonym))
            if source:
                mapping[field] = source
                break
    return mapping


def _effective_mapping(payload_mapping: dict[str, str], suggested_mapping: dict[str, str]) -> dict[str, str]:
    mapping = {**suggested_mapping}
    for field, source in payload_mapping.items():
        if source:
            mapping[_normalize(field)] = source
    return mapping


def _row_value(row: dict[str, str], mapping: dict[str, str], field: str) -> str:
    normalized_row = {_normalize(key): value for key, value in row.items()}
    source = mapping.get(field) or mapping.get(_normalize(field))
    if source:
        value = normalized_row.get(_normalize(source), "")
        if value:
            return value.strip()
    for synonym in FIELD_SYNONYMS.get(field, [field]):
        value = normalized_row.get(_normalize(synonym), "")
        if value:
            return value.strip()
    return ""


def _parse_int(value: str | None, default: int = 0) -> int:
    if not value:
        return default
    clean = re.sub(r"[^\d,.-]", "", value)
    if "," in clean and "." in clean:
        clean = clean.replace(".", "").replace(",", ".") if clean.rfind(",") > clean.rfind(".") else clean.replace(",", "")
    elif clean.count(".") > 1:
        clean = clean.replace(".", "")
    elif clean.count(",") > 1:
        clean = clean.replace(",", "")
    elif "," in clean:
        clean = clean.replace(",", ".")
    try:
        return max(0, round(float(clean)))
    except ValueError:
        return default


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    clean = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(clean, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        parsed = datetime.fromisoformat(clean.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _config_for(upload_type: str) -> dict[str, Any]:
    config = UPLOAD_TYPE_CONFIG.get(upload_type)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tipo de carga no soportado. Usa: {', '.join(UPLOAD_TYPE_CONFIG)}.",
        )
    return config


def _resolve_scope(db: Session, user: User, tenant_id: int | None, project_id: int | None) -> tuple[int, Project | None]:
    if project_id:
        project = db.get(Project, project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado.")
        tenant = require_tenant(db, user, tenant_id or project.tenant_id)
        if project.tenant_id != tenant.id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Proyecto fuera de la empresa.")
        return tenant.id, project
    tenant = require_tenant(db, user, tenant_id)
    return tenant.id, None


def _require_upload_permission(db: Session, user: User, upload_type: str, action: str) -> None:
    config = _config_for(upload_type)
    if action == "preview" and user_has_permission(db, user, "uploads.preview"):
        return
    if action == "confirm" and user_has_permission(db, user, "uploads.confirm"):
        specific = config["permission"]
        if user_has_permission(db, user, specific) or user_has_permission(db, user, "uploads.manage"):
            return
    require_permission(db, user, config["permission"] if action == "confirm" else "uploads.view")


def _project_from_row(db: Session, tenant_id: int, default_project: Project | None, row: dict[str, str], mapping: dict[str, str]) -> Project | None:
    raw_id = _row_value(row, mapping, "project_id")
    if raw_id.isdigit():
        project = db.get(Project, int(raw_id))
        if project is None or project.tenant_id != tenant_id:
            raise ValueError("Proyecto indicado no pertenece a la empresa.")
        return project
    code = _row_value(row, mapping, "project_code")
    name = _row_value(row, mapping, "project_name")
    if code or name:
        normalized_code = _normalize(code or name)
        normalized_name = _normalize(name or code)
        project = db.scalar(select(Project).where(Project.tenant_id == tenant_id, Project.code == code)) if code else None
        if project is None:
            projects = db.scalars(select(Project).where(Project.tenant_id == tenant_id)).all()
            project = next((item for item in projects if _normalize(item.code) == normalized_code or _normalize(item.name) == normalized_name), None)
        if project is None:
            raise ValueError("No se encontro el proyecto/cartera indicado.")
        return project
    return default_project


def _user_from_row(db: Session, tenant_id: int, row: dict[str, str], mapping: dict[str, str], prefix: str) -> User | None:
    raw_id = _row_value(row, mapping, f"{prefix}_id")
    email = _row_value(row, mapping, f"{prefix}_email")
    name = _row_value(row, mapping, f"{prefix}_name")
    user: User | None = None
    if raw_id.isdigit():
        user = db.get(User, int(raw_id))
    elif email:
        user = db.scalar(select(User).where(User.tenant_id == tenant_id, User.email == email.lower()))
    elif name:
        users = db.scalars(select(User).where(User.tenant_id == tenant_id)).all()
        user = next((item for item in users if _normalize(item.name) == _normalize(name)), None)
    if (raw_id or email or name) and (user is None or user.tenant_id != tenant_id):
        raise ValueError(f"No se encontro {prefix.replace('_', ' ')} en la empresa.")
    return user


def _find_customer(db: Session, tenant_id: int, document: str) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.tenant_id == tenant_id, Customer.document == document))


def _find_obligation(db: Session, tenant_id: int, obligation_number: str) -> CustomerObligation | None:
    return db.scalar(select(CustomerObligation).where(CustomerObligation.tenant_id == tenant_id, CustomerObligation.obligation_number == obligation_number))


def _ensure_project_assignment(db: Session, tenant_id: int, project: Project | None, target_user: User | None, role_in_project: str) -> None:
    if project is None or target_user is None:
        return
    assignment = db.scalar(select(UserProjectAssignment).where(UserProjectAssignment.user_id == target_user.id, UserProjectAssignment.project_id == project.id))
    if assignment is None:
        assignment = UserProjectAssignment(tenant_id=tenant_id, user_id=target_user.id, project_id=project.id)
        db.add(assignment)
    assignment.tenant_id = tenant_id
    assignment.role_in_project = role_in_project
    assignment.is_active = True


def _customer_payload(row: dict[str, str], mapping: dict[str, str]) -> dict[str, Any]:
    raw_balance = _row_value(row, mapping, "balance") or _row_value(row, mapping, "current_balance")
    raw_original_balance = _row_value(row, mapping, "original_balance")
    raw_dpd = _row_value(row, mapping, "dpd") or _row_value(row, mapping, "days_past_due")
    balance = _parse_int(raw_balance) if raw_balance else None
    dpd = _parse_int(raw_dpd) if raw_dpd else None
    status_value = _row_value(row, mapping, "status")
    risk_value = _row_value(row, mapping, "risk")
    risk = risk_value or (risk_from_dpd(dpd or 0, balance or 0) if raw_balance or raw_dpd else None)
    status_for_score = status_value or "Sin contacto"
    risk_for_score = risk or risk_from_dpd(dpd or 0, balance or 0)
    raw_priority = _row_value(row, mapping, "priority")
    return {
        "name": _row_value(row, mapping, "name"),
        "document": _row_value(row, mapping, "document"),
        "phone": _row_value(row, mapping, "phone") or None,
        "email": (_row_value(row, mapping, "email") or "").lower() or None,
        "city": _row_value(row, mapping, "city") or None,
        "segment": _row_value(row, mapping, "segment") or None,
        "obligation": _row_value(row, mapping, "obligation") or None,
        "balance": balance,
        "original_balance": _parse_int(raw_original_balance, balance or 0) if raw_original_balance or balance is not None else None,
        "dpd": dpd,
        "status": status_value or None,
        "risk": risk,
        "priority": _parse_int(raw_priority, priority_score(dpd or 0, balance or 0, risk_for_score, status_for_score)) if raw_priority or raw_balance or raw_dpd or status_value or risk else None,
        "next_action": _row_value(row, mapping, "next_action") or (next_action_for(status_for_score, risk_for_score) if status_value or risk else None),
        "contactability": _row_value(row, mapping, "contactability") or None,
        "notes": _row_value(row, mapping, "notes") or None,
    }


def _upsert_customer(db: Session, tenant_id: int, project: Project | None, row: dict[str, str], mapping: dict[str, str], user: User) -> tuple[Customer, str]:
    payload = _customer_payload(row, mapping)
    if not payload["document"]:
        raise ValueError("Documento requerido.")
    customer = _find_customer(db, tenant_id, payload["document"])
    action = "updated"
    if customer is None:
        if not payload["name"]:
            raise ValueError("Cliente no existe y falta nombre para crearlo.")
        check_customer_limit(db, tenant_id, user=user)
        customer = Customer(tenant_id=tenant_id, project_id=project.id if project else None, name=payload["name"], document=payload["document"])
        db.add(customer)
        action = "created"
    if project:
        customer.project_id = project.id
    for field in ("name", "phone", "email", "city", "segment", "obligation", "status", "risk", "priority", "next_action", "contactability", "notes"):
        value = payload.get(field)
        if value not in (None, ""):
            setattr(customer, field, value)
    for field in ("balance", "original_balance", "dpd"):
        if payload.get(field) is not None:
            setattr(customer, field, payload[field])
    assigned = _user_from_row(db, tenant_id, row, mapping, "assigned_user")
    if assigned:
        customer.assigned_user_id = assigned.id
        _ensure_project_assignment(db, tenant_id, project, assigned, "agent")
    leader = _user_from_row(db, tenant_id, row, mapping, "assigned_leader")
    if assigned and leader:
        assigned.leader_id = leader.id
        _ensure_project_assignment(db, tenant_id, project, leader, "leader")
    if customer.id is None:
        db.flush()
    return customer, action


def _upsert_obligation(db: Session, tenant_id: int, project: Project | None, customer: Customer, row: dict[str, str], mapping: dict[str, str]) -> tuple[CustomerObligation | None, str | None]:
    obligation_number = _row_value(row, mapping, "obligation_number")
    if not obligation_number:
        return None, None
    obligation = _find_obligation(db, tenant_id, obligation_number)
    action = "updated"
    current_balance = _parse_int(_row_value(row, mapping, "current_balance") or _row_value(row, mapping, "balance"))
    days_past_due = _parse_int(_row_value(row, mapping, "days_past_due") or _row_value(row, mapping, "dpd"))
    risk = _row_value(row, mapping, "risk") or risk_from_dpd(days_past_due, current_balance)
    if obligation is None:
        obligation = CustomerObligation(tenant_id=tenant_id, customer_id=customer.id, obligation_number=obligation_number)
        db.add(obligation)
        action = "created"
    elif obligation.customer_id != customer.id:
        raise ValueError("La obligacion existe asociada a otro cliente del tenant.")
    obligation.project_id = project.id if project else customer.project_id
    obligation.product_type = _row_value(row, mapping, "product_type") or obligation.product_type
    obligation.portfolio_name = _row_value(row, mapping, "portfolio_name") or obligation.portfolio_name
    obligation.purchase_number = _row_value(row, mapping, "purchase_number") or obligation.purchase_number
    obligation.original_amount = _parse_int(_row_value(row, mapping, "original_balance"), current_balance or obligation.original_amount)
    obligation.current_balance = current_balance or obligation.current_balance
    obligation.capital_amount = _parse_int(_row_value(row, mapping, "capital_amount")) or obligation.capital_amount
    obligation.interest_amount = _parse_int(_row_value(row, mapping, "interest_amount")) or obligation.interest_amount
    obligation.fees_amount = _parse_int(_row_value(row, mapping, "fees_amount")) or obligation.fees_amount
    obligation.days_past_due = days_past_due or obligation.days_past_due
    obligation.status = _row_value(row, mapping, "status") or obligation.status
    obligation.risk = risk
    assigned = _user_from_row(db, tenant_id, row, mapping, "assigned_user")
    leader = _user_from_row(db, tenant_id, row, mapping, "assigned_leader")
    if assigned:
        obligation.assigned_user_id = assigned.id
        customer.assigned_user_id = assigned.id
        _ensure_project_assignment(db, tenant_id, project, assigned, "agent")
    if leader:
        obligation.assigned_leader_id = leader.id
        _ensure_project_assignment(db, tenant_id, project, leader, "leader")
        if assigned:
            assigned.leader_id = leader.id
    return obligation, action


def _upsert_demographic(db: Session, tenant_id: int, customer: Customer, row: dict[str, str], mapping: dict[str, str], default_source: str) -> tuple[CustomerDemographic, str]:
    source = _row_value(row, mapping, "source") or default_source
    phone = _row_value(row, mapping, "phone") or None
    email = (_row_value(row, mapping, "email") or "").lower() or None
    address = _row_value(row, mapping, "address") or None
    existing = db.scalar(
        select(CustomerDemographic).where(
            CustomerDemographic.tenant_id == tenant_id,
            CustomerDemographic.customer_id == customer.id,
            CustomerDemographic.source == source,
            CustomerDemographic.phone == phone,
            CustomerDemographic.email == email,
            CustomerDemographic.address == address,
        )
    )
    action = "updated"
    demographic = existing
    if demographic is None:
        demographic = CustomerDemographic(tenant_id=tenant_id, customer_id=customer.id, source=source)
        db.add(demographic)
        action = "created"
    demographic.phone = phone or demographic.phone
    demographic.email = email or demographic.email
    demographic.address = address or demographic.address
    demographic.city = _row_value(row, mapping, "city") or demographic.city
    demographic.state = _row_value(row, mapping, "state") or demographic.state
    demographic.employer = _row_value(row, mapping, "employer") or demographic.employer
    demographic.job_title = _row_value(row, mapping, "job_title") or demographic.job_title
    demographic.reference_name = _row_value(row, mapping, "reference_name") or demographic.reference_name
    demographic.reference_phone = _row_value(row, mapping, "reference_phone") or demographic.reference_phone
    demographic.score = _parse_int(_row_value(row, mapping, "score"), demographic.score)
    demographic.metadata_json = json.dumps({"upload": True, "file_source": default_source}, ensure_ascii=True)
    return demographic, action


def _create_payment(db: Session, tenant_id: int, project: Project | None, customer: Customer, row: dict[str, str], mapping: dict[str, str], user: User, file_name: str | None, row_number: int) -> tuple[Payment, str]:
    amount = _parse_int(_row_value(row, mapping, "amount"))
    if amount <= 0:
        raise ValueError("Valor de pago invalido.")
    paid_at = _parse_datetime(_row_value(row, mapping, "paid_at")) or datetime.now(timezone.utc)
    method = _row_value(row, mapping, "method") or "Carga masiva"
    reference = _row_value(row, mapping, "reference")
    if not reference:
        fingerprint = hashlib.sha1(f"{tenant_id}:{file_name}:{row_number}:{customer.document}:{amount}:{paid_at.date()}".encode("utf-8")).hexdigest()[:16]
        reference = f"UPLOAD-{fingerprint}"
    existing = db.scalar(select(Payment).where(Payment.tenant_id == tenant_id, Payment.customer_id == customer.id, Payment.reference == reference))
    if existing:
        return existing, "updated"
    payment = Payment(tenant_id=tenant_id, project_id=project.id if project else customer.project_id, customer_id=customer.id, user_id=user.id, amount=amount, paid_at=paid_at, method=method, reference=reference)
    customer.balance = max(0, customer.balance - amount)
    customer.status = "Pagado" if customer.balance == 0 else "Pago parcial"
    customer.next_action = "Cerrar caso" if customer.balance == 0 else "Confirmar saldo restante"
    db.add(payment)
    db.add(
        ManagementActivity(
            tenant_id=tenant_id,
            project_id=payment.project_id,
            customer_id=customer.id,
            user_id=user.id,
            channel="payment_upload",
            result=customer.status,
            note=f"Pago cargado por archivo por {amount}.",
        )
    )
    return payment, "created"


def _create_activity(db: Session, tenant_id: int, project: Project | None, customer: Customer, row: dict[str, str], mapping: dict[str, str], user: User) -> tuple[ManagementActivity, str]:
    obligation = None
    obligation_number = _row_value(row, mapping, "obligation_number")
    if obligation_number:
        obligation = _find_obligation(db, tenant_id, obligation_number)
    activity = ManagementActivity(
        tenant_id=tenant_id,
        project_id=project.id if project else customer.project_id,
        customer_id=customer.id,
        obligation_id=obligation.id if obligation else None,
        user_id=user.id,
        channel=_row_value(row, mapping, "channel") or "upload",
        result=_row_value(row, mapping, "result") or "Novedad cargada",
        note=_row_value(row, mapping, "notes") or None,
        next_contact_at=_parse_datetime(_row_value(row, mapping, "next_contact_at")),
    )
    db.add(activity)
    customer.status = activity.result
    customer.next_action = activity.note or customer.next_action
    return activity, "created"


def _validate_rows(db: Session, tenant_id: int, project: Project | None, payload: UploadPreviewRequest, columns: list[str], rows: list[dict[str, str]]) -> tuple[dict[str, str], list[dict[str, Any]], list[dict[str, str]]]:
    config = _config_for(payload.upload_type)
    suggested_mapping = _suggest_mapping(columns)
    mapping = _effective_mapping(payload.mapping, suggested_mapping)
    errors: list[dict[str, Any]] = []
    valid_rows: list[dict[str, str]] = []
    for row_index, row in enumerate(rows, start=2):
        row_errors: list[str] = []
        for field in config["required"]:
            if not _row_value(row, mapping, field):
                row_errors.append(f"Falta {field}.")
        for money_field in {"balance", "original_balance", "current_balance", "amount", "capital_amount", "interest_amount", "fees_amount"}:
            value = _row_value(row, mapping, money_field)
            if value and _parse_int(value) < 0:
                row_errors.append(f"{money_field} invalido.")
        for date_field in {"paid_at", "next_contact_at"}:
            value = _row_value(row, mapping, date_field)
            if value and _parse_datetime(value) is None:
                row_errors.append(f"{date_field} invalido.")
        try:
            _project_from_row(db, tenant_id, project, row, mapping)
            _user_from_row(db, tenant_id, row, mapping, "assigned_user")
            _user_from_row(db, tenant_id, row, mapping, "assigned_leader")
        except ValueError as exc:
            row_errors.append(str(exc))
        if payload.upload_type in {"demograficos", "telefonos_emails_direcciones", "pagos", "novedades_operativas"}:
            document = _row_value(row, mapping, "document")
            if document and _find_customer(db, tenant_id, document) is None and not _row_value(row, mapping, "name"):
                row_errors.append("Cliente no existe; carga primero clientes/reparto o incluye nombre.")
        if row_errors:
            errors.append({"row": row_index, "document": _row_value(row, mapping, "document"), "errors": row_errors, "message": " | ".join(row_errors)})
        else:
            valid_rows.append(row)
    return mapping, errors, valid_rows


def _preview(payload: UploadPreviewRequest, db: Session, tenant_id: int, project: Project | None) -> UploadPreviewResponse:
    columns, rows = _parse_csv(payload.csv_text)
    config = _config_for(payload.upload_type)
    mapping, errors, valid_rows = _validate_rows(db, tenant_id, project, payload, columns, rows)
    return UploadPreviewResponse(
        upload_type=payload.upload_type,
        file_name=payload.file_name,
        total_rows=len(rows),
        valid_rows=len(valid_rows),
        error_rows=len(errors),
        columns=columns,
        sample=rows[:PREVIEW_LIMIT],
        suggested_mapping=mapping,
        required_fields=config["required"],
        optional_fields=config["optional"],
        summary={
            "label": config["label"],
            "preview_limit": PREVIEW_LIMIT,
            "delimiter": _detect_delimiter(payload.csv_text),
            "message": "Preview listo. Confirma la carga para procesar filas validas.",
        },
        errors=errors[:100],
    )


@router.post("/preview", response_model=UploadPreviewResponse)
def preview_upload(payload: UploadPreviewRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> UploadPreviewResponse:
    _require_upload_permission(db, user, payload.upload_type, "preview")
    tenant_id, project = _resolve_scope(db, user, payload.tenant_id, payload.project_id)
    return _preview(payload, db, tenant_id, project)


@router.post("/confirm", response_model=UploadBatchOut, status_code=status.HTTP_201_CREATED)
def confirm_upload(payload: UploadConfirmRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> UploadBatch:
    _require_upload_permission(db, user, payload.upload_type, "confirm")
    tenant_id, default_project = _resolve_scope(db, user, payload.tenant_id, payload.project_id)
    columns, rows = _parse_csv(payload.csv_text)
    mapping, errors, valid_rows = _validate_rows(db, tenant_id, default_project, payload, columns, rows)
    created_rows = 0
    updated_rows = 0
    result_rows: list[dict[str, Any]] = []
    if payload.create_records:
        valid_row_ids = {id(row) for row in valid_rows}
        for row_number, row in enumerate(rows, start=2):
            if id(row) not in valid_row_ids:
                continue
            try:
                project = _project_from_row(db, tenant_id, default_project, row, mapping)
                customer: Customer | None = None
                customer_action: str | None = None
                if payload.upload_type in {"clientes", "obligaciones", "reparto_cartera"}:
                    customer, customer_action = _upsert_customer(db, tenant_id, project, row, mapping, user)
                else:
                    document = _row_value(row, mapping, "document")
                    customer = _find_customer(db, tenant_id, document)
                    if customer is None and _row_value(row, mapping, "name"):
                        customer, customer_action = _upsert_customer(db, tenant_id, project, row, mapping, user)
                    if customer is None:
                        raise ValueError("Cliente no encontrado.")
                row_actions: list[str] = []
                if customer_action:
                    row_actions.append(f"customer_{customer_action}")
                    created_rows += 1 if customer_action == "created" else 0
                    updated_rows += 1 if customer_action == "updated" else 0
                if payload.upload_type in {"obligaciones", "reparto_cartera"} and customer:
                    obligation, obligation_action = _upsert_obligation(db, tenant_id, project, customer, row, mapping)
                    if obligation_action:
                        row_actions.append(f"obligation_{obligation_action}")
                        created_rows += 1 if obligation_action == "created" else 0
                        updated_rows += 1 if obligation_action == "updated" else 0
                if payload.upload_type in {"demograficos", "telefonos_emails_direcciones"} and customer:
                    _demographic, demographic_action = _upsert_demographic(db, tenant_id, customer, row, mapping, payload.upload_type)
                    row_actions.append(f"demographic_{demographic_action}")
                    created_rows += 1 if demographic_action == "created" else 0
                    updated_rows += 1 if demographic_action == "updated" else 0
                if payload.upload_type == "pagos" and customer:
                    _payment, payment_action = _create_payment(db, tenant_id, project, customer, row, mapping, user, payload.file_name, row_number)
                    row_actions.append(f"payment_{payment_action}")
                    created_rows += 1 if payment_action == "created" else 0
                    updated_rows += 1 if payment_action == "updated" else 0
                if payload.upload_type == "novedades_operativas" and customer:
                    _activity, activity_action = _create_activity(db, tenant_id, project, customer, row, mapping, user)
                    row_actions.append(f"activity_{activity_action}")
                    created_rows += 1
                result_rows.append({"row": row_number, "document": _row_value(row, mapping, "document"), "status": "processed", "actions": ", ".join(row_actions) or "validated"})
            except ValueError as exc:
                errors.append({"row": row_number, "document": _row_value(row, mapping, "document"), "errors": [str(exc)], "message": str(exc)})
    else:
        result_rows = [{"row": row_number, "document": _row_value(row, mapping, "document"), "status": "validated", "actions": "no_records_created"} for row_number, row in enumerate(valid_rows, start=2)]
    batch = UploadBatch(
        tenant_id=tenant_id,
        project_id=default_project.id if default_project else None,
        uploaded_by_id=user.id,
        upload_type=payload.upload_type,
        original_filename=payload.file_name,
        status="completed" if not errors else "completed_with_errors",
        total_rows=len(rows),
        valid_rows=max(0, len(rows) - len(errors)),
        error_rows=len(errors),
        created_rows=created_rows,
        updated_rows=updated_rows,
        mapping_json=json.dumps(mapping, ensure_ascii=True),
        summary_json=json.dumps(
            {
                "columns": columns,
                "mapping": mapping,
                "errors": errors[:500],
                "results": result_rows[:1000],
                "upload_type": payload.upload_type,
                "create_records": payload.create_records,
            },
            ensure_ascii=True,
            default=str,
        ),
        error_file_path=f"dynamic://upload_batches/{payload.upload_type}/errors" if errors else None,
        result_file_path=f"dynamic://upload_batches/{payload.upload_type}/result",
    )
    db.add(batch)
    db.flush()
    record_audit(
        db,
        user,
        "upload_batch",
        "confirm",
        entity_id=batch.id,
        tenant_id=tenant_id,
        module="uploads",
        after={"upload_type": payload.upload_type, "rows": len(rows), "valid": batch.valid_rows, "errors": batch.error_rows},
        request=request,
    )
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/templates/{upload_type}")
def upload_template(upload_type: str, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str]:
    _require_upload_permission(db, user, upload_type, "preview")
    config = _config_for(upload_type)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(config["template"])
    writer.writerow(_sample_template_row(upload_type, config["template"]))
    return {"upload_type": upload_type, "filename": f"plantilla_{upload_type}_iep.csv", "csv_text": output.getvalue()}


def _sample_template_row(upload_type: str, columns: list[str]) -> list[str]:
    sample_values = {
        "documento": "900000001",
        "cliente": "Cliente Demo Uno",
        "telefono": "3000000001",
        "email": "cliente.demo001@demo.local",
        "ciudad": "Bogota",
        "segmento": "Consumo",
        "saldo": "3500000",
        "saldo_actual": "3500000",
        "saldo_original": "4200000",
        "dias_mora": "45",
        "estado": "Sin contacto",
        "riesgo": "Medio",
        "gestor_email": "gestor1.andina@demo.icodeup.local",
        "lider_email": "coord.cobranzas.andina@demo.icodeup.local",
        "codigo_cartera": "BANCO-FERIAS",
        "numero_obligacion": "OBL-DEMO-001",
        "producto": "Credito consumo",
        "cartera": "Banco Ferias",
        "direccion": "Calle demo 123",
        "departamento": "Cundinamarca",
        "empleador": "Empresa Demo",
        "cargo": "Analista",
        "referencia": "Referencia Demo",
        "telefono_referencia": "3000000099",
        "fuente": upload_type,
        "score": "85",
        "valor_pago": "250000",
        "fecha_pago": "2026-06-04",
        "metodo": "Transferencia demo",
        "referencia_pago": "PAGO-DEMO-001",
        "canal": "telefonia",
        "resultado": "Contacto efectivo",
        "observacion": "Novedad demo cargada por archivo",
        "proxima_gestion": "2026-06-10",
    }
    return [sample_values.get(column, "") for column in columns]


@router.get("/batches", response_model=list[UploadBatchOut])
def list_batches(upload_type: str | None = None, page: int = 1, page_size: int = 20, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[UploadBatch]:
    require_permission(db, user, "uploads.view")
    page = max(1, page)
    page_size = min(max(page_size, 1), 20)
    query = select(UploadBatch).order_by(UploadBatch.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    if not is_platform_admin(db, user):
        query = query.where(UploadBatch.tenant_id == user.tenant_id)
    if upload_type:
        query = query.where(UploadBatch.upload_type == upload_type)
    return list(db.scalars(query))


@router.get("/batches/{batch_id}", response_model=UploadBatchOut)
def get_batch(batch_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> UploadBatch:
    require_permission(db, user, "uploads.view")
    batch = db.get(UploadBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado.")
    if not is_platform_admin(db, user) and batch.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lote fuera de tu empresa.")
    return batch


def _summary(batch: UploadBatch) -> dict[str, Any]:
    return json.loads(batch.summary_json or "{}")


def _csv_payload(rows: list[dict[str, Any]], filename: str, empty_message: str) -> dict[str, str]:
    output = StringIO()
    if rows:
        fieldnames = sorted({key for row in rows for key in row.keys()})
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    else:
        writer = csv.writer(output)
        writer.writerow(["message"])
        writer.writerow([empty_message])
    return {"filename": filename, "csv_text": output.getvalue()}


@router.get("/batches/{batch_id}/errors")
def batch_errors(batch_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str]:
    require_permission(db, user, "uploads.download")
    batch = get_batch(batch_id, db, user)
    summary = _summary(batch)
    return _csv_payload(summary.get("errors", []), f"errores_lote_{batch.id}.csv", "El lote no tiene errores.")


@router.get("/batches/{batch_id}/result")
def batch_result(batch_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str]:
    require_permission(db, user, "uploads.download")
    batch = get_batch(batch_id, db, user)
    summary = _summary(batch)
    return _csv_payload(summary.get("results", []), f"resultado_lote_{batch.id}.csv", "El lote no tiene resultados operativos almacenados.")


@router.get("/demographics", response_model=list[CustomerDemographicOut])
def list_demographics(customer_id: int | None = None, page: int = 1, page_size: int = 20, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[CustomerDemographicOut]:
    require_permission(db, user, "demographics.view")
    page_size = min(max(page_size, 1), 20)
    query = select(CustomerDemographic).order_by(CustomerDemographic.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    if not is_platform_admin(db, user):
        query = query.where(CustomerDemographic.tenant_id == user.tenant_id)
    if customer_id:
        query = query.where(CustomerDemographic.customer_id == customer_id)
    return [_demographic_to_out(item) for item in db.scalars(query)]


@router.post("/demographics", response_model=CustomerDemographicOut, status_code=status.HTTP_201_CREATED)
def create_demographic(payload: CustomerDemographicCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CustomerDemographicOut:
    require_permission(db, user, "demographics.manage")
    tenant = require_tenant(db, user, payload.tenant_id)
    customer = db.get(Customer, payload.customer_id)
    if customer is None or customer.tenant_id != tenant.id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente fuera de la empresa.")
    existing = db.scalar(
        select(CustomerDemographic).where(
            CustomerDemographic.tenant_id == tenant.id,
            CustomerDemographic.customer_id == customer.id,
            CustomerDemographic.source == payload.source,
            CustomerDemographic.phone == payload.phone,
            CustomerDemographic.email == payload.email,
        )
    )
    if existing:
        return _demographic_to_out(existing)
    demographic = CustomerDemographic(**payload.model_dump(exclude={"tenant_id", "metadata"}), tenant_id=tenant.id, metadata_json=json.dumps(payload.metadata))
    db.add(demographic)
    db.flush()
    record_audit(db, user, "customer_demographic", "create", entity_id=demographic.id, tenant_id=tenant.id, module="uploads", after={"customer_id": customer.id, "source": payload.source}, request=request)
    db.commit()
    db.refresh(demographic)
    return _demographic_to_out(demographic)


def _demographic_to_out(item: CustomerDemographic) -> CustomerDemographicOut:
    return CustomerDemographicOut(
        id=item.id,
        tenant_id=item.tenant_id,
        customer_id=item.customer_id,
        source=item.source,
        phone=item.phone,
        email=item.email,
        address=item.address,
        city=item.city,
        state=item.state,
        employer=item.employer,
        job_title=item.job_title,
        reference_name=item.reference_name,
        reference_phone=item.reference_phone,
        score=item.score,
        metadata=json.loads(item.metadata_json or "{}"),
        is_active=item.is_active,
        created_at=item.created_at,
    )
