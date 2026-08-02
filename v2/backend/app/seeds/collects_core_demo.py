from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR
from app.db.session import SessionLocal
from app.models import (
    Customer,
    CustomerDemographic,
    CustomerObligation,
    PaymentAgreement,
    PaymentAgreementInstallment,
    Project,
    TelephonyExtension,
    TelephonyProvider,
    Tenant,
    User,
)


SEED_MARKER = "iep_collects_core_incremental_seed"


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


def _ensure_telephony(db: Session, tenant_id: int) -> dict[str, int]:
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
    return {"providers_created": provider_created, "extensions_created": extensions_created}


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
                "telephony_providers": _count(db, TelephonyProvider, tenant.id),
                "telephony_extensions": _count(db, TelephonyExtension, tenant.id),
            }
            created_obligations = _ensure_obligations(db, tenant.id, customers)
            created_demographics = _ensure_demographics(db, tenant.id, customers)
            created_agreements = _ensure_agreements(db, tenant.id, customers, max_agreements=min(5, len(customers)))
            telephony = _ensure_telephony(db, tenant.id)
            after = {
                "customers": len(customers),
                "obligations": before["obligations"] + created_obligations,
                "demographics": before["demographics"] + created_demographics,
                "agreements": before["agreements"] + created_agreements,
                "telephony_providers": before["telephony_providers"] + telephony["providers_created"],
                "telephony_extensions": before["telephony_extensions"] + telephony["extensions_created"],
            }
            results[tenant.slug] = {"before": before, "after": after, "created": {"obligations": created_obligations, "demographics": created_demographics, "agreements": created_agreements, **telephony}}
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
