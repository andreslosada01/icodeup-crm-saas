from __future__ import annotations

import argparse
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models import BusinessRule, Customer, CustomerObligation, Project, Tenant
from app.services.contact_compliance import CONTACT_RULE_MODULE, CONTACT_RULE_TYPE


SEED_MARKER = "iep_contact_compliance_demo_seed"
DEFAULT_TENANT_SLUG = "andina-servicios-financieros"


def _tenant_scope(db: Session, tenant_slug: str | None) -> list[Tenant]:
    slug = tenant_slug or DEFAULT_TENANT_SLUG
    if slug == "*":
        return list(db.scalars(select(Tenant).where(Tenant.slug != settings.platform_tenant_slug).order_by(Tenant.name)))
    exact = db.scalar(select(Tenant).where(Tenant.slug == slug))
    if exact:
        return [exact]
    return list(db.scalars(select(Tenant).where(Tenant.slug.like(f"{slug}%")).order_by(Tenant.name)))


def _upsert_rule(
    db: Session,
    tenant: Tenant,
    *,
    code: str,
    name: str,
    description: str,
    condition: dict,
    action: dict,
    severity: str,
    is_active: bool = True,
) -> bool:
    item = db.scalar(
        select(BusinessRule).where(
            BusinessRule.tenant_id == tenant.id,
            BusinessRule.module == CONTACT_RULE_MODULE,
            BusinessRule.rule_type == CONTACT_RULE_TYPE,
            BusinessRule.code == code,
        )
    )
    created = item is None
    if item is None:
        item = BusinessRule(tenant_id=tenant.id, module=CONTACT_RULE_MODULE, rule_type=CONTACT_RULE_TYPE, code=code, name=name)
        db.add(item)
    item.name = name
    item.description = description
    item.condition_json = json.dumps({**condition, "seed": SEED_MARKER}, ensure_ascii=True)
    item.action_json = json.dumps({**action, "seed": SEED_MARKER}, ensure_ascii=True)
    item.severity = severity
    item.is_active = is_active
    return created


def _definitions(db: Session, tenant: Tenant) -> list[dict]:
    project = db.scalar(select(Project).where(Project.tenant_id == tenant.id, Project.status == "active").order_by(Project.id).limit(1))
    customer = db.scalar(select(Customer).where(Customer.tenant_id == tenant.id).order_by(Customer.priority.desc(), Customer.id).limit(1))
    obligation = db.scalar(select(CustomerObligation).where(CustomerObligation.tenant_id == tenant.id, CustomerObligation.customer_id == customer.id).order_by(CustomerObligation.id).limit(1)) if customer else None
    all_contact_channels = ["phone", "whatsapp", "email", "sms"]
    return [
        {
            "code": "CONTACT_WINDOW_DEMO",
            "name": "Ventana operativa demo",
            "description": "Regla demo configurable para horarios y dias de contacto.",
            "condition": {
                "project_id": None,
                "channels": all_contact_channels,
                "allowed_days": ["mon", "tue", "wed", "thu", "fri"],
                "start_time": "08:00",
                "end_time": "18:00",
                "priority": 10,
            },
            "action": {"severity": "warning", "recommended_action": "Programar contacto dentro de la ventana configurada.", "priority": 10},
            "severity": "warning",
        },
        {
            "code": "CONTACT_CHANNELS_PROJECT_DEMO",
            "name": "Canales permitidos por cartera demo",
            "description": "Regla demo para permitir canales especificos por cartera.",
            "condition": {
                "project_id": project.id if project else None,
                "channels": ["phone", "whatsapp", "email"],
                "blocked_channels": ["sms"],
                "priority": 20,
            },
            "action": {"severity": "block", "recommended_action": "Usar llamada, WhatsApp o email segun la estrategia de la cartera.", "priority": 20},
            "severity": "block",
        },
        {
            "code": "CONTACT_ATTEMPTS_DEMO",
            "name": "Maximos de intentos demo",
            "description": "Regla demo configurable para frecuencia de intentos por cliente.",
            "condition": {
                "project_id": project.id if project else None,
                "channels": all_contact_channels,
                "max_attempts_per_day": 3,
                "max_attempts_per_week": 10,
                "max_attempts_per_channel_day": 2,
                "priority": 30,
            },
            "action": {"severity": "warning", "recommended_action": "Esperar o usar una siguiente accion programada.", "priority": 30},
            "severity": "warning",
        },
        {
            "code": "CONTACT_CUSTOMER_BLOCK_DEMO",
            "name": "Cliente con restriccion especial demo",
            "description": "Regla demo para validar bloqueo por cliente u obligacion.",
            "condition": {
                "project_id": project.id if project else None,
                "channels": all_contact_channels,
                "blocked_customer_ids": [customer.id] if customer else [],
                "blocked_obligation_ids": [obligation.id] if obligation else [],
                "priority": 5,
            },
            "action": {"severity": "block", "recommended_action": "Escalar a coordinacion antes de contactar este cliente.", "priority": 5},
            "severity": "block",
        },
    ]


def run(tenant_slug: str | None, dry_run: bool) -> dict[str, dict]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurado.")
    results: dict[str, dict] = {}
    with SessionLocal() as db:
        for tenant in _tenant_scope(db, tenant_slug):
            before = len(
                list(
                    db.scalars(
                        select(BusinessRule).where(
                            BusinessRule.tenant_id == tenant.id,
                            BusinessRule.module == CONTACT_RULE_MODULE,
                            BusinessRule.rule_type == CONTACT_RULE_TYPE,
                        )
                    )
                )
            )
            created = 0
            for definition in _definitions(db, tenant):
                if _upsert_rule(db, tenant, **definition):
                    created += 1
            db.flush()
            after = len(
                list(
                    db.scalars(
                        select(BusinessRule).where(
                            BusinessRule.tenant_id == tenant.id,
                            BusinessRule.module == CONTACT_RULE_MODULE,
                            BusinessRule.rule_type == CONTACT_RULE_TYPE,
                        )
                    )
                )
            )
            results[tenant.slug] = {"before": before, "after": after, "created": created}
        if dry_run:
            db.rollback()
        else:
            db.commit()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed seguro TEST para Cumplimiento y contacto.")
    parser.add_argument("--tenant-slug", default=None, help=f"Tenant demo a configurar. Default: {DEFAULT_TENANT_SLUG}. Usa * para tenants no plataforma.")
    parser.add_argument("--dry-run", action="store_true", help="Calcula cambios y hace rollback.")
    parser.add_argument("--confirm-test", action="store_true", help="Requerido para escribir. Evita ejecucion accidental en produccion.")
    args = parser.parse_args()
    if not args.confirm_test and not args.dry_run:
        raise SystemExit("Este seed es solo para TEST. Usa --confirm-test para escribir o --dry-run para inspeccionar.")
    result = run(args.tenant_slug, args.dry_run)
    print(json.dumps({"dry_run": args.dry_run, "seed": SEED_MARKER, "result": result}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
