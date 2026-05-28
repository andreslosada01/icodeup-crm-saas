from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN, ROLE_LABELS
from app.core.security import hash_password
from app.models import MenuItem, Module, Permission, Role, RolePermission, SaasPlan, Tenant, TenantConfiguration, TenantModule, User
from app.services.access_control import sync_user_profile


MODULE_DEFS = [
    ("core", "Core SaaS", "Base comun de empresas, usuarios, permisos y configuracion.", "core", 0, "grid", 1),
    ("administration", "Administracion", "Gobierno de usuarios, roles, permisos y tenant.", "core", 0, "settings", 2),
    ("crm", "CRM 360", "Terceros, clientes, contactos y operacion comercial.", "business", 0, "users", 10),
    ("collections", "Cobranzas", "Cartera, cola de gestion, promesas, pagos y acuerdos.", "business", 0, "wallet", 20),
    ("legal", "Juridico", "Expedientes, actuaciones, audiencias y vencimientos.", "business", 0, "scale", 30),
    ("documents", "Documentos", "Gestion documental y expedientes digitales.", "business", 0, "folder", 40),
    ("sales", "Ventas", "Leads, oportunidades y pipeline comercial.", "business", 0, "trending-up", 50),
    ("bi", "BI y Analitica", "Dashboards, reportes y analitica operacional.", "analytics", 0, "bar-chart", 60),
    ("integrations", "Integraciones", "Canales, APIs y conectores empresariales.", "integration", 0, "plug", 70),
    ("hr", "Recursos Humanos", "Base futura para talento humano.", "future", 0, "badge", 100),
    ("finance", "Finanzas", "Base futura para contabilidad y finanzas.", "future", 0, "banknote", 110),
    ("industrial", "Operaciones Industriales", "Base futura para produccion, calidad y mantenimiento.", "future", 0, "factory", 120),
]

PLAN_DEFS = [
    ("Starter", "starter", "Entrada para equipos pequenos.", 0, 10, 2, 5000, False, False),
    ("Professional", "professional", "Operacion de crecimiento con documentos y BI operativo.", 0, 40, 8, 50000, False, True),
    ("Business", "business", "Operacion corporativa con modulos avanzados.", 0, 120, 25, 250000, True, True),
    ("Enterprise", "enterprise", "Licenciamiento a medida.", 0, 0, 0, 0, True, True),
]

