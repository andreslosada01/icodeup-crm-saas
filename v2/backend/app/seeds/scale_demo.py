from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import COORDINATOR, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.core.security import hash_password
from app.db.session import SessionLocal, init_database
from app.models import (
    CommunicationChannel,
    Customer,
    ManagementActivity,
    Payment,
    PaymentPromise,
    Project,
    Tenant,
    TypificationNode,
    User,
    UserProjectAssignment,
)


AGENT = "agent"
DEFAULT_PASSWORD = "Temporal123!"


@dataclass(frozen=True)
class DemoTenant:
    name: str
    slug: str
    tax_id: str
    projects: tuple[tuple[str, str, str], ...]


DEMO_TENANTS = (
    DemoTenant(
        name="Andina Servicios Integrales",
        slug="andina-servicios",
        tax_id="NIT 900888101",
        projects=(
            ("Banco Ferias", "BANCO-FERIAS", "Cartera financiera temprana y castigada."),
            ("Servicios Montero", "SERV-MONTERO", "Cartera comercial de servicios recurrentes."),
            ("Finanzas Losada", "FIN-LOSADA", "Normalizacion de obligaciones consumo y pyme."),
        ),
    ),
    DemoTenant(
        name="Inversiones Horizonte SAS",
        slug="inversiones-horizonte",
        tax_id="NIT 901277450",
        projects=(
            ("Cartera Retail Norte", "RETAIL-NORTE", "Clientes retail con mora mixta."),
            ("Creditos Pyme Capital", "PYME-CAPITAL", "Financiacion pyme con promesas activas."),
            ("Recuperacion Vehicular", "REC-VEHICULAR", "Obligaciones de financiacion vehicular."),
        ),
    ),
    DemoTenant(
        name="Grupo Atlas Financiero",
        slug="grupo-atlas-financiero",
        tax_id="NIT 901944003",
        projects=(
            ("Tarjeta Premium", "TARJETA-PREMIUM", "Cartera tarjeta con alto volumen transaccional."),
            ("Microcredito Productivo", "MICRO-PROD", "Microcredito productivo por zonas."),
            ("Hipotecario Preventivo", "HIPO-PREVENTIVO", "Cartera hipotecaria preventiva."),
        ),
    ),
)

FALLBACK_PROJECTS = (
    ("Cartera Consumo Demo", "CONSUMO-DEMO", "Cartera demo para pruebas de consumo."),
    ("Cartera Pyme Demo", "PYME-DEMO", "Cartera demo para pruebas pyme."),
)

CITIES = ("Bogota", "Medellin", "Cali", "Barranquilla", "Bucaramanga", "Pereira", "Cartagena", "Manizales")
SEGMENTS = ("Consumo", "Pyme", "Tarjeta", "Vehiculo", "Hipotecario", "Microcredito")
FIRST_NAMES = (
    "Ana",
    "Carlos",
    "Mariana",
    "Julian",
    "Laura",
    "Andres",
    "Paola",
    "Santiago",
    "Camila",
    "Diego",
    "Natalia",
    "Felipe",
)
LAST_NAMES = (
    "Herrera",
    "Torres",
    "Martinez",
    "Gomez",
    "Rincon",
    "Castro",
    "Morales",
    "Vargas",
    "Suarez",
    "Ortega",
    "Pardo",
    "Lozada",
)
STATUSES = ("Sin contacto", "Contactado", "Promesa", "Escalado", "Disputa", "Pago parcial")
CHANNELS = ("phone", "whatsapp", "email", "manual")


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("/", "-")
        .replace(".", "")
    )


def compact(value: str) -> str:
    return "".join(char.lower() for char in value if char.isalnum())


def risk_from_dpd(dpd: int, balance: int) -> str:
    if dpd >= 60 or balance >= 20_000_000:
        return "Alto"
    if dpd >= 15 or balance >= 5_000_000:
        return "Medio"
    return "Bajo"


