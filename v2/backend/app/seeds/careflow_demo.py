from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, TENANT_ADMIN
from app.db.session import SessionLocal
from app.models import CareCase, CareCaseCategory, CareCaseEvent, Customer, Module, Project, Tenant, TenantModule, User


SEED_MARKER = "iep_careflow_360_demo_seed"
DEFAULT_TENANT_SLUG = "andina-servicios-financieros"


def _count(db: Session, model, tenant_id: int) -> int:
    return db.scalar(select(func.count(model.id)).where(model.tenant_id == tenant_id)) or 0


def _tenant_scope(db: Session, tenant_slug: str | None) -> list[Tenant]:
    slug = tenant_slug or DEFAULT_TENANT_SLUG
    query = select(Tenant).where(Tenant.slug == slug)
    if slug == "*":
        query = select(Tenant).where(Tenant.slug != settings.platform_tenant_slug).order_by(Tenant.name)
    return list(db.scalars(query))


def _ensure_module(db: Session) -> Module:
    module = db.scalar(select(Module).where(Module.code == "careflow"))
    if module is None:
        module = Module(code="careflow", name="CareFlow 360")
        db.add(module)
        db.flush()
    module.name = "CareFlow 360"
    module.description = "Atencion al cliente, casos, solicitudes, SLA y seguimiento."
    module.category = "business"
    module.icon = "life-buoy"
    module.order = 68
    module.is_active = True
    return module


def _activate_module(db: Session, tenant: Tenant, module: Module) -> bool:
    tenant_module = db.scalar(select(TenantModule).where(TenantModule.tenant_id == tenant.id, TenantModule.module_code == "careflow"))
    created = tenant_module is None
    if tenant_module is None:
        tenant_module = TenantModule(tenant_id=tenant.id, module_code="careflow")
        db.add(tenant_module)
    tenant_module.module_id = module.id
    tenant_module.enabled = True
    tenant_module.is_enabled = True
    if tenant_module.enabled_at is None:
        tenant_module.enabled_at = datetime.now(timezone.utc)
    tenant_module.configuration_json = json.dumps({"demo": True, "mode": "simulated", "seed": SEED_MARKER}, ensure_ascii=True)
    return created


def _ensure_categories(db: Session, tenant: Tenant) -> int:
    created = 0
    definitions = [
        ("PQRS", "Peticiones, quejas, reclamos y solicitudes.", "alta", 24),
        ("Soporte operativo", "Consultas sobre pagos, documentos, estados y procesos.", "media", 48),
        ("Canales digitales", "Solicitudes recibidas por WhatsApp, web, email o chatbot.", "media", 36),
        ("Caso critico", "Atencion prioritaria con riesgo reputacional o vencimiento cercano.", "critica", 8),
    ]
    for name, description, priority, sla_hours in definitions:
        item = db.scalar(select(CareCaseCategory).where(CareCaseCategory.tenant_id == tenant.id, CareCaseCategory.name == name))
        if item is None:
            item = CareCaseCategory(tenant_id=tenant.id, name=name)
            db.add(item)
            created += 1
        item.description = description
        item.default_priority = priority
        item.default_sla_hours = sla_hours
        item.is_active = True
    return created


def _first_user(db: Session, tenant: Tenant, role: str) -> User | None:
    return db.scalar(select(User).where(User.tenant_id == tenant.id, User.role == role, User.status == "active").order_by(User.id).limit(1))


def _case_seed_data(db: Session, tenant: Tenant) -> list[dict]:
    now = datetime.now(timezone.utc)
    project = db.scalar(select(Project).where(Project.tenant_id == tenant.id, Project.status == "active").order_by(Project.id).limit(1))
    customers = list(db.scalars(select(Customer).where(Customer.tenant_id == tenant.id).order_by(Customer.id).limit(4)))
    admin = _first_user(db, tenant, TENANT_ADMIN) or db.scalar(select(User).where(User.tenant_id == tenant.id).order_by(User.id).limit(1))
    coordinator = _first_user(db, tenant, COORDINATOR) or admin
    agent = _first_user(db, tenant, AGENT) or coordinator or admin
    return [
        {
            "case_number": "CF-DEMO-001",
            "title": "Cliente solicita soporte sobre estado de pago",
            "description": "Caso demo para seguimiento de soporte operacional con SLA corto.",
            "channel": "whatsapp",
            "case_type": "soporte",
            "category": "Soporte operativo",
            "priority": "alta",
            "status": "en_proceso",
            "assigned_user_id": agent.id if agent else None,
            "created_by_id": admin.id if admin else agent.id,
            "project_id": project.id if project else None,
            "customer_id": customers[0].id if customers else None,
            "due_at": now + timedelta(hours=18),
        },
        {
            "case_number": "CF-DEMO-002",
            "title": "PQRS pendiente por validacion interna",
            "description": "Caso demo critico para tablero de prioridades y supervision.",
            "channel": "email",
            "case_type": "pqrs",
            "category": "PQRS",
            "priority": "critica",
            "status": "pendiente_interno",
            "assigned_user_id": coordinator.id if coordinator else agent.id if agent else None,
            "created_by_id": admin.id if admin else coordinator.id,
            "project_id": project.id if project else None,
            "customer_id": customers[1].id if len(customers) > 1 else None,
            "due_at": now - timedelta(hours=4),
        },
        {
            "case_number": "CF-DEMO-003",
            "title": "Solicitud web sin responsable asignado",
            "description": "Caso demo para validar gobierno operativo y asignacion.",
            "channel": "web",
            "case_type": "solicitud",
            "category": "Canales digitales",
            "priority": "media",
            "status": "nuevo",
            "assigned_user_id": None,
            "created_by_id": admin.id if admin else agent.id,
            "project_id": project.id if project else None,
            "customer_id": customers[2].id if len(customers) > 2 else None,
            "due_at": now + timedelta(days=2),
        },
        {
            "case_number": "CF-DEMO-004",
            "title": "Caso resuelto de referencia mensual",
            "description": "Caso demo cerrado para reportes del mes.",
            "channel": "llamada",
            "case_type": "consulta",
            "category": "Soporte operativo",
            "priority": "baja",
            "status": "cerrado",
            "assigned_user_id": agent.id if agent else None,
            "created_by_id": admin.id if admin else agent.id,
            "closed_by_id": agent.id if agent else admin.id if admin else None,
            "project_id": project.id if project else None,
            "customer_id": customers[3].id if len(customers) > 3 else None,
            "due_at": now - timedelta(days=1),
            "closed_at": now - timedelta(hours=2),
            "resolved_at": now - timedelta(hours=2),
        },
    ]


