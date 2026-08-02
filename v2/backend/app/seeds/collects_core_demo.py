from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.db.session import SessionLocal
from app.models import (
    Customer,
    CustomerDemographic,
    CustomerObligation,
    Module,
    PaymentAgreement,
    PaymentAgreementInstallment,
    Project,
    BusinessRule,
    TelephonyExtension,
    TelephonyProvider,
    Tenant,
    TenantModule,
    User,
    UserProjectAssignment,
)


SEED_MARKER = "iep_collects_core_incremental_seed"

SCORING_RULES = [
    ("SCORING_EFFECTIVE_CONTACT", "Scoring - contacto efectivo", {"result_contains_any": ["contactado", "contacto efectivo", "negociacion"], "channel_any": ["phone", "whatsapp", "email", "manual"]}, {"score": 65}, "medium"),
    ("SCORING_PROMISE_CREATED", "Scoring - promesa creada", {"result_contains_any": ["promesa"]}, {"score": 78}, "high"),
    ("SCORING_PAYMENT_REPORTED", "Scoring - pago reportado", {"result_contains_any": ["pago", "pagado", "normalizado"]}, {"score": 92}, "high"),
    ("SCORING_AGREEMENT_CREATED", "Scoring - acuerdo creado", {"result_contains_any": ["acuerdo"]}, {"score": 86}, "high"),
    ("SCORING_LEGAL_ESCALATION", "Scoring - escalamiento juridico", {"result_contains_any": ["escalado", "juridico"]}, {"score": 48}, "medium"),
    ("SCORING_NO_ANSWER", "Scoring - no contesta", {"result_contains_any": ["no contesta", "sin contacto", "ocupado"]}, {"score": 18}, "low"),
    ("SCORING_WRONG_NUMBER", "Scoring - numero errado", {"result_contains_any": ["numero errado", "telefono errado", "no ubicado"]}, {"score": 8}, "low"),
    ("SCORING_CLIENT_WITHOUT_CONTACT", "Scoring - cliente sin contacto", {"result_contains_any": ["sin contacto"]}, {"score": 12}, "low"),
    ("SCORING_SUPPORT_UPLOADED", "Scoring - soporte cargado", {"note_contains": "soporte"}, {"score": 52}, "medium"),
]


def _count(db: Session, model, tenant_id: int) -> int:
    return db.scalar(select(func.count(model.id)).where(model.tenant_id == tenant_id)) or 0


def _tenant_scope(db: Session, tenant_slug: str | None) -> list[Tenant]:
    query = select(Tenant).where(Tenant.slug != settings.platform_tenant_slug).order_by(Tenant.name)
    if tenant_slug:
        query = query.where(Tenant.slug == tenant_slug)
    return list(db.scalars(query))


def _project_for_customer(db: Session, tenant_id: int, customer: Customer) -> Project | None:
    if customer.project_id:
        return db.get(Project, customer.project_id)
    return db.scalar(select(Project).where(Project.tenant_id == tenant_id).order_by(Project.id).limit(1))


def _users(db: Session, tenant_id: int) -> tuple[User | None, User | None]:
    coordinator = db.scalar(select(User).where(User.tenant_id == tenant_id, User.role == COORDINATOR).order_by(User.id).limit(1))
    agent = db.scalar(select(User).where(User.tenant_id == tenant_id, User.role == AGENT).order_by(User.id).limit(1))
    return coordinator, agent


def _project_role_for_user(user: User) -> str:
    if user.role == TENANT_ADMIN:
        return "admin"
    if user.role == COORDINATOR:
        return "coordinator"
    if user.role == QUALITY_SUPERVISOR:
        return "quality_supervisor"
    if user.role == AGENT:
        return "agent"
    email = (user.email or "").lower()
    if email.startswith("abogado"):
        return "lawyer"
    if email.startswith("comercial"):
        return "sales"
    return "viewer"


def _ensure_project_assignments(db: Session, tenant_id: int) -> dict[str, int]:
    updated = 0
    created = 0
    projects = list(db.scalars(select(Project).where(Project.tenant_id == tenant_id).order_by(Project.id)))
    users = list(db.scalars(select(User).where(User.tenant_id == tenant_id, User.status == "active").order_by(User.id)))
    for project in projects:
        for user in users:
            expected_role = _project_role_for_user(user)
            if expected_role == "viewer":
                continue
            assignment = db.scalar(
                select(UserProjectAssignment).where(
                    UserProjectAssignment.user_id == user.id,
                    UserProjectAssignment.project_id == project.id,
                )
            )
            if assignment is None:
                assignment = UserProjectAssignment(tenant_id=tenant_id, user_id=user.id, project_id=project.id)
                db.add(assignment)
                created += 1
            old_role = assignment.role_in_project
            assignment.tenant_id = tenant_id
            assignment.is_active = True
            assignment.role_in_project = expected_role
            if assignment.role_in_project != old_role:
                updated += 1
    return {"assignments_created": created, "assignments_role_fixed": updated}