PERMISSION_DEFS = [
    ("platform.governance.view", "Ver Gobierno SaaS", "core"),
    ("platform.governance.configure", "Configurar Gobierno SaaS", "core"),
    ("health.view", "Ver salud del sistema", "core"),
    ("tenant.manage", "Administrar empresa", "administration"),
    ("tenant.settings.view", "Ver configuracion de empresa", "administration"),
    ("tenant.settings.configure", "Configurar empresa y branding", "administration"),
    ("users.manage", "Administrar usuarios", "administration"),
    ("users.view", "Ver usuarios", "administration"),
    ("users.create", "Crear usuarios", "administration"),
    ("users.update", "Actualizar usuarios", "administration"),
    ("users.assign", "Asignar usuarios", "administration"),
    ("roles.manage", "Administrar roles y permisos", "administration"),
    ("roles.view", "Ver roles y permisos", "administration"),
    ("roles.create", "Crear roles", "administration"),
    ("roles.update", "Actualizar roles", "administration"),
    ("roles.configure", "Asignar permisos a roles", "administration"),
    ("modules.manage", "Administrar modulos", "administration"),
    ("modules.view", "Ver modulos contratados", "administration"),
    ("modules.configure", "Activar modulos por empresa", "administration"),
    ("audit.logs.view", "Ver auditoria", "administration"),
    ("audit.logs.export", "Exportar auditoria", "administration"),
    ("crm.read", "Leer CRM", "crm"),
    ("crm.manage", "Gestionar CRM", "crm"),
    ("crm.manage_own", "Gestionar CRM asignado", "crm"),
    ("crm.dashboard.view", "Ver tablero CRM", "crm"),
    ("crm.clients.view", "Ver clientes", "crm"),
    ("crm.clients.create", "Crear clientes", "crm"),
    ("crm.clients.update", "Actualizar clientes", "crm"),
    ("crm.clients.delete", "Eliminar clientes", "crm"),
    ("crm.clients.export", "Exportar clientes", "crm"),
    ("crm.clients.import", "Importar clientes", "crm"),
    ("parties.view", "Ver terceros maestros", "crm"),
    ("parties.create", "Crear terceros maestros", "crm"),
    ("parties.update", "Actualizar terceros maestros", "crm"),
    ("parties.export", "Exportar terceros maestros", "crm"),
    ("collections.read", "Leer cobranzas", "collections"),
    ("collections.manage", "Gestionar cobranzas", "collections"),
    ("collections.manage_own", "Gestionar cobranzas asignadas", "collections"),
    ("collections.queue.view", "Ver cola de gestion", "collections"),
    ("collections.promises.view", "Ver promesas", "collections"),
    ("collections.promises.create", "Crear promesas", "collections"),
    ("collections.promises.update", "Actualizar promesas", "collections"),
    ("collections.promises.export", "Exportar promesas", "collections"),
    ("collections.payments.view", "Ver pagos", "collections"),
    ("collections.payments.create", "Crear pagos", "collections"),
    ("collections.payments.export", "Exportar pagos", "collections"),
    ("collections.agreements.view", "Ver acuerdos", "collections"),
    ("collections.agreements.create", "Crear acuerdos", "collections"),
    ("collections.agreements.update", "Actualizar acuerdos", "collections"),
    ("collections.agreements.export", "Exportar acuerdos", "collections"),
    ("legal.read", "Leer juridico", "legal"),
    ("legal.manage", "Gestionar juridico", "legal"),
    ("legal.cases.view", "Ver casos juridicos", "legal"),
    ("legal.cases.create", "Crear casos juridicos", "legal"),
    ("legal.cases.update", "Actualizar casos juridicos", "legal"),
    ("legal.cases.export", "Exportar casos juridicos", "legal"),
    ("legal.deadlines.view", "Ver vencimientos juridicos", "legal"),
    ("documents.read", "Leer documentos", "documents"),
    ("documents.manage", "Gestionar documentos", "documents"),
    ("documents.view", "Ver documentos", "documents"),
    ("documents.create", "Crear documentos", "documents"),
    ("documents.update", "Actualizar documentos", "documents"),
    ("documents.export", "Exportar documentos", "documents"),
    ("sales.read_own", "Leer ventas asignadas", "sales"),
    ("sales.manage", "Gestionar ventas", "sales"),
    ("sales.leads.view", "Ver leads", "sales"),
    ("sales.leads.create", "Crear leads", "sales"),
    ("sales.leads.update", "Actualizar leads", "sales"),
    ("sales.leads.export", "Exportar leads", "sales"),
    ("sales.opportunities.view", "Ver oportunidades", "sales"),
    ("sales.opportunities.create", "Crear oportunidades", "sales"),
    ("sales.opportunities.update", "Actualizar oportunidades", "sales"),
    ("sales.opportunities.export", "Exportar oportunidades", "sales"),
    ("reports.view", "Ver reportes", "bi"),
    ("reports.export", "Exportar reportes", "bi"),
    ("integrations.channels.view", "Ver canales", "integrations"),
    ("integrations.channels.create", "Crear canales", "integrations"),
    ("integrations.channels.update", "Actualizar canales", "integrations"),
    ("menu.view", "Ver menu dinamico", "core"),
]