def _sla_status(status_value: str, due_at: datetime | None) -> str:
    if status_value in {"resuelto", "cerrado", "cancelado"} or due_at is None:
        return "en_tiempo"
    now = datetime.now(timezone.utc)
    if due_at < now:
        return "vencido"
    if due_at <= now + timedelta(hours=24):
        return "proximo_a_vencer"
    return "en_tiempo"


def _ensure_cases(db: Session, tenant: Tenant) -> dict[str, int]:
    created = 0
    events_created = 0
    for data in _case_seed_data(db, tenant):
        item = db.scalar(select(CareCase).where(CareCase.tenant_id == tenant.id, CareCase.case_number == data["case_number"]))
        if item is None:
            item = CareCase(tenant_id=tenant.id, case_number=data["case_number"], title=data["title"], created_by_id=data["created_by_id"])
            db.add(item)
            db.flush()
            created += 1
        for field, value in data.items():
            setattr(item, field, value)
        item.tenant_id = tenant.id
        item.sla_status = _sla_status(item.status, item.due_at)
        item.metadata_json = json.dumps({"demo": True, "seed": SEED_MARKER}, ensure_ascii=True)
        event = db.scalar(select(CareCaseEvent).where(CareCaseEvent.case_id == item.id, CareCaseEvent.event_type == "nota", CareCaseEvent.description == "Evento demo CareFlow 360."))
        if event is None:
            event = CareCaseEvent(
                tenant_id=tenant.id,
                case_id=item.id,
                event_type="nota",
                description="Evento demo CareFlow 360.",
                created_by_id=item.created_by_id,
                metadata_json=json.dumps({"demo": True, "seed": SEED_MARKER}, ensure_ascii=True),
            )
            db.add(event)
            events_created += 1
    db.flush()
    return {"cases_created": created, "events_created": events_created}


def run(tenant_slug: str | None, dry_run: bool) -> dict[str, dict]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurado.")
    results: dict[str, dict] = {}
    with SessionLocal() as db:
        module = _ensure_module(db)
        for tenant in _tenant_scope(db, tenant_slug):
            before = {
                "careflow_modules": db.scalar(select(func.count(TenantModule.id)).where(TenantModule.tenant_id == tenant.id, TenantModule.module_code == "careflow")) or 0,
                "categories": _count(db, CareCaseCategory, tenant.id),
                "cases": _count(db, CareCase, tenant.id),
                "events": _count(db, CareCaseEvent, tenant.id),
            }
            module_created = _activate_module(db, tenant, module)
            categories_created = _ensure_categories(db, tenant)
            cases = _ensure_cases(db, tenant)
            after = {
                "careflow_modules": db.scalar(select(func.count(TenantModule.id)).where(TenantModule.tenant_id == tenant.id, TenantModule.module_code == "careflow")) or 0,
                "categories": _count(db, CareCaseCategory, tenant.id),
                "cases": _count(db, CareCase, tenant.id),
                "events": _count(db, CareCaseEvent, tenant.id),
            }
            results[tenant.slug] = {
                "before": before,
                "after": after,
                "created": {"module_activation_created": int(module_created), "categories_created": categories_created, **cases},
            }
        if dry_run:
            db.rollback()
        else:
            db.commit()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed seguro TEST para CareFlow 360.")
    parser.add_argument("--tenant-slug", default=None, help=f"Tenant demo a activar. Default: {DEFAULT_TENANT_SLUG}. Usa * para todos los tenants no plataforma.")
    parser.add_argument("--dry-run", action="store_true", help="Calcula cambios y hace rollback.")
    parser.add_argument("--confirm-test", action="store_true", help="Requerido para escribir. Evita ejecucion accidental en produccion.")
    args = parser.parse_args()
    if not args.confirm_test and not args.dry_run:
        raise SystemExit("Este seed es solo para TEST. Usa --confirm-test para escribir o --dry-run para inspeccionar.")
    result = run(args.tenant_slug, args.dry_run)
    print(json.dumps({"dry_run": args.dry_run, "seed": SEED_MARKER, "result": result}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
