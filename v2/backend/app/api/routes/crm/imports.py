from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Customer, ImportBatch, User
from app.schemas.crm import ImportCustomersRequest, ImportCustomersResponse
from app.services.audit_service import record_audit
from app.services.access_control import require_permission
from app.services.plan_limits import check_customer_limit

from .access import ensure_manage_access, project_for_access, validate_assigned_user
from .utils import next_action_for, parse_csv_records, parse_money, pick, priority_score, risk_from_dpd


router = APIRouter()


@router.post("/customers/import", response_model=ImportCustomersResponse)
def import_customers(payload: ImportCustomersRequest, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ImportCustomersResponse:
    require_permission(db, user, "crm.clients.import")
    ensure_manage_access(user)
    project = project_for_access(db, payload.project_id, user)
    validate_assigned_user(db, project.tenant_id, payload.assigned_user_id)
    records = parse_csv_records(payload.csv_text)
    new_records = 0
    for record in records:
        name = pick(record, ["nombre", "cliente", "name"])
        document = pick(record, ["documento", "cedula", "nit", "identificacion", "id"])
        if not name or not document:
            continue
        existing = db.scalar(
            select(Customer.id).where(
                Customer.tenant_id == project.tenant_id,
                Customer.project_id == project.id,
                Customer.document == document.strip(),
            )
        )
        if existing is None:
            new_records += 1
    check_customer_limit(db, project.tenant_id, increment=new_records, user=user)
    imported = updated = skipped = 0
    for record in records:
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
    db.flush()
    record_audit(
        db,
        user,
        "import_batch",
        "create",
        batch.id,
        batch.tenant_id,
        after={"imported_count": imported, "updated_count": updated, "skipped_count": skipped},
    )
    db.commit()
    return ImportCustomersResponse(imported_count=imported, updated_count=updated, skipped_count=skipped, batch_id=batch.id)