ROLE_PERMISSION_MAP = {
    PLATFORM_ADMIN: [code for code, _, _ in PERMISSION_DEFS],
    TENANT_ADMIN: [
        "tenant.manage", "tenant.settings.view", "tenant.settings.configure",
        "users.manage", "users.view", "users.create", "users.update", "users.assign",
        "roles.manage", "roles.view", "roles.create", "roles.update", "roles.configure",
        "modules.view", "crm.read", "crm.manage", "crm.dashboard.view",
        "crm.clients.view", "crm.clients.create", "crm.clients.update", "crm.clients.export", "crm.clients.import",
        "parties.view", "parties.create", "parties.update", "parties.export",
        "collections.read", "collections.manage", "collections.queue.view",
        "collections.promises.view", "collections.promises.create", "collections.promises.update", "collections.promises.export",
        "collections.payments.view", "collections.payments.create", "collections.payments.export",
        "collections.agreements.view", "collections.agreements.create", "collections.agreements.update", "collections.agreements.export",
        "legal.read", "legal.manage", "legal.cases.view", "legal.cases.create", "legal.cases.update", "legal.cases.export", "legal.deadlines.view",
        "documents.read", "documents.manage", "documents.view", "documents.create", "documents.update", "documents.export",
        "sales.manage", "sales.leads.view", "sales.leads.create", "sales.leads.update", "sales.leads.export", "sales.opportunities.view", "sales.opportunities.create", "sales.opportunities.update", "sales.opportunities.export",
        "reports.view", "reports.export", "integrations.channels.view", "integrations.channels.create", "integrations.channels.update",
        "audit.logs.view", "audit.logs.export", "menu.view",
    ],
    COORDINATOR: [
        "crm.read", "crm.manage", "crm.dashboard.view", "crm.clients.view", "crm.clients.create", "crm.clients.update", "crm.clients.import",
        "parties.view", "parties.create", "parties.update",
        "collections.read", "collections.manage", "collections.queue.view",
        "collections.promises.view", "collections.promises.create", "collections.promises.update",
        "collections.payments.view", "collections.payments.create",
        "collections.agreements.view", "collections.agreements.create", "collections.agreements.update",
        "legal.read", "legal.manage", "legal.cases.view", "legal.cases.create", "legal.cases.update", "legal.deadlines.view",
        "documents.read", "documents.manage", "documents.view", "documents.create", "documents.update",
        "sales.manage", "sales.leads.view", "sales.leads.create", "sales.leads.update", "sales.opportunities.view", "sales.opportunities.create", "sales.opportunities.update",
        "reports.view", "reports.export", "menu.view",
    ],
    QUALITY_SUPERVISOR: [
        "crm.read", "crm.dashboard.view", "crm.clients.view", "parties.view",
        "collections.read", "collections.queue.view", "collections.promises.view", "collections.payments.view", "collections.agreements.view",
        "legal.read", "legal.cases.view", "legal.deadlines.view", "documents.read", "documents.view",
        "reports.view", "menu.view",
    ],
    AGENT: [
        "crm.read", "crm.manage_own", "crm.dashboard.view", "crm.clients.view", "crm.clients.update",
        "parties.view", "collections.read", "collections.manage_own", "collections.queue.view",
        "collections.promises.view", "collections.promises.create", "collections.promises.update",
        "collections.payments.view", "collections.payments.create",
        "documents.read", "documents.view", "sales.read_own", "sales.leads.view", "sales.opportunities.view", "menu.view",
    ],
}

MENU_DEFS = [
    ("Gobierno SaaS", "governance", "core", "platform.governance.view", "platform_admin", 1),
    ("Empresas", "tenants", "administration", "tenant.manage", "platform_admin", 10),
    ("Planes", "plans", "administration", "platform.governance.configure", "platform_admin", 15),
    ("Suscripciones", "subscriptions", "administration", "platform.governance.configure", "platform_admin", 20),
    ("Modulos", "modules", "administration", "modules.configure", "platform_admin", 25),
    ("Usuarios", "users", "administration", "users.manage", "platform_admin", 30),
    ("Proyectos", "projects", "administration", "tenant.manage", "platform_admin", 35),
    ("Tipificaciones", "typifications", "collections", "collections.manage", "platform_admin", 40),
    ("Auditoria", "audit", "administration", "audit.logs.view", "platform_admin", 45),
    ("Salud sistema", "system-health", "core", "health.view", "platform_admin", 50),
    ("Inicio empresa", "dashboard", "core", "menu.view", "company_admin", 1),
    ("Mi empresa", "tenant-settings", "administration", "tenant.settings.view", "company_admin", 5),
    ("Usuarios", "company-users", "administration", "users.view", "company_admin", 10),
    ("Roles y permisos", "roles-permissions", "administration", "roles.view", "company_admin", 15),
    ("Modulos contratados", "tenant-modules", "administration", "modules.view", "company_admin", 20),
    ("Branding", "branding", "administration", "tenant.settings.configure", "company_admin", 25),
    ("Clientes / terceros", "customers", "crm", "crm.clients.view", "company_admin", 30),
    ("Tercero maestro", "parties", "crm", "parties.view", "company_admin", 35),
    ("Cola de gestion", "queue", "collections", "collections.queue.view", "company_admin", 40),
    ("Promesas", "promises", "collections", "collections.promises.view", "company_admin", 50),
    ("Pagos", "payments", "collections", "collections.payments.view", "company_admin", 60),
    ("Acuerdos", "agreements", "collections", "collections.agreements.view", "company_admin", 70),
    ("Juridico", "legal", "legal", "legal.cases.view", "company_admin", 80),
    ("Documentos", "documents", "documents", "documents.view", "company_admin", 90),
    ("Ventas", "sales", "sales", "sales.leads.view", "company_admin", 100),
    ("Reportes BI", "reports", "bi", "reports.view", "company_admin", 110),
    ("Canales", "channels", "integrations", "integrations.channels.view", "company_admin", 120),
    ("Auditoria", "audit", "administration", "audit.logs.view", "company_admin", 130),
    ("Inicio", "dashboard", "core", "menu.view", "operational_leader", 1),
    ("Cola de gestion", "queue", "collections", "collections.queue.view", "operational_leader", 10),
    ("Clientes / terceros", "customers", "crm", "crm.clients.view", "operational_leader", 20),
    ("Tercero maestro", "parties", "crm", "parties.view", "operational_leader", 25),
    ("Promesas", "promises", "collections", "collections.promises.view", "operational_leader", 30),
    ("Pagos", "payments", "collections", "collections.payments.view", "operational_leader", 40),
    ("Acuerdos", "agreements", "collections", "collections.agreements.view", "operational_leader", 50),
    ("Juridico", "legal", "legal", "legal.cases.view", "operational_leader", 60),
    ("Documentos", "documents", "documents", "documents.view", "operational_leader", 70),
    ("Ventas", "sales", "sales", "sales.leads.view", "operational_leader", 80),
    ("Reportes BI", "reports", "bi", "reports.view", "operational_leader", 90),
    ("Inicio", "dashboard", "core", "menu.view", "operational_user", 1),
    ("Mi operacion", "queue", "collections", "collections.queue.view", "operational_user", 10),
    ("Clientes / terceros", "customers", "crm", "crm.clients.view", "operational_user", 20),
    ("Tareas", "tasks", "collections", "collections.queue.view", "operational_user", 25),
    ("Documentos", "documents", "documents", "documents.view", "operational_user", 30),
]