def _ensure_scoring_rules(db: Session, tenant_id: int) -> dict[str, int]:
    created = 0
    updated = 0
    for code, name, condition, action, severity in SCORING_RULES:
        rule = db.scalar(
            select(BusinessRule).where(
                BusinessRule.tenant_id == tenant_id,
                BusinessRule.module == "collections",
                BusinessRule.rule_type == "scoring",
                BusinessRule.code == code,
            )
        )
        if rule is None:
            rule = BusinessRule(tenant_id=tenant_id, module="collections", rule_type="scoring", code=code, name=name)
            db.add(rule)
            created += 1
        else:
            updated += 1
        rule.name = name
        rule.condition_json = json.dumps(condition, ensure_ascii=True)
        rule.action_json = json.dumps(action, ensure_ascii=True)
        rule.severity = severity
        rule.is_active = True
    return {"scoring_rules_created": created, "scoring_rules_updated": updated}


def _obligation_number(customer: Customer, index: int) -> str:
    document = "".join(ch for ch in customer.document if ch.isalnum()) or str(customer.id)
    return f"IEP-{document}-{index:02d}"


def _ensure_obligations(db: Session, tenant_id: int, customers: list[Customer]) -> int:
    created = 0
    for customer_index, customer in enumerate(customers, start=1):
        project = _project_for_customer(db, tenant_id, customer)
        _, agent = _users(db, tenant_id)
        base_balance = max(customer.balance or 0, 900000 + (customer_index * 125000))
        for index, product in enumerate(("Credito consumo", "Tarjeta empresarial"), start=1):
            number = _obligation_number(customer, index)
            item = db.scalar(select(CustomerObligation).where(CustomerObligation.tenant_id == tenant_id, CustomerObligation.obligation_number == number))
            if item is None:
                amount = base_balance // 2 if index == 1 else base_balance - (base_balance // 2)
                item = CustomerObligation(tenant_id=tenant_id, customer_id=customer.id, obligation_number=number)
                db.add(item)
                created += 1
            else:
                amount = item.current_balance or base_balance // 2
            item.project_id = project.id if project else customer.project_id
            item.product_type = product
            item.portfolio_name = project.name if project else customer.segment
            item.original_amount = max(item.original_amount or 0, amount + (index * 85000))
            item.current_balance = item.current_balance or amount
            item.days_past_due = item.days_past_due or customer.dpd or (18 * index)
            item.status = item.status or "active"
            item.risk = item.risk or customer.risk or "Medio"
            item.priority = item.priority or max(customer.priority or 0, 70 - (index * 8))
            item.assignment_date = item.assignment_date or datetime.now(timezone.utc) - timedelta(days=12 + index)
            item.due_date = item.due_date or datetime.now(timezone.utc) + timedelta(days=15 * index)
            item.assigned_user_id = item.assigned_user_id or customer.assigned_user_id or (agent.id if agent else None)
            item.metadata_json = json.dumps({"seed": SEED_MARKER, "product_index": index}, ensure_ascii=True)
        db.flush()
        customer.balance = sum(db.scalars(select(CustomerObligation.current_balance).where(CustomerObligation.tenant_id == tenant_id, CustomerObligation.customer_id == customer.id))) or customer.balance
        customer.original_balance = max(customer.original_balance or 0, sum(db.scalars(select(CustomerObligation.original_amount).where(CustomerObligation.tenant_id == tenant_id, CustomerObligation.customer_id == customer.id))) or 0)
    return created


def _ensure_demographics(db: Session, tenant_id: int, customers: list[Customer]) -> int:
    created = 0
    for index, customer in enumerate(customers, start=1):
        source = "iep-core-demo"
        phone = customer.phone or f"300555{index:04d}"
        item = db.scalar(
            select(CustomerDemographic).where(
                CustomerDemographic.tenant_id == tenant_id,
                CustomerDemographic.customer_id == customer.id,
                CustomerDemographic.source == source,
                CustomerDemographic.phone == phone,
            )
        )
        if item is None:
            item = CustomerDemographic(tenant_id=tenant_id, customer_id=customer.id, source=source, phone=phone)
            db.add(item)
            created += 1
        item.email = item.email or customer.email or f"cliente{customer.id}@demo-clientes.local"
        item.address = item.address or f"Calle {20 + index} # {10 + index}-30"
        item.city = item.city or customer.city or "Bogota"
        item.state = item.state or "Demo"
        item.score = max(item.score or 0, 78 - index)
        item.contactability = item.contactability or customer.contactability or "Media"
        item.priority = item.priority or max(customer.priority or 0, 50)
        item.valid_from = item.valid_from or date.today()
        item.valid_until = item.valid_until or date.today() + timedelta(days=180)
        item.metadata_json = json.dumps({"seed": SEED_MARKER, "verified": False, "source_type": "test_demo"}, ensure_ascii=True)
    return created