def priority_score(dpd: int, balance: int, risk: str, status: str) -> int:
    risk_score = {"Alto": 30, "Medio": 18, "Bajo": 8}.get(risk, 12)
    status_score = {"Promesa": 12, "Sin contacto": 10, "Escalado": 14, "Disputa": 12}.get(status, 5)
    return min(100, risk_score + min(35, round(dpd / 3)) + min(25, round(balance / 2_000_000)) + status_score)


def next_action_for(status: str, risk: str) -> str:
    if status == "Promesa":
        return "Confirmar cumplimiento de promesa"
    if status == "Escalado":
        return "Seguimiento lider y ruta especializada"
    if status == "Disputa":
        return "Solicitar soporte documental y congelar automatizaciones"
    if risk == "Alto":
        return "Contacto prioritario y alternativa de normalizacion"
    return "Programar nueva gestion"


def get_or_create_tenant(db: Session, demo: DemoTenant) -> Tenant:
    tenant = db.scalar(select(Tenant).where(Tenant.slug == demo.slug))
    if tenant:
        return tenant
    tenant = Tenant(
        name=demo.name,
        slug=demo.slug,
        tax_id=demo.tax_id,
        notes="Tenant demo generado para pruebas de IcodeUp CRM V2.",
    )
    db.add(tenant)
    db.flush()
    return tenant


def get_or_create_project(db: Session, tenant: Tenant, name: str, code: str, description: str) -> Project:
    project = db.scalar(select(Project).where(Project.tenant_id == tenant.id, Project.code == code))
    if project:
        return project
    project = Project(tenant_id=tenant.id, name=name, code=code, description=description, status="active")
    db.add(project)
    db.flush()
    return project


def get_or_create_user(
    db: Session,
    tenant: Tenant,
    email: str,
    name: str,
    role: str,
    title: str,
    leader_id: int | None = None,
) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user:
        changed = False
        if user.leader_id != leader_id:
            user.leader_id = leader_id
            changed = True
        if user.title != title:
            user.title = title
            changed = True
        if changed:
            db.flush()
        return user
    user = User(
        tenant_id=tenant.id,
        name=name,
        email=email,
        role=role,
        phone=f"+57 300 {random.randint(100, 999)} {random.randint(1000, 9999)}",
        title=title,
        leader_id=leader_id,
        password_hash=hash_password(DEFAULT_PASSWORD),
        status="active",
    )
    db.add(user)
    db.flush()
    return user


def ensure_assignment(db: Session, user: User, project: Project) -> None:
    exists = db.scalar(
        select(UserProjectAssignment).where(
            UserProjectAssignment.user_id == user.id,
            UserProjectAssignment.project_id == project.id,
        )
    )
    if not exists:
        db.add(UserProjectAssignment(user_id=user.id, project_id=project.id))


def ensure_channels(db: Session, tenant: Tenant) -> int:
    created = 0
    channel_specs = (
        ("whatsapp", "Linea WhatsApp principal", "+57 300 555 0101", "Meta Cloud API"),
        ("email", "Correo cobranzas", f"cobranzas@{tenant.slug}.demo", "SMTP corporativo"),
        ("telephony", "Telefonia WebRTC", f"sip:{tenant.slug}@pbx.demo", "PBX WebRTC"),
    )
    for kind, label, value, provider in channel_specs:
        exists = db.scalar(
            select(CommunicationChannel).where(
                CommunicationChannel.tenant_id == tenant.id,
                CommunicationChannel.kind == kind,
                CommunicationChannel.label == label,
            )
        )
        if exists:
            continue
        db.add(
            CommunicationChannel(
                tenant_id=tenant.id,
                kind=kind,
                label=label,
                value=value,
                provider=provider,
                is_default=True,
                status="active",
            )
        )
        created += 1
    return created