def _get_or_create_module(db: Session, code: str, name: str, description: str, category: str, base_price: int, icon: str, order: int) -> Module:
    module = db.scalar(select(Module).where(Module.code == code))
    if module is None:
        module = Module(code=code, name=name)
        db.add(module)
    module.description = description
    module.category = category
    module.base_price = base_price
    module.icon = icon
    module.order = order
    module.is_active = True
    return module


def _seed_modules(db: Session) -> dict[str, Module]:
    modules = {}
    for args in MODULE_DEFS:
        module = _get_or_create_module(db, *args)
        modules[module.code] = module
    db.flush()
    return modules


def _seed_plans(db: Session) -> None:
    for name, code, description, price, max_users, max_projects, max_records, includes_ai, includes_advanced_bi in PLAN_DEFS:
        plan = db.scalar(select(SaasPlan).where(SaasPlan.code == code))
        if plan is None:
            plan = SaasPlan(name=name, code=code)
            db.add(plan)
        plan.description = description
        plan.base_price = price
        plan.monthly_price = price
        plan.max_users = max_users
        plan.max_projects = max_projects
        plan.max_customers = max_records
        plan.max_records = max_records
        plan.includes_ai = includes_ai
        plan.includes_advanced_bi = includes_advanced_bi
        plan.includes_collections = True
        plan.includes_bi = True
        plan.is_active = True
        plan.status = "active"


def _seed_roles_and_permissions(db: Session, modules: dict[str, Module]) -> dict[str, Role]:
    permissions = {}
    for code, name, module_code in PERMISSION_DEFS:
        permission = db.scalar(select(Permission).where(Permission.code == code))
        if permission is None:
            permission = Permission(code=code, name=name)
            db.add(permission)
        permission.name = name
        permission.module_code = module_code
        permission.module_id = modules[module_code].id if module_code in modules else None
        permissions[code] = permission
    roles = {}
    for code, label in ROLE_LABELS.items():
        role = db.scalar(select(Role).where(Role.tenant_id.is_(None), Role.code == code))
        if role is None:
            role = Role(tenant_id=None, code=code, name=label, is_system_role=True)
            db.add(role)
        role.name = label
        role.is_active = True
        roles[code] = role
    db.flush()
    for role_code, permission_codes in ROLE_PERMISSION_MAP.items():
        role = roles[role_code]
        existing = {
            item.permission_id
            for item in db.scalars(select(RolePermission).where(RolePermission.role_id == role.id))
        }
        for permission_code in permission_codes:
            permission = permissions[permission_code]
            if permission.id not in existing:
                db.add(RolePermission(role_id=role.id, permission_id=permission.id))
    return roles