def _ensure_agreements(db: Session, tenant_id: int, customers: list[Customer], max_agreements: int) -> int:
    created = 0
    _, agent = _users(db, tenant_id)
    if agent is None:
        return created
    for customer in customers[:max_agreements]:
        obligation = db.scalar(select(CustomerObligation).where(CustomerObligation.tenant_id == tenant_id, CustomerObligation.customer_id == customer.id).order_by(CustomerObligation.priority.desc()).limit(1))
        existing = db.scalar(select(PaymentAgreement).where(PaymentAgreement.tenant_id == tenant_id, PaymentAgreement.customer_id == customer.id, PaymentAgreement.notes.contains(SEED_MARKER)).limit(1))
        if existing or obligation is None:
            continue
        total_amount = max(90000, min(obligation.current_balance, 360000))
        agreement = PaymentAgreement(
            tenant_id=tenant_id,
            project_id=obligation.project_id or customer.project_id,
            customer_id=customer.id,
            obligation_id=obligation.id,
            user_id=customer.assigned_user_id or agent.id,
            total_amount=total_amount,
            installment_count=3,
            start_date=datetime.now(timezone.utc) + timedelta(days=7),
            status="active",
            notes=f"Seed incremental TEST {SEED_MARKER}",
        )
        db.add(agreement)
        db.flush()
        base = total_amount // agreement.installment_count
        remainder = total_amount % agreement.installment_count
        for index in range(agreement.installment_count):
            db.add(
                PaymentAgreementInstallment(
                    agreement_id=agreement.id,
                    due_date=agreement.start_date + timedelta(days=30 * index),
                    amount=base + (1 if index < remainder else 0),
                )
            )
        created += 1
    return created


def _config_dict(raw_config: str | None) -> dict:
    if not raw_config:
        return {}
    try:
        data = json.loads(raw_config)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _telephony_module_active_count(db: Session, tenant_id: int) -> int:
    return db.scalar(
        select(func.count(TenantModule.id)).where(
            TenantModule.tenant_id == tenant_id,
            TenantModule.module_code == "telephony",
            TenantModule.enabled.is_(True),
            TenantModule.is_enabled.is_(True),
        )
    ) or 0


def _ensure_telephony_module(db: Session, tenant_id: int) -> dict[str, int]:
    module = db.scalar(select(Module).where(Module.code == "telephony"))
    if module is None:
        return {"telephony_module_created": 0, "telephony_module_activated": 0, "telephony_module_missing": 1}
    tenant_module = db.scalar(
        select(TenantModule).where(
            TenantModule.tenant_id == tenant_id,
            TenantModule.module_code == "telephony",
        )
    )
    created = 0
    was_active = bool(tenant_module and tenant_module.enabled and tenant_module.is_enabled)
    if tenant_module is None:
        tenant_module = TenantModule(tenant_id=tenant_id, module_code="telephony")
        db.add(tenant_module)
        created = 1
    tenant_module.module_id = module.id
    tenant_module.enabled = True
    tenant_module.is_enabled = True
    if tenant_module.enabled_at is None:
        tenant_module.enabled_at = datetime.now(timezone.utc)
    config = _config_dict(tenant_module.configuration_json)
    config.update({"demo": True, "mode": "simulated", "seed": SEED_MARKER, "provider": "IpCom Demo TEST"})
    tenant_module.configuration_json = json.dumps(config, ensure_ascii=True)
    return {
        "telephony_module_created": created,
        "telephony_module_activated": 0 if was_active else 1,
        "telephony_module_missing": 0,
    }