def ensure_typifications(db: Session, tenant: Tenant) -> int:
    created = 0
    specs = (
        ("Contacto efectivo", "CONTACTO", "Contactado", False, False, "phone", None),
        ("Promesa de pago", "PROMESA", "Promesa", True, False, "whatsapp", "CONTACTO"),
        ("Pago reportado", "PAGO", "Pago parcial", False, True, "manual", "CONTACTO"),
        ("No contesta", "NO_CONTESTA", "Sin contacto", False, False, "phone", None),
        ("Escalar a lider", "ESCALAR", "Escalado", False, False, "manual", None),
        ("Disputa documental", "DISPUTA", "Disputa", False, False, "email", None),
    )
    code_map: dict[str, TypificationNode] = {
        item.code: item for item in db.scalars(select(TypificationNode).where(TypificationNode.tenant_id == tenant.id))
    }
    for order, (label, code, next_status, requires_promise, requires_payment, channel, parent_code) in enumerate(specs, start=1):
        if code in code_map:
            continue
        parent = code_map.get(parent_code or "")
        node = TypificationNode(
            tenant_id=tenant.id,
            parent_id=parent.id if parent else None,
            label=label,
            code=code,
            next_status=next_status,
            requires_promise=requires_promise,
            requires_payment=requires_payment,
            channel=channel,
            sort_order=order,
        )
        db.add(node)
        db.flush()
        code_map[code] = node
        created += 1
    return created


def ensure_project_staff(db: Session, tenant: Tenant, project: Project) -> tuple[list[User], int]:
    tenant_key = compact(tenant.slug)
    project_key = compact(project.code)
    created_or_existing: list[User] = []
    assignment_count = 0

    tenant_admin = get_or_create_user(
        db,
        tenant,
        f"admin.{tenant_key}@demo.icodeup.local",
        f"Administrador {tenant.name}",
        TENANT_ADMIN,
        "Administrador tenant",
    )
    ensure_assignment(db, tenant_admin, project)
    assignment_count += 1

    coordinator = get_or_create_user(
        db,
        tenant,
        f"coord.{tenant_key}.{project_key}@demo.icodeup.local",
        f"Coordinador {project.name}",
        COORDINATOR,
        "Coordinador de cartera",
    )
    ensure_assignment(db, coordinator, project)
    assignment_count += 1

    supervisor = get_or_create_user(
        db,
        tenant,
        f"calidad.{tenant_key}.{project_key}@demo.icodeup.local",
        f"Supervisor Calidad {project.name}",
        QUALITY_SUPERVISOR,
        "Supervisor de calidad",
        leader_id=coordinator.id,
    )
    ensure_assignment(db, supervisor, project)
    assignment_count += 1

    for index in range(1, 5):
        agent = get_or_create_user(
            db,
            tenant,
            f"agente{index}.{tenant_key}.{project_key}@demo.icodeup.local",
            f"Agente {index} {project.name}",
            AGENT,
            "Gestor de cobranzas",
            leader_id=coordinator.id,
        )
        ensure_assignment(db, agent, project)
        created_or_existing.append(agent)
        assignment_count += 1
    return created_or_existing, assignment_count