def _seed_menu(db: Session, modules: dict[str, Module]) -> None:
    for existing_item in db.scalars(select(MenuItem)):
        existing_item.is_active = False
    for label, route_name, module_code, permission_code, audience, order in MENU_DEFS:
        item = db.scalar(
            select(MenuItem).where(
                MenuItem.route_name == route_name,
                MenuItem.module_code == module_code,
                MenuItem.audience == audience,
            )
        )
        if item is None:
            item = MenuItem(label=label, route_name=route_name, audience=audience)
            db.add(item)
        item.label = label
        item.url = f"#{route_name}"
        item.module_code = module_code
        item.module_id = modules[module_code].id if module_code in modules else None
        item.required_permission = permission_code
        item.required_permission_code = permission_code
        item.order = order
        item.is_active = True


def _seed_tenant_modules(db: Session, modules: dict[str, Module]) -> None:
    tenants = list(db.scalars(select(Tenant)))
    default_enabled = {"core", "administration", "crm", "collections", "legal", "documents", "sales", "bi", "integrations"}
    for tenant in tenants:
        for module_code, module in modules.items():
            existing = db.scalar(select(TenantModule).where(TenantModule.tenant_id == tenant.id, TenantModule.module_code == module_code))
            if existing is None:
                enabled = tenant.slug == settings.platform_tenant_slug or module_code in default_enabled
                existing = TenantModule(
                    tenant_id=tenant.id,
                    module_id=module.id,
                    module_code=module_code,
                    enabled=enabled,
                    is_enabled=enabled,
                    enabled_at=datetime.now(timezone.utc) if enabled else None,
                )
                db.add(existing)
            else:
                existing.module_id = module.id
                existing.is_enabled = existing.enabled if existing.enabled is not None else existing.is_enabled
                if existing.is_enabled and existing.enabled_at is None:
                    existing.enabled_at = datetime.now(timezone.utc)


def _seed_tenant_configuration(db: Session, tenant: Tenant) -> None:
    defaults = {
        "login.headline": "Plataforma Inteligente de Operaciones Empresariales",
        "login.subheadline": "Gestiona operaciones, datos, modulos y decisiones desde una experiencia SaaS segura.",
        "branding.primary_color": tenant.primary_color,
        "branding.secondary_color": tenant.secondary_color,
    }
    for key, value in defaults.items():
        config = db.scalar(select(TenantConfiguration).where(TenantConfiguration.tenant_id == tenant.id, TenantConfiguration.key == key))
        if config is None:
            db.add(TenantConfiguration(tenant_id=tenant.id, key=key, value_json=f'"{value}"', is_active=True))


def bootstrap_platform(db: Session) -> None:
    if not settings.platform_admin_email or not settings.platform_admin_password:
        return

    modules = _seed_modules(db)
    _seed_plans(db)
    roles = _seed_roles_and_permissions(db, modules)
    _seed_menu(db, modules)

    tenant = db.scalar(select(Tenant).where(Tenant.slug == settings.platform_tenant_slug))
    if tenant is None:
        tenant = Tenant(
            name="IcodeUp Platform",
            slug=settings.platform_tenant_slug,
            tax_id="PLATFORM",
            document_type="NIT",
            document_number="PLATFORM",
            primary_color="#15956f",
            secondary_color="#2563eb",
        )
        db.add(tenant)
        db.flush()
    tenant.document_type = tenant.document_type or "NIT"
    tenant.document_number = tenant.document_number or tenant.tax_id
    tenant.timezone = tenant.timezone or "America/Bogota"

    user = db.scalar(select(User).where(User.email == settings.platform_admin_email.lower()))
    if user is None:
        user = User(
            tenant_id=tenant.id,
            name="IcodeUp Plataforma",
            email=settings.platform_admin_email.lower(),
            role=PLATFORM_ADMIN,
            password_hash=hash_password(settings.platform_admin_password),
        )
        db.add(user)
        db.flush()
    user.role = PLATFORM_ADMIN
    user.tenant_id = tenant.id

    for existing_tenant in db.scalars(select(Tenant)):
        existing_tenant.document_number = existing_tenant.document_number or existing_tenant.tax_id
        existing_tenant.document_type = existing_tenant.document_type or "NIT"
        existing_tenant.primary_color = existing_tenant.primary_color or "#15956f"
        existing_tenant.secondary_color = existing_tenant.secondary_color or "#2563eb"
        existing_tenant.timezone = existing_tenant.timezone or "America/Bogota"
        _seed_tenant_configuration(db, existing_tenant)

    _seed_tenant_modules(db, modules)
    for existing_user in db.scalars(select(User)):
        sync_user_profile(db, existing_user)

    db.commit()