def _ensure_telephony(db: Session, tenant_id: int) -> dict[str, int]:
    module_result = _ensure_telephony_module(db, tenant_id)
    coordinator, agent = _users(db, tenant_id)
    provider = db.scalar(select(TelephonyProvider).where(TelephonyProvider.tenant_id == tenant_id, TelephonyProvider.name == "IpCom Demo TEST"))
    provider_created = 0
    if provider is None:
        provider = TelephonyProvider(tenant_id=tenant_id, name="IpCom Demo TEST")
        db.add(provider)
        provider_created = 1
    provider.provider_type = "sip_trunk"
    provider.host = provider.host or "pbx.demo.local"
    provider.port = provider.port or 5060
    provider.is_active = True
    provider.config_json = json.dumps({"mode": "simulated", "seed": SEED_MARKER, "outbound_enabled": True, "real_credentials": False, "external_prefix": "0218739#", "mobile_prepend": "000157", "mobile_match_pattern": "3XXXXXXXXX"}, ensure_ascii=True)
    db.flush()

    extensions_created = 0
    for user, number in ((coordinator, "1001"), (agent, "1002")):
        if user is None:
            continue
        extension = db.scalar(select(TelephonyExtension).where(TelephonyExtension.tenant_id == tenant_id, TelephonyExtension.extension_number == number))
        if extension is None:
            extension = TelephonyExtension(tenant_id=tenant_id, user_id=user.id, extension_number=number)
            db.add(extension)
            extensions_created += 1
        extension.user_id = user.id
        extension.provider_id = provider.id
        extension.display_name = f"{user.name} - Extension {number}"
        extension.sip_username = number
        extension.sip_domain = "pbx.demo.local"
        extension.status = "available"
        extension.is_active = True
        extension.metadata_json = json.dumps({"mode": "simulated", "seed": SEED_MARKER, "real_credentials": False}, ensure_ascii=True)
    return {**module_result, "providers_created": provider_created, "extensions_created": extensions_created}


def run(tenant_slug: str | None, limit_customers: int, dry_run: bool) -> dict[str, dict[str, int]]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurado.")
    results: dict[str, dict[str, int]] = {}
    with SessionLocal() as db:
        tenants = _tenant_scope(db, tenant_slug)
        for tenant in tenants:
            customers = list(db.scalars(select(Customer).where(Customer.tenant_id == tenant.id).order_by(Customer.id).limit(limit_customers)))
            before = {
                "customers": len(customers),
                "obligations": _count(db, CustomerObligation, tenant.id),
                "demographics": _count(db, CustomerDemographic, tenant.id),
                "agreements": _count(db, PaymentAgreement, tenant.id),
                "telephony_modules_active": _telephony_module_active_count(db, tenant.id),
                "telephony_providers": _count(db, TelephonyProvider, tenant.id),
                "telephony_extensions": _count(db, TelephonyExtension, tenant.id),
                "project_assignments": db.scalar(select(func.count(UserProjectAssignment.id)).where(UserProjectAssignment.tenant_id == tenant.id)) or 0,
                "scoring_rules": db.scalar(select(func.count(BusinessRule.id)).where(BusinessRule.tenant_id == tenant.id, BusinessRule.module == "collections", BusinessRule.rule_type == "scoring")) or 0,
            }
            created_obligations = _ensure_obligations(db, tenant.id, customers)
            created_demographics = _ensure_demographics(db, tenant.id, customers)
            created_agreements = _ensure_agreements(db, tenant.id, customers, max_agreements=min(5, len(customers)))
            assignments = _ensure_project_assignments(db, tenant.id)
            scoring = _ensure_scoring_rules(db, tenant.id)
            telephony = _ensure_telephony(db, tenant.id)
            after = {
                "customers": len(customers),
                "obligations": before["obligations"] + created_obligations,
                "demographics": before["demographics"] + created_demographics,
                "agreements": before["agreements"] + created_agreements,
                "telephony_modules_active": _telephony_module_active_count(db, tenant.id),
                "telephony_providers": before["telephony_providers"] + telephony["providers_created"],
                "telephony_extensions": before["telephony_extensions"] + telephony["extensions_created"],
                "project_assignments": db.scalar(select(func.count(UserProjectAssignment.id)).where(UserProjectAssignment.tenant_id == tenant.id)) or 0,
                "scoring_rules": db.scalar(select(func.count(BusinessRule.id)).where(BusinessRule.tenant_id == tenant.id, BusinessRule.module == "collections", BusinessRule.rule_type == "scoring")) or 0,
            }
            results[tenant.slug] = {"before": before, "after": after, "created": {"obligations": created_obligations, "demographics": created_demographics, "agreements": created_agreements, **assignments, **scoring, **telephony}}
        if dry_run:
            db.rollback()
        else:
            db.commit()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed incremental seguro para completar data demo de Collects 360 en TEST.")
    parser.add_argument("--tenant-slug", default=None, help="Slug de tenant demo a completar. Si se omite, aplica a tenants de negocio.")
    parser.add_argument("--limit-customers", type=int, default=10, help="Clientes por tenant a enriquecer.")
    parser.add_argument("--dry-run", action="store_true", help="Calcula cambios y hace rollback.")
    parser.add_argument("--confirm-test", action="store_true", help="Requerido para escribir. Evita ejecucion accidental en produccion.")
    args = parser.parse_args()
    if not args.confirm_test and not args.dry_run:
        raise SystemExit("Este seed es solo para TEST. Usa --confirm-test para escribir o --dry-run para inspeccionar.")
    result = run(args.tenant_slug, max(1, args.limit_customers), args.dry_run)
    print(json.dumps({"dry_run": args.dry_run, "seed": SEED_MARKER, "result": result}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