def customer_name(rng: random.Random, index: int) -> str:
    if index % 11 == 0:
        return f"{rng.choice(('Comercial', 'Servicios', 'Distribuciones', 'Alimentos'))} {rng.choice(LAST_NAMES)} SAS"
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def create_activity_package(db: Session, customer: Customer, user: User, rng: random.Random, now: datetime) -> tuple[int, int, int]:
    activities = promises = payments = 0
    if customer.status == "Sin contacto":
        return activities, promises, payments

    activity_count = rng.randint(1, 3)
    for activity_index in range(activity_count):
        created_at = now - timedelta(days=rng.randint(1, 35), hours=rng.randint(1, 12))
        result = customer.status if activity_index == activity_count - 1 else rng.choice(("Contactado", "Sin contacto", "Gestion registrada"))
        db.add(
            ManagementActivity(
                tenant_id=customer.tenant_id,
                project_id=customer.project_id,
                customer_id=customer.id,
                user_id=user.id,
                channel=rng.choice(CHANNELS),
                result=result,
                note=f"Gestion demo {activity_index + 1}: objecion, acuerdo o seguimiento registrado.",
                next_contact_at=customer.next_contact_at,
                created_at=created_at,
            )
        )
        activities += 1

    if customer.status == "Promesa" or rng.random() < 0.18:
        amount = max(80_000, round(customer.balance * rng.uniform(0.08, 0.38)))
        due_date = now + timedelta(days=rng.randint(-6, 18))
        db.add(
            PaymentPromise(
                tenant_id=customer.tenant_id,
                project_id=customer.project_id,
                customer_id=customer.id,
                user_id=user.id,
                amount=amount,
                due_date=due_date,
                channel=rng.choice(("phone", "whatsapp", "email")),
                status="Vigente" if due_date >= now else "Vencida",
            )
        )
        promises += 1

    if customer.status == "Pago parcial" or rng.random() < 0.12:
        amount = max(50_000, round(customer.original_balance * rng.uniform(0.05, 0.22)))
        amount = min(amount, customer.balance)
        if amount:
            customer.balance = max(0, customer.balance - amount)
            db.add(
                Payment(
                    tenant_id=customer.tenant_id,
                    project_id=customer.project_id,
                    customer_id=customer.id,
                    user_id=user.id,
                    amount=amount,
                    paid_at=now - timedelta(days=rng.randint(0, 28)),
                    method=rng.choice(("Transferencia", "PSE", "Consignacion", "Pago en linea")),
                    reference=f"DEMO-{customer.id}-{rng.randint(1000, 9999)}",
                )
            )
            payments += 1

    return activities, promises, payments


def seed_customers(db: Session, tenant: Tenant, project: Project, agents: list[User], customers_per_project: int, seed: int) -> dict[str, int]:
    rng = random.Random(seed + project.id)
    now = datetime.now(timezone.utc)
    created = activities = promises = payments = 0
    project_key = compact(project.code)[:18]
    existing_docs = {
        document
        for (document,) in db.execute(
            select(Customer.document).where(Customer.tenant_id == tenant.id, Customer.project_id == project.id)
        )
    }

    for index in range(1, customers_per_project + 1):
        document = f"DUMMY-{tenant.id}-{project.id}-{index:05d}"
        if document in existing_docs:
            continue
        base_balance = rng.randint(250_000, 42_000_000)
        dpd = rng.choice([rng.randint(0, 14), rng.randint(15, 35), rng.randint(36, 70), rng.randint(71, 120)])
        status = rng.choices(STATUSES, weights=[24, 26, 18, 10, 7, 15], k=1)[0]
        risk = risk_from_dpd(dpd, base_balance)
        assigned = rng.choice(agents)
        last_contact_at = None if status == "Sin contacto" else now - timedelta(days=rng.randint(0, 18))
        next_contact_at = now + timedelta(days=rng.randint(-3, 14)) if status in {"Promesa", "Contactado", "Escalado"} else None
        customer = Customer(
            tenant_id=tenant.id,
            project_id=project.id,
            assigned_user_id=assigned.id,
            name=customer_name(rng, index),
            document=document,
            phone=f"+57 3{rng.randint(0, 9)}0 {rng.randint(100, 999)} {rng.randint(1000, 9999)}",
            email=f"cliente{index:05d}.{project_key}@demo-clientes.local",
            city=rng.choice(CITIES),
            segment=rng.choice(SEGMENTS),
            obligation=f"OBL-{project_key.upper()}-{index:05d}",
            balance=base_balance,
            original_balance=round(base_balance * rng.uniform(1.0, 1.22)),
            dpd=dpd,
            status=status,
            risk=risk,
            priority=priority_score(dpd, base_balance, risk, status),
            next_action=next_action_for(status, risk),
            contactability=rng.choices(("Alta", "Media", "Baja"), weights=[36, 48, 16], k=1)[0],
            notes="Cliente demo generado para pruebas de tableros, BI, cola y reportes.",
            last_contact_at=last_contact_at,
            next_contact_at=next_contact_at,
        )
        db.add(customer)
        db.flush()
        created += 1
        a_count, p_count, pay_count = create_activity_package(db, customer, assigned, rng, now)
        activities += a_count
        promises += p_count
        payments += pay_count
    return {"customers": created, "activities": activities, "promises": promises, "payments": payments}


def ensure_demo_structure(db: Session) -> tuple[list[Tenant], list[Project], dict[str, int]]:
    stats = {"tenants": 0, "projects": 0, "channels": 0, "typifications": 0}
    for demo in DEMO_TENANTS:
        before = db.scalar(select(Tenant).where(Tenant.slug == demo.slug))
        tenant = get_or_create_tenant(db, demo)
        if before is None:
            stats["tenants"] += 1
        for name, code, description in demo.projects:
            before_project = db.scalar(select(Project).where(Project.tenant_id == tenant.id, Project.code == code))
            get_or_create_project(db, tenant, name, code, description)
            if before_project is None:
                stats["projects"] += 1

    business_tenants = list(
        db.scalars(select(Tenant).where(Tenant.slug != settings.platform_tenant_slug).order_by(Tenant.name))
    )
    for tenant in business_tenants:
        stats["channels"] += ensure_channels(db, tenant)
        stats["typifications"] += ensure_typifications(db, tenant)
        tenant_projects = list(db.scalars(select(Project).where(Project.tenant_id == tenant.id).order_by(Project.name)))
        if not tenant_projects:
            for name, code, description in FALLBACK_PROJECTS:
                get_or_create_project(db, tenant, name, code, description)
                stats["projects"] += 1
            continue
        if len(tenant_projects) < 3:
            for name, code, description in FALLBACK_PROJECTS[: 3 - len(tenant_projects)]:
                existing_code = code
                suffix = 2
                while db.scalar(select(Project).where(Project.tenant_id == tenant.id, Project.code == existing_code)):
                    existing_code = f"{code}-{suffix}"
                    suffix += 1
                get_or_create_project(db, tenant, name, existing_code, description)
                stats["projects"] += 1

    projects = list(
        db.scalars(
            select(Project)
            .join(Tenant, Tenant.id == Project.tenant_id)
            .where(Tenant.slug != settings.platform_tenant_slug, Project.status == "active")
            .order_by(Tenant.name, Project.name)
        )
    )
    return business_tenants, projects, stats


def run(customers_per_project: int, seed: int, commit_every_project: bool) -> dict[str, int]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurado.")
    init_status = init_database()
    if not init_status.get("ok"):
        raise RuntimeError(init_status.get("detail", "No fue posible verificar la base de datos."))

    totals = {
        "tenants_created": 0,
        "projects_created": 0,
        "channels_created": 0,
        "typifications_created": 0,
        "assignments_checked": 0,
        "customers_created": 0,
        "activities_created": 0,
        "promises_created": 0,
        "payments_created": 0,
    }
    with SessionLocal() as db:
        _, projects, structure = ensure_demo_structure(db)
        totals["tenants_created"] += structure["tenants"]
        totals["projects_created"] += structure["projects"]
        totals["channels_created"] += structure["channels"]
        totals["typifications_created"] += structure["typifications"]

        for project in projects:
            tenant = db.get(Tenant, project.tenant_id)
            if tenant is None:
                continue
            agents, assignments = ensure_project_staff(db, tenant, project)
            totals["assignments_checked"] += assignments
            stats = seed_customers(db, tenant, project, agents, customers_per_project, seed)
            totals["customers_created"] += stats["customers"]
            totals["activities_created"] += stats["activities"]
            totals["promises_created"] += stats["promises"]
            totals["payments_created"] += stats["payments"]
            if commit_every_project:
                db.commit()
        db.commit()
    return totals


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera data dummy corporativa para IcodeUp CRM V2.")
    parser.add_argument("--customers-per-project", type=int, default=125)
    parser.add_argument("--seed", type=int, default=20260514)
    parser.add_argument("--single-transaction", action="store_true")
    args = parser.parse_args()
    totals = run(
        customers_per_project=max(1, args.customers_per_project),
        seed=args.seed,
        commit_every_project=not args.single_transaction,
    )
    print("Data demo V2 generada:")
    for key, value in totals.items():
        print(f"- {key}: {value}")
    print(f"- password_demo_usuarios: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    main()
