from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN, ROLE_LABELS
from app.core.security import hash_password
from app.models import (
    CommunicationChannel,
    CallRecording,
    ChannelConfiguration,
    ChannelEventLog,
    CommunicationTemplate,
    Customer,
    CustomerDemographic,
    CustomerObligation,
    Document,
    AlertRule,
    BusinessRule,
    FunctionalCatalog,
    Lead,
    IntegrationProvider,
    LegalAction,
    LegalCase,
    LegalDeadline,
    LegalHearing,
    ManagementActivity,
    MenuItem,
    Module,
    Opportunity,
    OperationalSheetRow,
    Party,
    Payment,
    PaymentAgreement,
    PaymentAgreementInstallment,
    PaymentPromise,
    Permission,
    Project,
    SavedDataView,
    Role,
    RolePermission,
    SaasPlan,
    Tenant,
    TenantConfiguration,
    TenantModule,
    TenantSubscription,
    TypificationCombinationRule,
    TypificationNode,
    TypificationTree,
    TypificationTreeNode,
    UploadBatch,
    User,
    UserProjectAssignment,
    UserProfile,
    WorkflowDefinition,
    WorkflowStage,
    WebhookConfiguration,
)
from app.services.access_control import sync_user_profile


DEMO_PASSWORD = "Demo360!2026"

MODULE_DEFS = [
    ("core", "Core SaaS", "Base comun de empresas, usuarios, permisos y configuracion.", "core", 0, "grid", 1),
    ("administration", "Administracion", "Gobierno de usuarios, roles, permisos y tenant.", "core", 0, "settings", 2),
    ("crm", "CRM 360", "Terceros, clientes, contactos y operacion comercial.", "business", 0, "users", 10),
    ("collections", "Cobranzas", "Cartera, cola de gestion, promesas, pagos y acuerdos.", "business", 0, "wallet", 20),
    ("legal", "Juridico", "Expedientes, actuaciones, audiencias y vencimientos.", "business", 0, "scale", 30),
    ("documents", "Documentos", "Gestion documental y expedientes digitales.", "business", 0, "folder", 40),
    ("sales", "Ventas", "Leads, oportunidades y pipeline comercial.", "business", 0, "trending-up", 50),
    ("bi", "BI y Analitica", "Dashboards, reportes y analitica operacional.", "analytics", 0, "bar-chart", 60),
    ("telephony", "Telefonia", "Click-to-call, extensiones, logs de llamadas y base WebRTC.", "integration", 0, "phone-call", 65),
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
    ("teams.view", "Ver equipos y carteras", "administration"),
    ("teams.manage", "Administrar equipos y carteras", "administration"),
    ("project_users.view", "Ver usuarios por cartera", "administration"),
    ("project_users.manage", "Asignar usuarios a carteras", "administration"),
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
    ("configuration.view", "Ver Centro de Configuracion", "administration"),
    ("configuration.manage", "Administrar configuracion funcional", "administration"),
    ("configuration.catalogs.manage", "Administrar catalogos funcionales", "administration"),
    ("configuration.rules.manage", "Administrar reglas de negocio", "administration"),
    ("configuration.alerts.manage", "Administrar reglas de alertas", "administration"),
    ("configuration.workflows.manage", "Administrar workflows", "administration"),
    ("alerts.view", "Ver alertas operativas", "bi"),
    ("alerts.manage", "Gestionar alertas", "bi"),
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
    ("crm.assignments.view", "Ver asignaciones operativas", "crm"),
    ("crm.assignments.manage", "Administrar asignaciones operativas", "crm"),
    ("crm.activities.view", "Ver gestiones", "crm"),
    ("crm.activities.create", "Registrar gestiones", "crm"),
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
    ("typifications.view", "Ver arboles de tipificacion", "collections"),
    ("typifications.manage", "Administrar tipificaciones legacy", "collections"),
    ("typifications.trees.manage", "Administrar arboles de gestion", "collections"),
    ("typifications.combinations.manage", "Administrar combinaciones", "collections"),
    ("recordings.view", "Ver grabaciones", "collections"),
    ("recordings.playback", "Reproducir grabaciones", "collections"),
    ("recordings.download", "Descargar grabaciones", "collections"),
    ("recordings.manage", "Administrar grabaciones", "collections"),
    ("recordings.audit.view", "Auditar grabaciones", "collections"),
    ("telephony.view", "Ver telefonia", "telephony"),
    ("telephony.manage", "Administrar proveedores de telefonia", "telephony"),
    ("telephony.call", "Iniciar click-to-call", "telephony"),
    ("telephony.logs.view", "Ver historial de llamadas", "telephony"),
    ("telephony.extensions.manage", "Administrar extensiones", "telephony"),
    ("uploads.view", "Ver cargas", "collections"),
    ("uploads.preview", "Previsualizar cargas", "collections"),
    ("uploads.confirm", "Confirmar cargas", "collections"),
    ("uploads.manage", "Administrar cargas", "collections"),
    ("uploads.repartos.manage", "Cargar repartos", "collections"),
    ("uploads.demographics.manage", "Cargar demograficos", "collections"),
    ("uploads.download", "Descargar resultados de cargas", "collections"),
    ("demographics.view", "Ver demograficos", "collections"),
    ("demographics.manage", "Administrar demograficos", "collections"),
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
    ("excel_web.view", "Ver Mi Excel Web", "bi"),
    ("excel_web.query", "Consultar Mi Excel Web", "bi"),
    ("excel_web.export", "Exportar Mi Excel Web", "bi"),
    ("excel_web.views.manage", "Administrar vistas Mi Excel Web", "bi"),
    ("excel_web.sheet.manage", "Administrar hoja operativa Mi Excel Web", "bi"),
    ("integrations.providers.view", "Ver proveedores de integracion", "integrations"),
    ("integrations.providers.manage", "Administrar proveedores de integracion", "integrations"),
    ("integrations.channels.view", "Ver canales", "integrations"),
    ("integrations.channels.create", "Crear canales", "integrations"),
    ("integrations.channels.update", "Actualizar canales", "integrations"),
    ("integrations.templates.view", "Ver plantillas de comunicacion", "integrations"),
    ("integrations.templates.manage", "Administrar plantillas de comunicacion", "integrations"),
    ("integrations.webhooks.view", "Ver webhooks", "integrations"),
    ("integrations.webhooks.manage", "Administrar webhooks", "integrations"),
    ("integrations.events.view", "Ver logs de canales", "integrations"),
    ("menu.view", "Ver menu dinamico", "core"),
]

ROLE_PERMISSION_MAP = {
    PLATFORM_ADMIN: [code for code, _, _ in PERMISSION_DEFS],
    TENANT_ADMIN: [
        "tenant.manage", "tenant.settings.view", "tenant.settings.configure",
        "users.manage", "users.view", "users.create", "users.update", "users.assign",
        "teams.view", "teams.manage", "project_users.view", "project_users.manage",
        "roles.manage", "roles.view", "roles.create", "roles.update", "roles.configure",
        "modules.view", "crm.read", "crm.manage", "crm.dashboard.view",
        "crm.clients.view", "crm.clients.create", "crm.clients.update", "crm.clients.export", "crm.clients.import",
        "crm.assignments.view", "crm.assignments.manage",
        "crm.activities.view", "crm.activities.create",
        "parties.view", "parties.create", "parties.update", "parties.export",
        "collections.read", "collections.manage", "collections.queue.view",
        "collections.promises.view", "collections.promises.create", "collections.promises.update", "collections.promises.export",
        "collections.payments.view", "collections.payments.create", "collections.payments.export",
        "collections.agreements.view", "collections.agreements.create", "collections.agreements.update", "collections.agreements.export",
        "typifications.view", "typifications.manage", "typifications.trees.manage", "typifications.combinations.manage",
        "recordings.view", "recordings.playback", "recordings.download", "recordings.manage", "recordings.audit.view",
        "telephony.view", "telephony.manage", "telephony.call", "telephony.logs.view", "telephony.extensions.manage",
        "uploads.view", "uploads.preview", "uploads.confirm", "uploads.manage", "uploads.repartos.manage", "uploads.demographics.manage", "uploads.download",
        "demographics.view", "demographics.manage",
        "legal.read", "legal.manage", "legal.cases.view", "legal.cases.create", "legal.cases.update", "legal.cases.export", "legal.deadlines.view",
        "documents.read", "documents.manage", "documents.view", "documents.create", "documents.update", "documents.export",
        "sales.manage", "sales.leads.view", "sales.leads.create", "sales.leads.update", "sales.leads.export", "sales.opportunities.view", "sales.opportunities.create", "sales.opportunities.update", "sales.opportunities.export",
        "reports.view", "reports.export", "excel_web.view", "excel_web.query", "excel_web.export", "excel_web.views.manage", "excel_web.sheet.manage",
        "integrations.providers.view", "integrations.providers.manage", "integrations.channels.view", "integrations.channels.create", "integrations.channels.update",
        "integrations.templates.view", "integrations.templates.manage", "integrations.webhooks.view", "integrations.webhooks.manage", "integrations.events.view",
        "audit.logs.view", "audit.logs.export", "menu.view",
        "configuration.view", "configuration.manage", "configuration.catalogs.manage", "configuration.rules.manage",
        "configuration.alerts.manage", "configuration.workflows.manage", "alerts.view", "alerts.manage",
    ],
    COORDINATOR: [
        "crm.read", "crm.manage", "crm.dashboard.view", "crm.clients.view", "crm.clients.create", "crm.clients.update", "crm.clients.import",
        "teams.view", "project_users.view", "crm.assignments.view", "crm.assignments.manage",
        "crm.activities.view", "crm.activities.create",
        "parties.view", "parties.create", "parties.update",
        "collections.read", "collections.manage", "collections.queue.view",
        "collections.promises.view", "collections.promises.create", "collections.promises.update",
        "collections.payments.view", "collections.payments.create",
        "collections.agreements.view", "collections.agreements.create", "collections.agreements.update",
        "typifications.view", "recordings.view", "recordings.playback", "uploads.view", "uploads.preview", "uploads.confirm", "uploads.repartos.manage", "uploads.demographics.manage", "demographics.view",
        "telephony.view", "telephony.call", "telephony.logs.view",
        "legal.read", "legal.manage", "legal.cases.view", "legal.cases.create", "legal.cases.update", "legal.deadlines.view",
        "documents.read", "documents.manage", "documents.view", "documents.create", "documents.update",
        "sales.manage", "sales.leads.view", "sales.leads.create", "sales.leads.update", "sales.opportunities.view", "sales.opportunities.create", "sales.opportunities.update",
        "reports.view", "reports.export", "excel_web.view", "excel_web.query", "excel_web.sheet.manage", "menu.view", "alerts.view",
    ],
    QUALITY_SUPERVISOR: [
        "crm.read", "crm.dashboard.view", "crm.clients.view", "parties.view",
        "teams.view", "project_users.view", "crm.assignments.view",
        "collections.read", "collections.queue.view", "collections.promises.view", "collections.payments.view", "collections.agreements.view",
        "crm.activities.view", "typifications.view", "recordings.view", "recordings.playback", "demographics.view", "excel_web.view", "excel_web.query",
        "telephony.view", "telephony.logs.view",
        "legal.read", "legal.cases.view", "legal.deadlines.view", "documents.read", "documents.view",
        "reports.view", "menu.view", "alerts.view",
    ],
    AGENT: [
        "crm.read", "crm.manage_own", "crm.dashboard.view", "crm.clients.view", "crm.clients.update", "crm.activities.view", "crm.activities.create",
        "parties.view", "collections.read", "collections.manage_own", "collections.queue.view",
        "collections.promises.view", "collections.promises.create", "collections.promises.update",
        "collections.payments.view", "collections.payments.create",
        "collections.agreements.view", "collections.agreements.create",
        "telephony.view", "telephony.call", "telephony.logs.view",
        "documents.read", "documents.view", "documents.create", "typifications.view", "demographics.view",
        "excel_web.view", "excel_web.query", "excel_web.views.manage", "excel_web.sheet.manage", "menu.view", "alerts.view",
    ],
}

SPECIALIZED_ROLE_DEFS = {
    "legal_director": {
        "name": "Director Juridico",
        "description": "Gestion juridica integral del tenant con documentos y lectura de clientes.",
        "permissions": [
            "menu.view", "crm.read", "crm.clients.view", "legal.read", "legal.manage",
            "legal.cases.view", "legal.cases.create", "legal.cases.update", "legal.deadlines.view",
            "documents.read", "documents.manage", "documents.view", "documents.create", "documents.update",
            "recordings.view", "recordings.playback", "demographics.view", "excel_web.view", "excel_web.query",
            "reports.view", "audit.logs.view", "alerts.view",
        ],
    },
    "lawyer": {
        "name": "Abogado",
        "description": "Gestion juridica de casos y documentos sin permisos amplios de cobranzas.",
        "permissions": [
            "menu.view", "crm.read", "crm.clients.view", "legal.read", "legal.manage",
            "legal.cases.view", "legal.cases.create", "legal.cases.update", "legal.deadlines.view",
            "documents.read", "documents.view", "documents.create", "recordings.view", "demographics.view", "alerts.view",
        ],
    },
    "sales_leader": {
        "name": "Lider Comercial",
        "description": "Gestion comercial del tenant con tablero y clientes en lectura.",
        "permissions": [
            "menu.view", "crm.read", "crm.clients.view", "sales.manage",
            "sales.leads.view", "sales.leads.create", "sales.leads.update", "sales.leads.export",
            "sales.opportunities.view", "sales.opportunities.create", "sales.opportunities.update", "sales.opportunities.export",
            "excel_web.view", "excel_web.query", "reports.view", "alerts.view",
        ],
    },
    "sales_advisor": {
        "name": "Asesor Comercial",
        "description": "Gestion de leads y oportunidades sin acceso a juridico ni cobranzas.",
        "permissions": [
            "menu.view", "crm.read", "crm.clients.view", "sales.read_own", "sales.manage",
            "sales.leads.view", "sales.leads.create", "sales.leads.update",
            "sales.opportunities.view", "sales.opportunities.create", "sales.opportunities.update", "excel_web.view", "excel_web.query", "alerts.view",
        ],
    },
    "collections_leader": {
        "name": "Lider de Cobranzas",
        "description": "Lider operativo de cobranza con permisos configurables equivalentes al coordinador.",
        "permissions": ROLE_PERMISSION_MAP[COORDINATOR],
    },
    "collections_agent": {
        "name": "Gestor de Cobranzas",
        "description": "Gestor operativo con alcance asignado y permisos configurables.",
        "permissions": ROLE_PERMISSION_MAP[AGENT],
    },
    "tenant_auditor": {
        "name": "Auditor Tenant",
        "description": "Lectura, auditoria y reportes del tenant sin gestion operativa.",
        "permissions": [
            "menu.view", "crm.read", "crm.dashboard.view", "crm.clients.view", "parties.view",
            "collections.read", "collections.queue.view", "collections.promises.view", "collections.payments.view", "collections.agreements.view",
            "legal.read", "legal.cases.view", "legal.deadlines.view", "documents.read", "documents.view",
            "typifications.view", "recordings.view", "recordings.playback", "recordings.audit.view", "uploads.view", "demographics.view", "excel_web.view", "excel_web.query", "reports.view", "audit.logs.view", "alerts.view",
        ],
    },
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
    ("Centro de Configuracion", "configuration", "administration", "configuration.view", "platform_admin", 47),
    ("Alertas", "alerts", "bi", "alerts.view", "platform_admin", 48),
    ("Telefonia", "telephony", "telephony", "telephony.view", "platform_admin", 49),
    ("Salud sistema", "system-health", "core", "health.view", "platform_admin", 50),
    ("Inicio empresa", "dashboard", "core", "menu.view", "company_admin", 1),
    ("Mi empresa", "tenant-settings", "administration", "tenant.settings.view", "company_admin", 5),
    ("Usuarios", "company-users", "administration", "users.view", "company_admin", 10),
    ("Roles y permisos", "roles-permissions", "administration", "roles.view", "company_admin", 15),
    ("Modulos contratados", "tenant-modules", "administration", "modules.view", "company_admin", 20),
    ("Branding", "branding", "administration", "tenant.settings.configure", "company_admin", 25),
    ("Equipos y carteras", "teams", "administration", "teams.view", "company_admin", 28),
    ("Clientes / terceros", "customers", "crm", "crm.clients.view", "company_admin", 30),
    ("Tercero maestro", "parties", "crm", "parties.view", "company_admin", 35),
    ("Cola de gestion", "queue", "collections", "collections.queue.view", "company_admin", 40),
    ("Promesas", "promises", "collections", "collections.promises.view", "company_admin", 50),
    ("Pagos", "payments", "collections", "collections.payments.view", "company_admin", 60),
    ("Acuerdos", "agreements", "collections", "collections.agreements.view", "company_admin", 70),
    ("Arboles de gestion", "typification-trees", "collections", "typifications.view", "company_admin", 72),
    ("Grabaciones", "recordings", "collections", "recordings.view", "company_admin", 74),
    ("Telefonia", "telephony", "telephony", "telephony.view", "company_admin", 75),
    ("Cargas y repartos", "uploads", "collections", "uploads.view", "company_admin", 76),
    ("Juridico", "legal", "legal", "legal.cases.view", "company_admin", 80),
    ("Documentos", "documents", "documents", "documents.view", "company_admin", 90),
    ("Ventas", "sales", "sales", "sales.leads.view", "company_admin", 100),
    ("Mi Excel Web", "excel-web", "bi", "excel_web.view", "company_admin", 108),
    ("Reportes BI", "reports", "bi", "reports.view", "company_admin", 110),
    ("Canales", "channels", "integrations", "integrations.channels.view", "company_admin", 120),
    ("Integraciones", "integrations", "integrations", "integrations.providers.view", "company_admin", 122),
    ("Centro de Configuracion", "configuration", "administration", "configuration.view", "company_admin", 125),
    ("Alertas", "alerts", "bi", "alerts.view", "company_admin", 128),
    ("Auditoria", "audit", "administration", "audit.logs.view", "company_admin", 130),
    ("Inicio", "dashboard", "core", "menu.view", "operational_leader", 1),
    ("Cola de gestion", "queue", "collections", "collections.queue.view", "operational_leader", 10),
    ("Clientes / terceros", "customers", "crm", "crm.clients.view", "operational_leader", 20),
    ("Tercero maestro", "parties", "crm", "parties.view", "operational_leader", 25),
    ("Promesas", "promises", "collections", "collections.promises.view", "operational_leader", 30),
    ("Pagos", "payments", "collections", "collections.payments.view", "operational_leader", 40),
    ("Acuerdos", "agreements", "collections", "collections.agreements.view", "operational_leader", 50),
    ("Equipos y carteras", "teams", "administration", "teams.view", "operational_leader", 51),
    ("Grabaciones", "recordings", "collections", "recordings.view", "operational_leader", 52),
    ("Telefonia", "telephony", "telephony", "telephony.view", "operational_leader", 53),
    ("Cargas y repartos", "uploads", "collections", "uploads.view", "operational_leader", 54),
    ("Juridico", "legal", "legal", "legal.cases.view", "operational_leader", 60),
    ("Documentos", "documents", "documents", "documents.view", "operational_leader", 70),
    ("Ventas", "sales", "sales", "sales.leads.view", "operational_leader", 80),
    ("Mi Excel Web", "excel-web", "bi", "excel_web.view", "operational_leader", 88),
    ("Reportes BI", "reports", "bi", "reports.view", "operational_leader", 90),
    ("Alertas", "alerts", "bi", "alerts.view", "operational_leader", 95),
    ("Inicio", "dashboard", "core", "menu.view", "operational_user", 1),
    ("Mi operacion", "queue", "collections", "collections.queue.view", "operational_user", 10),
    ("Clientes / terceros", "customers", "crm", "crm.clients.view", "operational_user", 20),
    ("Tareas", "tasks", "collections", "collections.queue.view", "operational_user", 25),
    ("Promesas", "promises", "collections", "collections.promises.view", "operational_user", 30),
    ("Pagos", "payments", "collections", "collections.payments.view", "operational_user", 40),
    ("Acuerdos", "agreements", "collections", "collections.agreements.view", "operational_user", 50),
    ("Mi telefono", "telephony", "telephony", "telephony.view", "operational_user", 55),
    ("Documentos", "documents", "documents", "documents.view", "operational_user", 60),
    ("Mi Excel Web", "excel-web", "bi", "excel_web.view", "operational_user", 65),
    ("Alertas", "alerts", "bi", "alerts.view", "operational_user", 70),
]

CATALOG_DEFAULTS = [
    ("collections", "customer_status", "SIN_CONTACTO", "Sin contacto", "#94a3b8", 10),
    ("collections", "customer_status", "CONTACTADO", "Contactado", "#2563eb", 20),
    ("collections", "customer_status", "PROMESA", "Promesa", "#f59e0b", 30),
    ("collections", "customer_status", "ESCALADO", "Escalado", "#dc2626", 40),
    ("collections", "risk", "BAJO", "Bajo", "#16a34a", 10),
    ("collections", "risk", "MEDIO", "Medio", "#f59e0b", 20),
    ("collections", "risk", "ALTO", "Alto", "#dc2626", 30),
    ("legal", "process_type", "EJECUTIVO", "Ejecutivo singular", "#2563eb", 10),
    ("legal", "process_stage", "RECIBIDO", "Recibido", "#64748b", 10),
    ("legal", "process_stage", "ESTUDIO", "En estudio", "#2563eb", 20),
    ("legal", "process_stage", "RADICADO", "Radicado", "#7c3aed", 30),
    ("legal", "process_stage", "TRAMITE", "En tramite", "#f59e0b", 40),
    ("legal", "process_stage", "AUDIENCIA", "Audiencia", "#dc2626", 50),
    ("legal", "process_stage", "FALLO", "Fallo", "#16a34a", 60),
    ("legal", "action_type", "REVISION", "Revision documental", "#2563eb", 10),
    ("legal", "hearing_type", "AUDIENCIA", "Audiencia", "#dc2626", 10),
    ("documents", "document_type", "PAGARE", "Pagare", "#2563eb", 10),
    ("documents", "document_type", "ACUERDO", "Acuerdo de pago", "#16a34a", 20),
    ("documents", "document_type", "DEMANDA", "Demanda", "#dc2626", 30),
    ("sales", "lead_source", "DEMO", "Demo comercial", "#2563eb", 10),
    ("sales", "opportunity_stage", "NEW", "Nuevo", "#64748b", 10),
    ("sales", "opportunity_stage", "CONTACTED", "Contactado", "#2563eb", 20),
    ("sales", "opportunity_stage", "PROPOSAL", "Propuesta", "#7c3aed", 30),
    ("sales", "opportunity_stage", "NEGOTIATION", "Negociacion", "#f59e0b", 40),
    ("sales", "opportunity_stage", "WON", "Ganado", "#16a34a", 50),
    ("sales", "opportunity_stage", "LOST", "Perdido", "#dc2626", 60),
]

BUSINESS_RULE_DEFAULTS = [
    ("collections", "sla", "CUSTOMER_WITHOUT_ACTIVITY", "Cliente sin gestion", '{"days": 7}', '{"alert": true}', "high"),
    ("collections", "sla", "PROMISE_DUE_SOON", "Promesa proxima a vencer", '{"days": 2}', '{"alert": true}', "medium"),
    ("legal", "sla", "LEGAL_DEADLINE_DUE_SOON", "Vencimiento juridico proximo", '{"days": 7}', '{"alert": true}', "high"),
    ("legal", "sla", "LEGAL_CASE_WITHOUT_ACTION", "Caso sin actuacion", '{"days": 10}', '{"alert": true}', "high"),
    ("sales", "sla", "LEAD_WITHOUT_FOLLOWUP", "Lead sin seguimiento", '{"days": 5}', '{"alert": true}', "medium"),
    ("sales", "sla", "OPPORTUNITY_CLOSE_DUE_SOON", "Oportunidad proxima a cierre", '{"days": 7}', '{"alert": true}', "high"),
]

ALERT_RULE_DEFAULTS = [
    ("collections", "CUSTOMER_WITHOUT_ACTIVITY", "Cliente sin gestion", "customer_without_activity", 7, "high", "collections_leader", "Cliente sin gestion reciente."),
    ("collections", "PROMISE_DUE_SOON", "Promesa proxima/vencida", "promise_due_soon", 2, "medium", "collections_agent", "Confirmar promesa antes del vencimiento."),
    ("legal", "LEGAL_DEADLINE_DUE_SOON", "Vencimiento juridico", "legal_deadline_due_soon", 7, "high", "lawyer", "Revisar termino procesal."),
    ("legal", "LEGAL_HEARING_DUE_SOON", "Audiencia proxima", "legal_hearing_due_soon", 5, "high", "lawyer", "Preparar audiencia y soportes."),
    ("legal", "LEGAL_CASE_WITHOUT_ACTION", "Caso sin actuacion", "legal_case_without_action", 10, "high", "legal_director", "Actualizar expediente juridico."),
    ("sales", "LEAD_WITHOUT_FOLLOWUP", "Lead sin seguimiento", "lead_without_followup", 5, "medium", "sales_advisor", "Registrar contacto comercial."),
    ("sales", "OPPORTUNITY_CLOSE_DUE_SOON", "Oportunidad proxima a cierre", "opportunity_close_due_soon", 7, "high", "sales_leader", "Actualizar plan de cierre."),
]

WORKFLOW_DEFAULTS = {
    "legal": {
        "code": "LEGAL_STANDARD",
        "name": "Flujo juridico estandar",
        "description": "Etapas base para expedientes de Collection & Legal CRM.",
        "stages": [
            ("RECIBIDO", "Recibido", "#64748b", 10, False),
            ("ESTUDIO", "En estudio", "#2563eb", 20, False),
            ("RADICADO", "Radicado", "#7c3aed", 30, False),
            ("TRAMITE", "En tramite", "#f59e0b", 40, False),
            ("AUDIENCIA", "Audiencia", "#dc2626", 50, False),
            ("FALLO", "Fallo", "#16a34a", 60, False),
            ("CERRADO", "Cerrado", "#0f766e", 70, True),
        ],
    },
    "sales": {
        "code": "SALES_PIPELINE",
        "name": "Pipeline comercial estandar",
        "description": "Etapas base para leads y oportunidades comerciales.",
        "stages": [
            ("NEW", "Nuevo", "#64748b", 10, False),
            ("CONTACTED", "Contactado", "#2563eb", 20, False),
            ("PROPOSAL", "Propuesta", "#7c3aed", 30, False),
            ("NEGOTIATION", "Negociacion", "#f59e0b", 40, False),
            ("WON", "Ganado", "#16a34a", 50, True),
            ("LOST", "Perdido", "#dc2626", 60, True),
        ],
    },
}

DEMO_TENANTS = [
    {
        "slug": "andina-servicios-financieros",
        "name": "Andina Servicios Financieros S.A.S.",
        "document_number": "900900001-1",
        "plan": "business",
        "modules": {"core", "administration", "crm", "collections", "legal", "documents", "bi", "sales", "telephony", "integrations"},
        "primary_color": "#15956f",
        "secondary_color": "#2563eb",
        "notes": "Tenant ficticio principal para demo comercial Collection & Legal CRM.",
    },
    {
        "slug": "legal-recovery-group-demo",
        "name": "Legal Recovery Group Demo",
        "document_number": "900900002-2",
        "plan": "professional",
        "modules": {"core", "administration", "legal", "documents", "bi", "telephony"},
        "primary_color": "#235f74",
        "secondary_color": "#7c3aed",
        "notes": "Firma juridica ficticia para mostrar expedientes y documentos.",
    },
    {
        "slug": "cooperativa-horizonte-demo",
        "name": "Cooperativa Horizonte Demo",
        "document_number": "900900003-3",
        "plan": "starter",
        "modules": {"core", "administration", "crm", "collections", "bi", "telephony"},
        "primary_color": "#15803d",
        "secondary_color": "#0f766e",
        "notes": "Cooperativa ficticia para mostrar cobranzas en plan Starter.",
    },
]

ANDINA_PROJECTS = [
    ("BANCO-FERIAS-CONSUMO", "Banco Ferias - Consumo Castigado", "Cartera de consumo castigado con saldos medios y mora avanzada.", 20),
    ("COOP-FUTURO-MICRO", "Cooperativa Futuro - Microcredito", "Microcredito productivo con seguimiento preventivo y correctivo.", 15),
    ("RETAIL-HOGAR-TARJETA", "Retail Hogar - Tarjeta Privada", "Tarjeta privada retail con promesas recurrentes.", 15),
    ("CARTERA-JUDICIALIZADA", "Cartera Judicializada - Recuperacion Legal", "Expedientes prejuridicos y juridicos con control documental.", 10),
]

SECONDARY_PROJECTS = {
    "legal-recovery-group-demo": [
        ("LEGAL-DEMO-EXP", "Expedientes Judiciales Demo", "Gestion de casos juridicos y vencimientos procesales."),
        ("LEGAL-DEMO-DOC", "Control Documental Legal", "Repositorio documental para procesos juridicos."),
    ],
    "cooperativa-horizonte-demo": [
        ("HORIZONTE-MICRO", "Microcredito Horizonte Demo", "Cartera de microcredito con recaudo operativo."),
    ],
}

DEMO_USER_DEFS = [
    ("superadmin@demo.icodeup.local", "SuperAdmin Icodeup Demo", PLATFORM_ADMIN, "Gobierno SaaS Icodeup", None),
    ("admin.andina@demo.icodeup.local", "Admin Empresa Andina", TENANT_ADMIN, "Administracion empresa", None),
    ("coord.cobranzas.andina@demo.icodeup.local", "Coordinador de Cobranzas", COORDINATOR, "Lider operativo cobranzas", None),
    ("gestor1.andina@demo.icodeup.local", "Gestor Demo Uno", AGENT, "Gestor de cartera", "coord.cobranzas.andina@demo.icodeup.local"),
    ("gestor2.andina@demo.icodeup.local", "Gestor Demo Dos", AGENT, "Gestor de cartera", "coord.cobranzas.andina@demo.icodeup.local"),
    ("calidad.andina@demo.icodeup.local", "Supervisor Calidad Demo", QUALITY_SUPERVISOR, "Supervisor de calidad", "coord.cobranzas.andina@demo.icodeup.local"),
    ("abogado.andina@demo.icodeup.local", "Abogado Juridico Demo", AGENT, "Abogado juridico", "admin.andina@demo.icodeup.local"),
    ("comercial.andina@demo.icodeup.local", "Analista Comercial Demo", AGENT, "Analista comercial", "admin.andina@demo.icodeup.local"),
]

DEMO_NAMES = [
    "Cliente Demo Aurora", "Cliente Demo Boreal", "Cliente Demo Camino", "Cliente Demo Delta", "Cliente Demo Eclipse",
    "Cliente Demo Farallones", "Cliente Demo Galeria", "Cliente Demo Horizonte", "Cliente Demo Indigo", "Cliente Demo Jardin",
    "Cliente Demo Kpital", "Cliente Demo Laguna", "Cliente Demo Monteluz", "Cliente Demo Norte", "Cliente Demo Origen",
    "Cliente Demo Paraiso", "Cliente Demo Quimbaya", "Cliente Demo Roble", "Cliente Demo Sabana", "Cliente Demo Terra",
]

DEMO_CITIES = ["Bogota", "Medellin", "Cali", "Barranquilla", "Bucaramanga", "Pereira", "Manizales", "Cartagena"]

PILOT_TENANT_DEF = {
    "slug": "icodeup-advisors",
    "name": "Icodeup Advisors",
    "document_number": "900360001-1",
    "plan": "business",
    "modules": {"core", "administration", "crm", "collections", "legal", "documents", "bi", "sales", "telephony", "integrations"},
    "primary_color": "#15956f",
    "secondary_color": "#2563eb",
    "notes": "Tenant piloto local ficticio para QA interno de Icodeup 360 Collection CRM.",
}

PILOT_PROJECTS = [
    ("PILOTO-CONSUMO", "Cartera Consumo Piloto", "Cartera ficticia de consumo para validacion local.", 120),
    ("PILOTO-PREVENTIVA", "Cartera Preventiva Piloto", "Cartera ficticia preventiva con mora temprana.", 90),
    ("PILOTO-JURIDICA", "Cartera Juridica Piloto", "Cartera ficticia prejuridica y juridica.", 90),
]

PILOT_USER_DEFS = [
    ("admin.icodeup@demo.icodeup.local", "Admin Icodeup Advisors Piloto", TENANT_ADMIN, "Administrador tenant piloto", None, "tenant_admin"),
    ("lider.cobranzas.icodeup@demo.icodeup.local", "Lider Cobranzas Icodeup Piloto", COORDINATOR, "Lider de cobranzas piloto", None, "collections_leader"),
    ("gestor1.icodeup@demo.icodeup.local", "Gestor Uno Icodeup Piloto", AGENT, "Gestor piloto", "lider.cobranzas.icodeup@demo.icodeup.local", "collections_agent"),
    ("gestor2.icodeup@demo.icodeup.local", "Gestor Dos Icodeup Piloto", AGENT, "Gestor piloto", "lider.cobranzas.icodeup@demo.icodeup.local", "collections_agent"),
    ("gestor3.icodeup@demo.icodeup.local", "Gestor Tres Icodeup Piloto", AGENT, "Gestor piloto", "lider.cobranzas.icodeup@demo.icodeup.local", "collections_agent"),
    ("gestor4.icodeup@demo.icodeup.local", "Gestor Cuatro Icodeup Piloto", AGENT, "Gestor piloto", "lider.cobranzas.icodeup@demo.icodeup.local", "collections_agent"),
    ("gestor5.icodeup@demo.icodeup.local", "Gestor Cinco Icodeup Piloto", AGENT, "Gestor piloto", "lider.cobranzas.icodeup@demo.icodeup.local", "collections_agent"),
    ("calidad.icodeup@demo.icodeup.local", "Calidad Icodeup Piloto", QUALITY_SUPERVISOR, "Supervisor calidad piloto", "lider.cobranzas.icodeup@demo.icodeup.local", "tenant_auditor"),
    ("auditor.icodeup@demo.icodeup.local", "Auditor Icodeup Piloto", QUALITY_SUPERVISOR, "Auditor piloto", None, "tenant_auditor"),
    ("abogado.icodeup@demo.icodeup.local", "Abogado Icodeup Piloto", AGENT, "Abogado piloto", None, "lawyer"),
    ("comercial.icodeup@demo.icodeup.local", "Comercial Icodeup Piloto", AGENT, "Comercial piloto", None, "sales_advisor"),
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
        current_links = list(db.scalars(select(RolePermission).where(RolePermission.role_id == role.id)))
        target_permission_ids = {permissions[permission_code].id for permission_code in permission_codes}
        for link in current_links:
            if link.permission_id not in target_permission_ids:
                db.delete(link)
        existing = {item.permission_id for item in current_links if item.permission_id in target_permission_ids}
        for permission_code in permission_codes:
            permission = permissions[permission_code]
            if permission.id not in existing:
                db.add(RolePermission(role_id=role.id, permission_id=permission.id))
    return roles


def _replace_role_permissions(db: Session, role: Role, permission_codes: list[str]) -> None:
    permissions = list(db.scalars(select(Permission).where(Permission.code.in_(permission_codes)))) if permission_codes else []
    permission_by_code = {item.code: item for item in permissions}
    missing = sorted(set(permission_codes) - set(permission_by_code))
    if missing:
        raise RuntimeError(f"Permisos no encontrados para rol {role.code}: {', '.join(missing)}")
    current = list(db.scalars(select(RolePermission).where(RolePermission.role_id == role.id)))
    target_ids = {item.id for item in permissions}
    current_ids = {item.permission_id for item in current}
    for item in current:
        if item.permission_id not in target_ids:
            db.delete(item)
    for permission in permissions:
        if permission.id not in current_ids:
            db.add(RolePermission(role_id=role.id, permission_id=permission.id))


def _ensure_specialized_roles_for_tenant(db: Session, tenant: Tenant) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for code, definition in SPECIALIZED_ROLE_DEFS.items():
        role = db.scalar(select(Role).where(Role.tenant_id == tenant.id, Role.code == code))
        if role is None:
            role = Role(tenant_id=tenant.id, code=code, name=definition["name"], is_system_role=False)
            db.add(role)
            db.flush()
        role.name = definition["name"]
        role.description = definition["description"]
        role.is_active = True
        role.is_system_role = False
        _replace_role_permissions(db, role, list(definition["permissions"]))
        roles[code] = role
    return roles


def _assign_profile_role(db: Session, user: User, role: Role) -> None:
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if profile is None:
        profile = UserProfile(user_id=user.id, tenant_id=user.tenant_id)
        db.add(profile)
    profile.tenant_id = user.tenant_id
    profile.role_id = role.id
    profile.status = user.status
    profile.is_platform_admin = user.role == PLATFORM_ADMIN
    profile.is_company_admin = user.role == TENANT_ADMIN


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


def _seed_functional_configuration(db: Session, tenant: Tenant | None = None) -> None:
    tenant_id = tenant.id if tenant else None
    for module, catalog_type, code, label, color, order in CATALOG_DEFAULTS:
        item = db.scalar(
            select(FunctionalCatalog).where(
                FunctionalCatalog.tenant_id == tenant_id,
                FunctionalCatalog.module == module,
                FunctionalCatalog.catalog_type == catalog_type,
                FunctionalCatalog.code == code,
            )
        )
        if item is None:
            item = FunctionalCatalog(tenant_id=tenant_id, module=module, catalog_type=catalog_type, code=code, label=label)
            db.add(item)
        item.label = label
        item.color = color
        item.order = order
        item.is_system = tenant_id is None
        item.is_active = True
    for module, rule_type, code, name, condition_json, action_json, severity in BUSINESS_RULE_DEFAULTS:
        item = db.scalar(
            select(BusinessRule).where(
                BusinessRule.tenant_id == tenant_id,
                BusinessRule.module == module,
                BusinessRule.rule_type == rule_type,
                BusinessRule.code == code,
            )
        )
        if item is None:
            item = BusinessRule(tenant_id=tenant_id, module=module, rule_type=rule_type, code=code, name=name)
            db.add(item)
        item.name = name
        item.condition_json = condition_json
        item.action_json = action_json
        item.severity = severity
        item.is_active = True
    for module, code, name, condition_type, threshold_days, severity, target_role, message_template in ALERT_RULE_DEFAULTS:
        item = db.scalar(select(AlertRule).where(AlertRule.tenant_id == tenant_id, AlertRule.module == module, AlertRule.code == code))
        if item is None:
            item = AlertRule(tenant_id=tenant_id, module=module, code=code, name=name, condition_type=condition_type)
            db.add(item)
        item.name = name
        item.condition_type = condition_type
        item.threshold_days = threshold_days
        item.severity = severity
        item.target_role = target_role
        item.message_template = message_template
        item.is_active = True
    for module, definition in WORKFLOW_DEFAULTS.items():
        workflow = db.scalar(
            select(WorkflowDefinition).where(
                WorkflowDefinition.tenant_id == tenant_id,
                WorkflowDefinition.module == module,
                WorkflowDefinition.code == definition["code"],
            )
        )
        if workflow is None:
            workflow = WorkflowDefinition(tenant_id=tenant_id, module=module, code=definition["code"], name=definition["name"])
            db.add(workflow)
            db.flush()
        workflow.name = definition["name"]
        workflow.description = definition["description"]
        workflow.is_active = True
        for code, name, color, order, is_final in definition["stages"]:
            stage = db.scalar(select(WorkflowStage).where(WorkflowStage.workflow_id == workflow.id, WorkflowStage.code == code))
            if stage is None:
                stage = WorkflowStage(workflow_id=workflow.id, code=code, name=name)
                db.add(stage)
            stage.name = name
            stage.color = color
            stage.order = order
            stage.is_final = is_final
            stage.is_active = True
    db.flush()


def _get_or_create_demo_tenant(db: Session, tenant_def: dict) -> Tenant:
    tenant = db.scalar(select(Tenant).where(Tenant.slug == tenant_def["slug"]))
    if tenant is None:
        tenant = Tenant(name=tenant_def["name"], slug=tenant_def["slug"])
        db.add(tenant)
        db.flush()
    tenant.name = tenant_def["name"]
    tenant.tax_id = tenant_def["document_number"]
    tenant.document_type = "NIT"
    tenant.document_number = tenant_def["document_number"]
    tenant.status = "active"
    tenant.primary_color = tenant_def["primary_color"]
    tenant.secondary_color = tenant_def["secondary_color"]
    tenant.timezone = "America/Bogota"
    tenant.logo_url = "/assets/icodeup-logo.png"
    tenant.notes = tenant_def["notes"]
    return tenant


def _get_or_create_project(db: Session, tenant: Tenant, code: str, name: str, description: str) -> Project:
    project = db.scalar(select(Project).where(Project.tenant_id == tenant.id, Project.code == code))
    if project is None:
        project = Project(tenant_id=tenant.id, code=code, name=name)
        db.add(project)
        db.flush()
    project.name = name
    project.description = description
    project.status = "active"
    return project


def _get_or_create_demo_user(
    db: Session,
    tenant: Tenant,
    email: str,
    name: str,
    role: str,
    title: str,
    leader_email: str | None = None,
) -> User:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None:
        user = User(
            tenant_id=tenant.id,
            name=name,
            email=email.lower(),
            role=role,
            password_hash=hash_password(DEMO_PASSWORD),
        )
        db.add(user)
        db.flush()
    user.tenant_id = tenant.id
    user.name = name
    user.role = role
    user.title = title
    user.status = "active"
    user.phone = user.phone or f"300000{user.id:04d}"
    if leader_email:
        leader = db.scalar(select(User).where(User.email == leader_email.lower()))
        if leader is not None:
            user.leader_id = leader.id
    return user


def _ensure_assignment(db: Session, user: User, project: Project, role_in_project: str = "agent", is_active: bool = True) -> None:
    existing = db.scalar(
        select(UserProjectAssignment).where(
            UserProjectAssignment.user_id == user.id,
            UserProjectAssignment.project_id == project.id,
        )
    )
    if existing is None:
        existing = UserProjectAssignment(user_id=user.id, project_id=project.id)
        db.add(existing)
    existing.tenant_id = project.tenant_id
    existing.role_in_project = role_in_project
    existing.is_active = is_active


def _ensure_subscription(db: Session, tenant: Tenant, plan_code: str) -> None:
    plan = db.scalar(select(SaasPlan).where(SaasPlan.code == plan_code))
    if plan is None:
        return
    subscription = db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant.id))
    now = datetime.now(timezone.utc)
    if subscription is None:
        subscription = TenantSubscription(tenant_id=tenant.id, plan_id=plan.id, start_date=now)
        db.add(subscription)
    subscription.plan_id = plan.id
    subscription.status = "active"
    subscription.billing_cycle = "monthly"
    subscription.renewal_date = now + timedelta(days=30)
    subscription.notes = "Suscripcion ficticia de demostracion comercial."
    tenant.plan_id = plan.id


def _set_demo_modules(db: Session, tenant: Tenant, modules: dict[str, Module], enabled_codes: set[str]) -> None:
    for module_code, module in modules.items():
        tenant_module = db.scalar(
            select(TenantModule).where(TenantModule.tenant_id == tenant.id, TenantModule.module_code == module_code)
        )
        enabled = module_code in enabled_codes
        if tenant_module is None:
            tenant_module = TenantModule(tenant_id=tenant.id, module_code=module_code, module_id=module.id)
            db.add(tenant_module)
        tenant_module.module_id = module.id
        tenant_module.enabled = enabled
        tenant_module.is_enabled = enabled
        tenant_module.enabled_at = datetime.now(timezone.utc) if enabled and tenant_module.enabled_at is None else (tenant_module.enabled_at if enabled else None)
        tenant_module.configuration_json = '{"demo": true}' if enabled else None


def _ensure_channels(db: Session, tenant: Tenant, project: Project | None = None) -> None:
    channel_defs = [
        ("whatsapp", "Linea principal cobranzas demo", "3000000101", "WhatsApp Cloud API Demo"),
        ("email", "Correo cobranzas demo", "cobranzas@demo.icodeup.local", "SMTP Demo"),
        ("telephony", "Telefonia WebRTC demo", "sip:andina-demo@pbx.demo.local", "SIP/WebRTC Demo"),
    ]
    for kind, label, value, provider in channel_defs:
        channel = db.scalar(select(CommunicationChannel).where(CommunicationChannel.tenant_id == tenant.id, CommunicationChannel.kind == kind, CommunicationChannel.value == value))
        if channel is None:
            channel = CommunicationChannel(tenant_id=tenant.id, project_id=project.id if project else None, kind=kind, label=label, value=value)
            db.add(channel)
        channel.label = label
        channel.provider = provider
        channel.is_default = True
        channel.status = "active"
        channel.config_json = '{"demo": true, "real_provider_connected": false}'


def _ensure_typifications(db: Session, tenant: Tenant) -> dict[str, TypificationNode]:
    tree = [
        ("CONTACTO", "Contacto efectivo", None, "Contactado", False, False, "phone", 10),
        ("PROMESA", "Promesa de pago", "CONTACTO", "Promesa", True, False, "whatsapp", 20),
        ("PAGO", "Pago confirmado", "CONTACTO", "Pago", False, True, "email", 30),
        ("NO_CONTACTO", "No contacto", None, "Sin contacto", False, False, "phone", 40),
        ("ESCALAR_JURIDICO", "Escalar a juridico", None, "Escalado", False, False, "email", 50),
        ("ACUERDO", "Acuerdo de pago", "CONTACTO", "Acuerdo", True, False, "phone", 60),
    ]
    nodes: dict[str, TypificationNode] = {}
    for code, label, parent_code, next_status, requires_promise, requires_payment, channel, sort_order in tree:
        node = db.scalar(select(TypificationNode).where(TypificationNode.tenant_id == tenant.id, TypificationNode.code == code))
        if node is None:
            node = TypificationNode(tenant_id=tenant.id, code=code, label=label)
            db.add(node)
            db.flush()
        node.label = label
        node.next_status = next_status
        node.requires_promise = requires_promise
        node.requires_payment = requires_payment
        node.channel = channel
        node.sort_order = sort_order
        node.parent_id = nodes[parent_code].id if parent_code and parent_code in nodes else None
        nodes[code] = node
    return nodes


def _ensure_party_for_customer(db: Session, tenant: Tenant, customer: Customer) -> None:
    party = db.scalar(
        select(Party).where(
            Party.tenant_id == tenant.id,
            Party.document_type == "CC-DEMO",
            Party.document_number == customer.document,
        )
    )
    if party is None:
        party = Party(tenant_id=tenant.id, party_type="person", document_type="CC-DEMO", document_number=customer.document)
        db.add(party)
    party.display_name = customer.name
    party.legal_name = customer.name
    party.email = customer.email
    party.phone = customer.phone
    party.city = customer.city
    party.status = "active"
    party.is_customer = True
    party.is_debtor = True
    party.external_ref = f"DEMO-CUSTOMER-{customer.document}"
    party.notes = "Tercero maestro ficticio generado para demo comercial."


def _ensure_customer(
    db: Session,
    tenant: Tenant,
    project: Project,
    assigned_user: User,
    index: int,
    segment: str,
    judicialized: bool = False,
) -> Customer:
    document = f"9001{index:05d}"
    customer = db.scalar(select(Customer).where(Customer.tenant_id == tenant.id, Customer.document == document))
    if customer is None:
        customer = Customer(tenant_id=tenant.id, document=document, name=f"{DEMO_NAMES[index % len(DEMO_NAMES)]} {index:03d}")
        db.add(customer)
        db.flush()
    dpd = (index * 7) % 125 + (90 if judicialized else 0)
    balance = 780000 + (index * 365000)
    customer.project_id = project.id
    customer.assigned_user_id = assigned_user.id
    customer.name = f"{DEMO_NAMES[index % len(DEMO_NAMES)]} {index:03d}"
    customer.phone = f"3000{index:06d}"
    customer.email = f"cliente.demo{index:03d}@demo.local"
    customer.city = DEMO_CITIES[index % len(DEMO_CITIES)]
    customer.segment = segment
    customer.obligation = f"OBL-DEMO-{project.code}-{index:03d}"
    customer.balance = balance
    customer.original_balance = balance + 450000
    customer.dpd = dpd
    customer.risk = "Alto" if dpd >= 75 else "Medio" if dpd >= 25 else "Bajo"
    customer.priority = min(100, int(dpd * 0.55) + int(balance / 1_000_000))
    customer.status = "Escalado" if judicialized else ("Promesa" if index % 4 == 0 else "Contactado" if index % 3 == 0 else "Sin contacto")
    customer.next_action = "Revisar expediente juridico" if judicialized else ("Confirmar promesa de pago" if index % 4 == 0 else "Gestion telefonica prioritaria")
    customer.contactability = "Alta" if index % 3 == 0 else "Media" if index % 3 == 1 else "Baja"
    customer.notes = "Registro ficticio para demo comercial Icodeup 360. No corresponde a persona real."
    customer.last_contact_at = datetime.now(timezone.utc) - timedelta(days=index % 11)
    customer.next_contact_at = datetime.now(timezone.utc) + timedelta(days=(index % 5) + 1)
    _ensure_party_for_customer(db, tenant, customer)
    return customer


def _ensure_customer_obligations(db: Session, customer: Customer, leader: User | None = None) -> list[CustomerObligation]:
    count = 1 + (customer.id % 3)
    obligations: list[CustomerObligation] = []
    remaining_balance = customer.balance
    product_types = ["Consumo", "Microcredito", "Tarjeta privada", "Judicializada"]
    for position in range(1, count + 1):
        number = f"{customer.obligation or 'OBL-DEMO'}-{position}"
        item = db.scalar(select(CustomerObligation).where(CustomerObligation.tenant_id == customer.tenant_id, CustomerObligation.obligation_number == number))
        if item is None:
            item = CustomerObligation(tenant_id=customer.tenant_id, customer_id=customer.id, obligation_number=number)
            db.add(item)
            db.flush()
        share = max(150000, int(remaining_balance / (count - position + 1)))
        remaining_balance -= share
        item.project_id = customer.project_id
        item.customer_id = customer.id
        item.product_type = product_types[(customer.id + position) % len(product_types)]
        item.portfolio_name = customer.segment or "Cartera demo"
        item.purchase_number = f"COMPRA-DEMO-{customer.project_id or 0}-{position:02d}"
        item.original_amount = share + 250000
        item.current_balance = share
        item.capital_amount = int(share * 0.74)
        item.interest_amount = int(share * 0.19)
        item.fees_amount = share - (item.capital_amount or 0) - (item.interest_amount or 0)
        item.days_past_due = max(0, customer.dpd - ((position - 1) * 12))
        item.status = "judicializada" if customer.status == "Escalado" else "active"
        item.risk = "Alto" if item.days_past_due >= 75 else "Medio" if item.days_past_due >= 25 else "Bajo"
        item.assigned_user_id = customer.assigned_user_id
        item.assigned_leader_id = leader.id if leader else None
        item.metadata_json = json.dumps({"demo": True, "source": "bootstrap_operativo", "summary_from_customer": customer.id})
        obligations.append(item)
    return obligations


def _ensure_operational_sheet_rows(db: Session, tenant: Tenant, customers: list[Customer], users_by_id: dict[int, User]) -> None:
    statuses = ["Pendiente", "Seguimiento", "Gestionado", "Pagos", "Cerrado"]
    for index, customer in enumerate(customers[:24], start=1):
        owner = users_by_id.get(customer.assigned_user_id or 0)
        if owner is None:
            continue
        obligation = db.scalar(select(CustomerObligation).where(CustomerObligation.customer_id == customer.id).order_by(CustomerObligation.id))
        obligation_number = obligation.obligation_number if obligation else customer.obligation
        commitment = f"Seguimiento demo hoja operativa {index:02d}"
        row = db.scalar(
            select(OperationalSheetRow).where(
                OperationalSheetRow.tenant_id == tenant.id,
                OperationalSheetRow.user_id == owner.id,
                OperationalSheetRow.document == customer.document,
                OperationalSheetRow.obligation_number == obligation_number,
                OperationalSheetRow.commitment == commitment,
            )
        )
        if row is None:
            row = OperationalSheetRow(tenant_id=tenant.id, user_id=owner.id, document=customer.document, obligation_number=obligation_number, commitment=commitment)
            db.add(row)
        row.project_id = customer.project_id
        row.customer_id = customer.id
        row.obligation_id = obligation.id if obligation else None
        row.date = (datetime.now(timezone.utc) - timedelta(days=index % 6)).date()
        row.portfolio = customer.segment or "Cartera demo"
        row.customer_name = customer.name
        row.management_note = "Registro ficticio de seguimiento para demo operacional."
        row.amount = max(120000, int((obligation.current_balance if obligation else customer.balance) * (0.08 + (index % 4) * 0.03)))
        row.status = statuses[index % len(statuses)]
        row.next_action_at = datetime.now(timezone.utc) + timedelta(days=(index % 7) + 1)
        row.metadata_json = json.dumps({"demo": True, "source": "bootstrap_excel_web_operativo", "customer_id": customer.id})


def _first_customer_obligation(db: Session, customer: Customer) -> CustomerObligation | None:
    return db.scalar(select(CustomerObligation).where(CustomerObligation.customer_id == customer.id).order_by(CustomerObligation.id))


def _ensure_activity(db: Session, customer: Customer, user: User, typification: TypificationNode | None, channel: str, result: str, note: str, days_ago: int) -> None:
    obligation = _first_customer_obligation(db, customer)
    existing = db.scalar(select(ManagementActivity).where(ManagementActivity.customer_id == customer.id, ManagementActivity.note == note))
    if existing is None:
        db.add(
            ManagementActivity(
                tenant_id=customer.tenant_id,
                project_id=customer.project_id,
                customer_id=customer.id,
                obligation_id=obligation.id if obligation else None,
                user_id=user.id,
                typification_id=typification.id if typification else None,
                channel=channel,
                result=result,
                note=note,
                next_contact_at=datetime.now(timezone.utc) + timedelta(days=2),
                created_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
            )
        )
    elif obligation and existing.obligation_id is None:
        existing.obligation_id = obligation.id


def _ensure_promise(db: Session, customer: Customer, user: User, amount: int, due_in_days: int, status: str) -> None:
    obligation = _first_customer_obligation(db, customer)
    existing = db.scalar(select(PaymentPromise).where(PaymentPromise.customer_id == customer.id, PaymentPromise.amount == amount, PaymentPromise.status == status))
    if existing is None:
        db.add(
            PaymentPromise(
                tenant_id=customer.tenant_id,
                project_id=customer.project_id,
                customer_id=customer.id,
                obligation_id=obligation.id if obligation else None,
                user_id=user.id,
                amount=amount,
                due_date=datetime.now(timezone.utc) + timedelta(days=due_in_days),
                channel="whatsapp",
                status=status,
            )
        )
    elif obligation and existing.obligation_id is None:
        existing.obligation_id = obligation.id


def _ensure_payment(db: Session, customer: Customer, user: User, amount: int, days_ago: int) -> None:
    reference = f"DEMO-PAGO-{customer.document}-{amount}"
    existing = db.scalar(select(Payment).where(Payment.tenant_id == customer.tenant_id, Payment.reference == reference))
    if existing is None:
        db.add(
            Payment(
                tenant_id=customer.tenant_id,
                project_id=customer.project_id,
                customer_id=customer.id,
                user_id=user.id,
                amount=amount,
                paid_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
                method="Transferencia demo",
                reference=reference,
            )
        )


def _ensure_agreement(db: Session, customer: Customer, user: User, installments: int, total_amount: int, status: str) -> PaymentAgreement:
    obligation = _first_customer_obligation(db, customer)
    note = f"DEMO-ACUERDO-{customer.document}"
    agreement = db.scalar(select(PaymentAgreement).where(PaymentAgreement.customer_id == customer.id, PaymentAgreement.notes == note))
    if agreement is None:
        agreement = PaymentAgreement(
            tenant_id=customer.tenant_id,
            project_id=customer.project_id,
            customer_id=customer.id,
            obligation_id=obligation.id if obligation else None,
            user_id=user.id,
            total_amount=total_amount,
            installment_count=installments,
            start_date=datetime.now(timezone.utc) - timedelta(days=7),
            status=status,
            notes=note,
        )
        db.add(agreement)
        db.flush()
    elif obligation and agreement.obligation_id is None:
        agreement.obligation_id = obligation.id
    agreement.status = status
    existing_installments = list(db.scalars(select(PaymentAgreementInstallment).where(PaymentAgreementInstallment.agreement_id == agreement.id)))
    if not existing_installments:
        amount = max(1, int(total_amount / installments))
        for item in range(installments):
            paid_amount = amount if item == 0 and status in {"active", "partial", "completed"} else 0
            db.add(
                PaymentAgreementInstallment(
                    agreement_id=agreement.id,
                    due_date=datetime.now(timezone.utc) + timedelta(days=(item + 1) * 15),
                    amount=amount,
                    paid_amount=paid_amount,
                    status="paid" if paid_amount else ("overdue" if item == 1 and status == "overdue" else "pending"),
                )
            )
    return agreement


def _ensure_document(
    db: Session,
    tenant: Tenant,
    user: User,
    document_type: str,
    original_name: str,
    storage_path: str,
    project_id: int | None = None,
    customer_id: int | None = None,
    legal_case_id: int | None = None,
    agreement_id: int | None = None,
    payment_id: int | None = None,
) -> None:
    document = db.scalar(select(Document).where(Document.tenant_id == tenant.id, Document.storage_path == storage_path))
    if document is None:
        document = Document(tenant_id=tenant.id, storage_path=storage_path, uploaded_by_id=user.id, document_type=document_type, original_name=original_name)
        db.add(document)
    document.project_id = project_id
    document.customer_id = customer_id
    document.legal_case_id = legal_case_id
    document.agreement_id = agreement_id
    document.payment_id = payment_id
    document.mime_type = "application/pdf"
    document.size_bytes = 256000
    document.status = "active"
    document.notes = "Metadato documental ficticio. No existe archivo real asociado en el repositorio."


def _ensure_legal_case(db: Session, tenant: Tenant, customer: Customer, lawyer: User, index: int) -> LegalCase:
    case_number = f"DEMO-LEGAL-{index:03d}"
    legal_case = db.scalar(select(LegalCase).where(LegalCase.tenant_id == tenant.id, LegalCase.case_number == case_number))
    if legal_case is None:
        legal_case = LegalCase(
            tenant_id=tenant.id,
            project_id=customer.project_id,
            customer_id=customer.id,
            case_number=case_number,
            process_type="Ejecutivo singular demo",
        )
        db.add(legal_case)
        db.flush()
    legal_case.assigned_lawyer_id = lawyer.id
    legal_case.court_name = f"Juzgado Demo {index:02d}"
    legal_case.amount = customer.balance
    legal_case.status = "open" if index % 5 else "closed"
    legal_case.stage = ["Recibido", "En estudio", "Radicado", "En tramite", "Audiencia programada"][index % 5]
    legal_case.risk = "high" if customer.dpd > 120 else "medium"
    legal_case.next_action = "Preparar actuacion juridica demo"
    legal_case.next_deadline_at = datetime.now(timezone.utc) + timedelta(days=(index % 12) + 3)
    legal_case.notes = "Caso juridico ficticio para demostracion comercial."
    actions = [
        ("Revision documental", "Validacion de pagare y contrato demo."),
        ("Radicacion", "Radicacion ficticia de demanda demo."),
        ("Seguimiento", "Control de termino procesal demo."),
    ]
    for offset, (action_type, description) in enumerate(actions):
        existing = db.scalar(select(LegalAction).where(LegalAction.legal_case_id == legal_case.id, LegalAction.action_type == action_type))
        if existing is None:
            db.add(
                LegalAction(
                    tenant_id=tenant.id,
                    legal_case_id=legal_case.id,
                    user_id=lawyer.id,
                    action_type=action_type,
                    description=description,
                    action_date=datetime.now(timezone.utc) - timedelta(days=offset + 1),
                    next_deadline_at=datetime.now(timezone.utc) + timedelta(days=offset + 7),
                )
            )
    hearing = db.scalar(select(LegalHearing).where(LegalHearing.legal_case_id == legal_case.id, LegalHearing.hearing_type == "Audiencia demo"))
    if hearing is None:
        db.add(
            LegalHearing(
                tenant_id=tenant.id,
                legal_case_id=legal_case.id,
                hearing_type="Audiencia demo",
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=20 + index),
                location="Sala virtual demo",
                status="scheduled",
                notes="Audiencia ficticia para flujo comercial.",
            )
        )
    deadline = db.scalar(select(LegalDeadline).where(LegalDeadline.legal_case_id == legal_case.id, LegalDeadline.title == "Vencimiento procesal demo"))
    if deadline is None:
        db.add(
            LegalDeadline(
                tenant_id=tenant.id,
                legal_case_id=legal_case.id,
                title="Vencimiento procesal demo",
                due_at=datetime.now(timezone.utc) + timedelta(days=(index % 15) + 2),
                status="open",
                priority="high" if index % 2 == 0 else "medium",
            )
        )
    return legal_case


def _ensure_sales_demo(db: Session, tenant: Tenant, project: Project, owner: User) -> None:
    lead_defs = [
        ("BPO Andes Demo", "bpo-andes@demo.local", "BPO de cobranzas", "Propuesta", "proposal", 65, "open"),
        ("Fintech Prisma Demo", "fintech-prisma@demo.local", "Fintech", "Negociacion", "negotiation", 55, "open"),
        ("Cooperativa Norte Demo", "cooperativa-norte@demo.local", "Cooperativa", "Ganada", "closed_won", 100, "won"),
        ("Retail Nova Demo", "retail-nova@demo.local", "Retail", "Perdida", "closed_lost", 0, "lost"),
        ("Firma Legal Beta Demo", "legal-beta@demo.local", "Firma juridica", "Calificacion", "qualification", 35, "open"),
        ("Servicios Omega Demo", "servicios-omega@demo.local", "Servicios", "Contacto", "discovery", 25, "open"),
    ]
    for idx, (company, email, interest, status, stage, probability, opportunity_status) in enumerate(lead_defs, start=1):
        lead = db.scalar(select(Lead).where(Lead.tenant_id == tenant.id, Lead.email == email))
        if lead is None:
            lead = Lead(tenant_id=tenant.id, email=email, name=f"Contacto Demo {idx:02d}")
            db.add(lead)
            db.flush()
        lead.project_id = project.id
        lead.assigned_user_id = owner.id
        lead.company = company
        lead.document = f"9100{idx:05d}"
        lead.phone = f"3001{idx:06d}"
        lead.source = "Demo comercial"
        lead.interest = interest
        lead.status = status.lower().replace(" ", "_")
        lead.priority = "high" if probability >= 55 else "medium"
        lead.notes = "Lead ficticio para mostrar evolucion CRM 360."
        opportunity = db.scalar(select(Opportunity).where(Opportunity.tenant_id == tenant.id, Opportunity.lead_id == lead.id))
        if opportunity is None:
            opportunity = Opportunity(tenant_id=tenant.id, lead_id=lead.id, name=f"Icodeup 360 - {company}")
            db.add(opportunity)
        opportunity.project_id = project.id
        opportunity.assigned_user_id = owner.id
        opportunity.amount = 8_000_000 + (idx * 1_500_000)
        opportunity.stage = stage
        opportunity.probability = probability
        opportunity.expected_close_date = datetime.now(timezone.utc) + timedelta(days=20 + idx)
        opportunity.status = opportunity_status
        opportunity.lost_reason = "No aplica en demo" if opportunity_status != "lost" else "Presupuesto aplazado demo"
        opportunity.notes = "Oportunidad ficticia para demo comercial."


def _ensure_pilot_customer(db: Session, tenant: Tenant, project: Project, assigned_user: User, index: int, segment: str) -> Customer:
    document = f"9903{index:05d}"
    customer = db.scalar(select(Customer).where(Customer.tenant_id == tenant.id, Customer.document == document))
    if customer is None:
        customer = Customer(tenant_id=tenant.id, document=document, name=f"Cliente Piloto Icodeup {index:03d}")
        db.add(customer)
        db.flush()
    if project.code == "PILOTO-PREVENTIVA":
        dpd = (index * 3) % 45
    elif project.code == "PILOTO-JURIDICA":
        dpd = 90 + ((index * 5) % 160)
    else:
        dpd = 25 + ((index * 7) % 120)
    balance = 650000 + ((index % 60) * 135000) + (index * 17500)
    customer.project_id = project.id
    customer.assigned_user_id = assigned_user.id
    customer.name = f"Cliente Piloto Icodeup {index:03d}"
    customer.phone = f"3009{index:06d}"
    customer.email = f"cliente.piloto{index:03d}@demo.icodeup.local"
    customer.city = DEMO_CITIES[index % len(DEMO_CITIES)]
    customer.segment = segment
    customer.obligation = f"PILOT-{project.code}-{index:03d}"
    customer.balance = balance
    customer.original_balance = balance + 380000
    customer.dpd = dpd
    customer.risk = "Alto" if dpd >= 75 else "Medio" if dpd >= 25 else "Bajo"
    customer.priority = min(100, int(dpd * 0.6) + int(balance / 1_200_000))
    customer.status = "Escalado" if project.code == "PILOTO-JURIDICA" and index % 3 == 0 else ("Promesa" if index % 5 == 0 else "Contactado" if index % 2 == 0 else "Sin contacto")
    customer.next_action = "Revisar ruta juridica piloto" if customer.status == "Escalado" else ("Confirmar compromiso piloto" if customer.status == "Promesa" else "Gestionar contacto piloto")
    customer.contactability = "Alta" if index % 4 == 0 else "Media" if index % 4 in {1, 2} else "Baja"
    customer.notes = "Registro ficticio del piloto local Icodeup Advisors. No corresponde a una persona real."
    customer.last_contact_at = datetime.now(timezone.utc) - timedelta(days=index % 12)
    customer.next_contact_at = datetime.now(timezone.utc) + timedelta(days=(index % 6) + 1)
    _ensure_party_for_customer(db, tenant, customer)
    return customer


def _ensure_pilot_obligation(db: Session, customer: Customer, leader: User, position: int) -> CustomerObligation:
    number = f"PILOT-OBL-{customer.document}-{position:02d}"
    item = db.scalar(select(CustomerObligation).where(CustomerObligation.tenant_id == customer.tenant_id, CustomerObligation.obligation_number == number))
    if item is None:
        item = CustomerObligation(tenant_id=customer.tenant_id, customer_id=customer.id, obligation_number=number)
        db.add(item)
        db.flush()
    divisor = 2 if position == 1 and customer.balance > 1_000_000 else 3
    current_balance = max(180000, int(customer.balance / divisor) + (position * 55000))
    item.project_id = customer.project_id
    item.customer_id = customer.id
    item.product_type = ["Consumo", "Preventiva", "Tarjeta", "Juridica"][position % 4]
    item.portfolio_name = customer.segment or "Piloto Icodeup"
    item.purchase_number = f"PILOT-COMPRA-{customer.project_id}-{position:02d}"
    item.original_amount = current_balance + 240000
    item.current_balance = current_balance
    item.capital_amount = int(current_balance * 0.72)
    item.interest_amount = int(current_balance * 0.2)
    item.fees_amount = current_balance - (item.capital_amount or 0) - (item.interest_amount or 0)
    item.days_past_due = max(0, customer.dpd - ((position - 1) * 9))
    item.status = "judicializada" if customer.status == "Escalado" else "active"
    item.risk = "Alto" if item.days_past_due >= 75 else "Medio" if item.days_past_due >= 25 else "Bajo"
    item.assigned_user_id = customer.assigned_user_id
    item.assigned_leader_id = leader.id
    item.metadata_json = json.dumps({"demo": True, "pilot": "icodeup_advisors", "source": "seed_pilot_icodeup_advisors"})
    return item


def _ensure_pilot_demographic(db: Session, tenant: Tenant, customer: Customer, index: int) -> None:
    demographic = db.scalar(select(CustomerDemographic).where(CustomerDemographic.tenant_id == tenant.id, CustomerDemographic.customer_id == customer.id, CustomerDemographic.source == "PILOTO_ICODEUP"))
    if demographic is None:
        demographic = CustomerDemographic(tenant_id=tenant.id, customer_id=customer.id, source="PILOTO_ICODEUP")
        db.add(demographic)
    demographic.phone = f"3019{index:06d}"
    demographic.email = f"demografico.piloto{index:03d}@demo.icodeup.local"
    demographic.address = f"Carrera Piloto {index:03d} # 36-00"
    demographic.city = customer.city
    demographic.state = "Departamento Piloto"
    demographic.employer = f"Empresa Piloto {index:03d}"
    demographic.job_title = "Cargo piloto"
    demographic.reference_name = f"Referencia Piloto {index:03d}"
    demographic.reference_phone = f"3029{index:06d}"
    demographic.score = 55 + (index % 40)
    demographic.metadata_json = json.dumps({"demo": True, "pilot": "icodeup_advisors", "contactability": customer.contactability})
    demographic.is_active = True


def _ensure_pilot_upload_batch(db: Session, tenant: Tenant, project: Project, user: User, upload_type: str, filename: str, total: int, created: int, reparto: bool = False) -> None:
    batch = db.scalar(select(UploadBatch).where(UploadBatch.tenant_id == tenant.id, UploadBatch.original_filename == filename))
    if batch is None:
        batch = UploadBatch(tenant_id=tenant.id, project_id=project.id, uploaded_by_id=user.id, upload_type=upload_type, original_filename=filename)
        db.add(batch)
    batch.project_id = project.id
    batch.uploaded_by_id = user.id
    batch.upload_type = upload_type
    batch.status = "completed"
    batch.total_rows = total
    batch.valid_rows = total
    batch.error_rows = 0
    batch.created_rows = created
    batch.updated_rows = 0
    batch.result_file_path = f"tenants/piloto/icodeup-advisors/uploads/{filename}"
    batch.summary_json = json.dumps({"demo": True, "pilot": "icodeup_advisors", "reparto": reparto, "file_is_metadata_only": True})


def seed_pilot_icodeup_advisors(db: Session, modules: dict[str, Module], roles: dict[str, Role]) -> None:
    tenant = _get_or_create_demo_tenant(db, PILOT_TENANT_DEF)
    _ensure_subscription(db, tenant, PILOT_TENANT_DEF["plan"])
    _set_demo_modules(db, tenant, modules, PILOT_TENANT_DEF["modules"])
    _seed_tenant_configuration(db, tenant)
    _seed_functional_configuration(db, tenant)

    users: dict[str, User] = {}
    for email, name, legacy_role, title, leader_email, _profile_code in PILOT_USER_DEFS:
        users[email] = _get_or_create_demo_user(db, tenant, email, name, legacy_role, title, leader_email)

    specialized_roles = _ensure_specialized_roles_for_tenant(db, tenant)
    for email, _name, legacy_role, _title, _leader_email, profile_code in PILOT_USER_DEFS:
        role = specialized_roles.get(profile_code) or roles[legacy_role]
        _assign_profile_role(db, users[email], role)

    projects = [
        _get_or_create_project(db, tenant, code, name, description)
        for code, name, description, _count in PILOT_PROJECTS
    ]
    for project in projects:
        for email, user in users.items():
            if email.startswith("admin."):
                role_in_project = "admin"
            elif email.startswith("lider."):
                role_in_project = "leader"
            elif email.startswith("gestor"):
                role_in_project = "agent"
            elif email.startswith("calidad") or email.startswith("auditor"):
                role_in_project = "quality"
            elif email.startswith("abogado"):
                role_in_project = "lawyer"
            elif email.startswith("comercial"):
                role_in_project = "sales"
            else:
                role_in_project = "viewer"
            _ensure_assignment(db, user, project, role_in_project)

    admin = users["admin.icodeup@demo.icodeup.local"]
    leader = users["lider.cobranzas.icodeup@demo.icodeup.local"]
    lawyer = users["abogado.icodeup@demo.icodeup.local"]
    commercial = users["comercial.icodeup@demo.icodeup.local"]
    agents = [users[f"gestor{idx}.icodeup@demo.icodeup.local"] for idx in range(1, 6)]
    _ensure_channels(db, tenant, projects[0])
    typifications = _ensure_typifications(db, tenant)

    customers: list[Customer] = []
    global_index = 1
    for project_idx, (project_code, _name, _description, count) in enumerate(PILOT_PROJECTS):
        project = next(item for item in projects if item.code == project_code)
        segment = ["Consumo Piloto", "Preventiva Piloto", "Juridica Piloto"][project_idx]
        for _ in range(count):
            assigned = agents[(global_index - 1) % len(agents)]
            customer = _ensure_pilot_customer(db, tenant, project, assigned, global_index, segment)
            _ensure_pilot_obligation(db, customer, leader, 1)
            if global_index <= 200:
                _ensure_pilot_obligation(db, customer, leader, 2)
            activity_code = "PROMESA" if global_index % 5 == 0 else "ESCALAR_JURIDICO" if project.code == "PILOTO-JURIDICA" and global_index % 7 == 0 else "CONTACTO" if global_index % 2 == 0 else "NO_CONTACTO"
            _ensure_activity(db, customer, assigned, typifications.get(activity_code), "phone" if activity_code != "ESCALAR_JURIDICO" else "email", "Gestion piloto", f"PILOTO ICODEUP gestion {customer.document}", global_index % 14)
            if global_index <= 50:
                _ensure_promise(db, customer, assigned, max(95000, int(customer.balance * 0.1)), 4 + (global_index % 10), "Vigente" if global_index <= 38 else "Vencida")
            if global_index <= 30:
                _ensure_payment(db, customer, assigned, max(85000, int(customer.balance * 0.06)), global_index % 12)
            if global_index <= 20:
                _ensure_agreement(db, customer, assigned, 4, max(320000, int(customer.balance * 0.35)), "active" if global_index % 5 else "overdue")
            if global_index <= 100:
                _ensure_pilot_demographic(db, tenant, customer, global_index)
            if project.code == "PILOTO-JURIDICA" and global_index % 9 == 0:
                _ensure_legal_case(db, tenant, customer, lawyer, 500 + global_index)
            customers.append(customer)
            global_index += 1

    _ensure_operational_sheet_rows(db, tenant, customers, {user.id: user for user in users.values()})
    _ensure_sales_demo(db, tenant, projects[0], commercial)
    _ensure_pilot_upload_batch(db, tenant, projects[0], admin, "reparto_cartera", "reparto_icodeup_piloto_consumo.csv", 120, 120, reparto=True)
    _ensure_pilot_upload_batch(db, tenant, projects[1], admin, "reparto_cartera", "reparto_icodeup_piloto_preventiva.csv", 90, 90, reparto=True)
    _ensure_pilot_upload_batch(db, tenant, projects[2], admin, "demograficos", "demograficos_icodeup_piloto.csv", 100, 100)
    event = db.scalar(select(ChannelEventLog).where(ChannelEventLog.tenant_id == tenant.id, ChannelEventLog.event_type == "pilot.seed.icodeup_advisors"))
    if event is None:
        db.add(ChannelEventLog(tenant_id=tenant.id, channel_type="system", event_type="pilot.seed.icodeup_advisors", status="simulated", payload_json=json.dumps({"demo": True, "pilot": "icodeup_advisors", "customers": 300, "obligations": 500})))


def _seed_phase8b_collection_demo(db: Session, tenant: Tenant, projects: list[Project], users: dict[str, User]) -> None:
    admin = users["admin.andina@demo.icodeup.local"]
    leader = users["coord.cobranzas.andina@demo.icodeup.local"]
    gestor_1 = users["gestor1.andina@demo.icodeup.local"]
    gestor_2 = users["gestor2.andina@demo.icodeup.local"]
    project = projects[0]

    tree = db.scalar(select(TypificationTree).where(TypificationTree.tenant_id == tenant.id, TypificationTree.code == "COBRANZA_ANDINA"))
    if tree is None:
        tree = TypificationTree(tenant_id=tenant.id, project_id=None, module="collections", code="COBRANZA_ANDINA", name="Arbol Cobranza Andina Demo")
        db.add(tree)
        db.flush()
    tree.description = "Arbol demo de combinaciones para cobranza administrativa, prejuridica y juridica."
    tree.status = "active"
    node_defs = [
        (None, 1, "CONTACTO_EFECTIVO", "Contacto efectivo", "#16a34a", 10, {"requires_comment": True}),
        (None, 1, "NO_CONTACTO", "No contacto", "#dc2626", 20, {"requires_next_action": True}),
        (None, 1, "TERCERO", "Contacto tercero", "#f59e0b", 30, {"requires_comment": True}),
        ("CONTACTO_EFECTIVO", 2, "PROMESA_PAGO", "Promesa de pago", "#2563eb", 10, {"requires_promise": True, "requires_amount": True, "requires_next_action": True, "target_customer_status": "Promesa", "changes_customer_status": True}),
        ("CONTACTO_EFECTIVO", 2, "ACUERDO", "Acuerdo de pago", "#7c3aed", 20, {"requires_amount": True, "requires_document": True, "target_customer_status": "Acuerdo", "changes_customer_status": True}),
        ("NO_CONTACTO", 2, "NUMERO_NO_EXISTE", "Numero no existe", "#dc2626", 10, {"generates_alert": True}),
        ("NO_CONTACTO", 2, "SIN_RESPUESTA", "Sin respuesta", "#f59e0b", 20, {"requires_next_action": True}),
        ("TERCERO", 2, "MENSAJE_DEJADO", "Mensaje dejado", "#f59e0b", 10, {"requires_next_action": True}),
        ("CONTACTO_EFECTIVO", 2, "ESCALAR_JURIDICO", "Escalar a juridico", "#991b1b", 30, {"escalates_to_legal": True, "requires_document": True}),
    ]
    nodes: dict[str, TypificationTreeNode] = {}
    for parent_code, level, code, label, color, order, flags in node_defs:
        node = db.scalar(select(TypificationTreeNode).where(TypificationTreeNode.tree_id == tree.id, TypificationTreeNode.code == code))
        if node is None:
            node = TypificationTreeNode(tree_id=tree.id, code=code, label=label)
            db.add(node)
            db.flush()
        nodes[code] = node
        node.parent_id = nodes[parent_code].id if parent_code else None
        node.level = level
        node.label = label
        node.color = color
        node.order = order
        node.is_active = True
        node.requires_comment = bool(flags.get("requires_comment"))
        node.requires_promise = bool(flags.get("requires_promise"))
        node.requires_next_action = bool(flags.get("requires_next_action"))
        node.requires_amount = bool(flags.get("requires_amount"))
        node.requires_document = bool(flags.get("requires_document"))
        node.changes_customer_status = bool(flags.get("changes_customer_status"))
        node.target_customer_status = flags.get("target_customer_status")
        node.generates_alert = bool(flags.get("generates_alert"))
        node.escalates_to_legal = bool(flags.get("escalates_to_legal"))
    combinations = [
        (["CONTACTO_EFECTIVO", "PROMESA_PAGO"], {"promise_amount": True, "promise_due_date": True, "note": True}, {"customer_status": "Promesa", "next_action": "Confirmar cumplimiento de promesa"}),
        (["CONTACTO_EFECTIVO", "ACUERDO"], {"amount": True, "document": True}, {"customer_status": "Acuerdo", "enable_agreement": True}),
        (["NO_CONTACTO", "NUMERO_NO_EXISTE"], {"next_contact_at": True}, {"generate_alert": True, "next_action": "Cruzar demograficos"}),
        (["CONTACTO_EFECTIVO", "ESCALAR_JURIDICO"], {"document": True, "note": True}, {"escalate_to_legal": True}),
    ]
    for path, required, effects in combinations:
        path_ids = [nodes[code].id for code in path if code in nodes]
        path_json = json.dumps(path_ids)
        rule = db.scalar(select(TypificationCombinationRule).where(TypificationCombinationRule.tree_id == tree.id, TypificationCombinationRule.path_json == path_json))
        if rule is None:
            rule = TypificationCombinationRule(tenant_id=tenant.id, project_id=None, tree_id=tree.id, path_json=path_json)
            db.add(rule)
        rule.required_fields_json = json.dumps(required)
        rule.effects_json = json.dumps(effects)
        rule.is_active = True

    customers = list(db.scalars(select(Customer).where(Customer.tenant_id == tenant.id).order_by(Customer.id).limit(60)))
    activities = list(db.scalars(select(ManagementActivity).where(ManagementActivity.tenant_id == tenant.id).order_by(ManagementActivity.id).limit(30)))
    for index, customer in enumerate(customers[:30], start=1):
        demographic = db.scalar(select(CustomerDemographic).where(CustomerDemographic.tenant_id == tenant.id, CustomerDemographic.customer_id == customer.id, CustomerDemographic.source == "DEMO_FASE_8B"))
        if demographic is None:
            demographic = CustomerDemographic(tenant_id=tenant.id, customer_id=customer.id, source="DEMO_FASE_8B")
            db.add(demographic)
        demographic.phone = f"3008{index:06d}"
        demographic.email = f"demografico{index:03d}@demo.local"
        demographic.address = f"Calle Demo {index:02d} # 8B-00"
        demographic.city = customer.city
        demographic.state = "Departamento Demo"
        demographic.employer = f"Empresa Demo {index:02d}"
        demographic.job_title = "Cargo demo"
        demographic.reference_name = f"Referencia Demo {index:02d}"
        demographic.reference_phone = f"3018{index:06d}"
        demographic.score = 60 + (index % 35)
        demographic.metadata_json = json.dumps({"demo": True, "contactabilidad": customer.contactability})
    for index, customer in enumerate(customers[:20], start=1):
        activity = activities[(index - 1) % len(activities)] if activities else None
        recording = db.scalar(select(CallRecording).where(CallRecording.tenant_id == tenant.id, CallRecording.call_id == f"CALL-DEMO-8B-{index:03d}"))
        if recording is None:
            recording = CallRecording(tenant_id=tenant.id, call_id=f"CALL-DEMO-8B-{index:03d}")
            db.add(recording)
        recording.project_id = customer.project_id
        recording.customer_id = customer.id
        recording.activity_id = activity.id if activity else None
        recording.user_id = customer.assigned_user_id or (gestor_1.id if index % 2 else gestor_2.id)
        recording.phone_number = customer.phone
        recording.direction = "outbound"
        recording.started_at = datetime.now(timezone.utc) - timedelta(days=index)
        recording.duration_seconds = 60 + (index * 13)
        recording.recording_url = None
        recording.storage_path = f"tenants/demo/andina/recordings/call_demo_8b_{index:03d}.mp3"
        recording.provider_code = "TRONCAL_DEMO_SIP_ANDINA"
        recording.status = "available"
        recording.metadata_json = json.dumps({"demo": True, "quality_score": 70 + (index % 25)})
    batch_defs = [
        ("reparto_cartera", "reparto_andina_demo_8b.csv", 60, 60, 0),
        ("demograficos", "demograficos_andina_demo_8b.csv", 30, 30, 0),
        ("grabaciones", "metadata_grabaciones_demo_8b.csv", 20, 20, 0),
    ]
    for upload_type, filename, total, valid, errors in batch_defs:
        batch = db.scalar(select(UploadBatch).where(UploadBatch.tenant_id == tenant.id, UploadBatch.original_filename == filename))
        if batch is None:
            batch = UploadBatch(tenant_id=tenant.id, project_id=project.id, uploaded_by_id=admin.id, upload_type=upload_type, original_filename=filename)
            db.add(batch)
        batch.status = "completed"
        batch.total_rows = total
        batch.valid_rows = valid
        batch.error_rows = errors
        batch.created_rows = valid
        batch.updated_rows = 0
        batch.result_file_path = f"tenants/demo/andina/uploads/{filename}"
        batch.summary_json = json.dumps({"demo": True, "message": "Lote ficticio para demo comercial"})
    view_defs = [
        (admin, "Cartera alto riesgo", "customers", ["name", "document", "balance", "dpd", "risk"], {"risk": "Alto"}, True),
        (admin, "Pagos del mes", "payments", ["customer_id", "amount", "paid_at", "method"], {}, True),
        (admin, "Reparto por gestor", "customers", ["name", "document", "assigned_user_id", "balance", "status"], {}, True),
        (leader, "Productividad equipo", "activities", ["customer_id", "user_id", "channel", "result", "created_at"], {}, True),
        (leader, "Promesas vencidas equipo", "promises", ["customer_id", "user_id", "amount", "due_date", "status"], {"status": "Vencida"}, True),
        (leader, "Obligaciones equipo alto riesgo", "obligations", ["customer_id", "obligation_number", "current_balance", "days_past_due", "risk", "assigned_user_id"], {"risk": "Alto"}, True),
        (gestor_1, "Mis clientes pendientes", "customers", ["name", "document", "balance", "dpd", "status", "risk"], {}, False),
        (gestor_1, "Mis promesas vencidas", "promises", ["customer_id", "amount", "due_date", "status"], {"status": "Vencida"}, False),
        (gestor_1, "Mis gestiones de hoy", "activities", ["customer_id", "channel", "result", "note", "created_at"], {}, False),
        (gestor_1, "Mis obligaciones alto riesgo", "obligations", ["customer_id", "obligation_number", "current_balance", "days_past_due", "risk"], {"risk": "Alto"}, False),
        (gestor_2, "Mis clientes pendientes", "customers", ["name", "document", "balance", "dpd", "status", "risk"], {}, False),
        (gestor_2, "Mis obligaciones alto riesgo", "obligations", ["customer_id", "obligation_number", "current_balance", "days_past_due", "risk"], {"risk": "Alto"}, False),
    ]
    for owner, name, source, columns, filters, is_public in view_defs:
        view = db.scalar(select(SavedDataView).where(SavedDataView.tenant_id == tenant.id, SavedDataView.user_id == owner.id, SavedDataView.name == name))
        if view is None:
            view = SavedDataView(tenant_id=tenant.id, user_id=owner.id, name=name, source=source)
            db.add(view)
        view.columns_json = json.dumps(columns)
        view.filters_json = json.dumps(filters)
        view.sort_json = json.dumps({"field": "id", "direction": "desc"})
        view.is_public = is_public
        view.is_favorite = True
    provider_defs = [
        ("TRONCAL_DEMO_SIP_ANDINA", "Troncal Demo SIP Andina", "telephony"),
        ("WHATSAPP_BUSINESS_DEMO", "WhatsApp Business Demo", "whatsapp"),
        ("SMTP_DEMO_ANDINA", "SMTP Demo Andina", "email"),
    ]
    provider_ids: dict[str, int] = {}
    for code, name, provider_type in provider_defs:
        provider = db.scalar(select(IntegrationProvider).where(IntegrationProvider.tenant_id == tenant.id, IntegrationProvider.code == code))
        if provider is None:
            provider = IntegrationProvider(tenant_id=tenant.id, code=code, name=name, provider_type=provider_type)
            db.add(provider)
            db.flush()
        provider.status = "configured"
        provider.base_url = f"https://demo.icodeup.local/{provider_type}"
        provider.config_json = json.dumps({"demo": True, "mode": "simulated"})
        provider.secret_mask = "de****mo"
        provider_ids[code] = provider.id
    channel_defs = [
        ("telephony", "Telefonia WebRTC Demo", "TRONCAL_DEMO_SIP_ANDINA", "+570000000000"),
        ("whatsapp", "Linea WhatsApp Cobranzas Demo", "WHATSAPP_BUSINESS_DEMO", "+570000000001"),
        ("email", "Correo Cobranzas Demo", "SMTP_DEMO_ANDINA", "cobranzas@demo.icodeup.local"),
        ("sms", "SMS Demo", None, "ICODEUP"),
    ]
    for channel_type, name, provider_code, from_value in channel_defs:
        channel = db.scalar(select(ChannelConfiguration).where(ChannelConfiguration.tenant_id == tenant.id, ChannelConfiguration.channel_type == channel_type, ChannelConfiguration.name == name))
        if channel is None:
            channel = ChannelConfiguration(tenant_id=tenant.id, channel_type=channel_type, name=name)
            db.add(channel)
        channel.provider_id = provider_ids.get(provider_code) if provider_code else None
        channel.status = "active"
        channel.from_value = from_value
        channel.config_json = json.dumps({"demo": True})
    template_defs = [
        ("whatsapp", "PROMESA_RECORDATORIO", "Recordatorio promesa", None, "Hola {{cliente}}, recuerda tu compromiso de pago demo."),
        ("email", "ACUERDO_PAGO", "Acuerdo de pago", "Acuerdo de pago demo", "Adjuntamos resumen demo de acuerdo de pago."),
        ("sms", "CONTACTO_RAPIDO", "Contacto rapido", None, "Icodeup 360 demo: por favor comunicate con nosotros."),
    ]
    for channel_type, code, name, subject, body in template_defs:
        template = db.scalar(select(CommunicationTemplate).where(CommunicationTemplate.tenant_id == tenant.id, CommunicationTemplate.code == code))
        if template is None:
            template = CommunicationTemplate(tenant_id=tenant.id, channel_type=channel_type, code=code, name=name, body=body)
            db.add(template)
        template.subject = subject
        template.body = body
        template.status = "active"
    webhook = db.scalar(select(WebhookConfiguration).where(WebhookConfiguration.tenant_id == tenant.id, WebhookConfiguration.name == "Webhook Pagos Demo"))
    if webhook is None:
        webhook = WebhookConfiguration(tenant_id=tenant.id, name="Webhook Pagos Demo", event_type="payment.created", target_url="https://demo.icodeup.local/webhooks/payments")
        db.add(webhook)
    webhook.status = "active"
    webhook.secret_mask = "wh****mo"
    event = db.scalar(select(ChannelEventLog).where(ChannelEventLog.tenant_id == tenant.id, ChannelEventLog.event_type == "demo.seed.8b"))
    if event is None:
        db.add(ChannelEventLog(tenant_id=tenant.id, channel_type="system", event_type="demo.seed.8b", status="simulated", payload_json=json.dumps({"demo": True, "message": "Semilla Fase 8B"})))


def _seed_secondary_demo_tenants(db: Session, tenants: dict[str, Tenant], modules: dict[str, Module]) -> None:
    for tenant_def in DEMO_TENANTS[1:]:
        tenant = tenants[tenant_def["slug"]]
        _ensure_subscription(db, tenant, tenant_def["plan"])
        _set_demo_modules(db, tenant, modules, tenant_def["modules"])
        admin = _get_or_create_demo_user(db, tenant, f"admin.{tenant.slug}@demo.icodeup.local", f"Admin {tenant.name}", TENANT_ADMIN, "Administrador demo")
        for code, name, description in SECONDARY_PROJECTS.get(tenant.slug, []):
            project = _get_or_create_project(db, tenant, code, name, description)
            _ensure_assignment(db, admin, project, "leader")
        _seed_tenant_configuration(db, tenant)
        _seed_functional_configuration(db, tenant)


def _seed_phase5_demo_data(db: Session, modules: dict[str, Module], platform_tenant: Tenant) -> None:
    tenants = {tenant_def["slug"]: _get_or_create_demo_tenant(db, tenant_def) for tenant_def in DEMO_TENANTS}
    andina = tenants["andina-servicios-financieros"]
    _ensure_subscription(db, andina, "business")
    _set_demo_modules(db, andina, modules, DEMO_TENANTS[0]["modules"])
    _seed_tenant_configuration(db, andina)
    _seed_functional_configuration(db, andina)

    platform_demo = _get_or_create_demo_user(db, platform_tenant, DEMO_USER_DEFS[0][0], DEMO_USER_DEFS[0][1], DEMO_USER_DEFS[0][2], DEMO_USER_DEFS[0][3])
    platform_demo.leader_id = None

    users: dict[str, User] = {}
    for email, name, role, title, leader_email in DEMO_USER_DEFS[1:]:
        users[email] = _get_or_create_demo_user(db, andina, email, name, role, title, leader_email)

    specialized_roles = _ensure_specialized_roles_for_tenant(db, andina)
    _assign_profile_role(db, users["coord.cobranzas.andina@demo.icodeup.local"], specialized_roles["collections_leader"])
    _assign_profile_role(db, users["gestor1.andina@demo.icodeup.local"], specialized_roles["collections_agent"])
    _assign_profile_role(db, users["gestor2.andina@demo.icodeup.local"], specialized_roles["collections_agent"])
    _assign_profile_role(db, users["calidad.andina@demo.icodeup.local"], specialized_roles["tenant_auditor"])
    _assign_profile_role(db, users["abogado.andina@demo.icodeup.local"], specialized_roles["lawyer"])
    _assign_profile_role(db, users["comercial.andina@demo.icodeup.local"], specialized_roles["sales_advisor"])

    projects = [
        _get_or_create_project(db, andina, code, name, description)
        for code, name, description, _count in ANDINA_PROJECTS
    ]
    for project in projects:
        for email, user in users.items():
            role_in_project = "leader"
            if email.startswith("gestor"):
                role_in_project = "agent"
            elif email.startswith("calidad"):
                role_in_project = "quality"
            elif email.startswith("abogado"):
                role_in_project = "lawyer"
            elif email.startswith("comercial"):
                role_in_project = "sales"
            _ensure_assignment(db, user, project, role_in_project)
    _ensure_channels(db, andina, projects[0])
    typifications = _ensure_typifications(db, andina)

    gestor_1 = users["gestor1.andina@demo.icodeup.local"]
    gestor_2 = users["gestor2.andina@demo.icodeup.local"]
    leader = users["coord.cobranzas.andina@demo.icodeup.local"]
    lawyer = users["abogado.andina@demo.icodeup.local"]
    commercial = users["comercial.andina@demo.icodeup.local"]
    global_index = 1
    for project_idx, (code, _name, _description, count) in enumerate(ANDINA_PROJECTS):
        project = next(item for item in projects if item.code == code)
        for _ in range(count):
            assigned = gestor_1 if global_index % 2 else gestor_2
            segment = ["Consumo castigado", "Microcredito", "Tarjeta privada", "Judicializado"][project_idx]
            judicialized = code == "CARTERA-JUDICIALIZADA"
            customer = _ensure_customer(db, andina, project, assigned, global_index, segment, judicialized)
            _ensure_customer_obligations(db, customer, leader)
            _ensure_activity(db, customer, assigned, typifications.get("CONTACTO"), "phone", "Llamada efectiva", f"DEMO FASE 5 gestion telefonica {customer.document}", global_index % 10)
            if global_index % 3 == 0:
                _ensure_activity(db, customer, assigned, typifications.get("PROMESA"), "whatsapp", "Promesa generada", f"DEMO FASE 5 promesa whatsapp {customer.document}", 2)
                _ensure_promise(db, customer, assigned, max(120000, int(customer.balance * 0.12)), 5 + (global_index % 12), "Vigente")
            if global_index % 5 == 0:
                _ensure_promise(db, customer, assigned, max(90000, int(customer.balance * 0.08)), -2, "Vencida")
            if global_index % 4 == 0:
                _ensure_payment(db, customer, assigned, max(80000, int(customer.balance * 0.07)), global_index % 14)
            if global_index % 6 == 0:
                agreement = _ensure_agreement(db, customer, assigned, 4, max(400000, int(customer.balance * 0.45)), "active" if global_index % 12 else "overdue")
                _ensure_document(
                    db,
                    andina,
                    assigned,
                    "acuerdo de pago",
                    f"acuerdo_demo_{customer.document}.pdf",
                    f"tenants/demo/andina/acuerdos/acuerdo_demo_{customer.document}.pdf",
                    project_id=customer.project_id,
                    customer_id=customer.id,
                    agreement_id=agreement.id,
                )
            if global_index <= 18:
                _ensure_document(
                    db,
                    andina,
                    assigned,
                    "pagare",
                    f"pagare_demo_{customer.document}.pdf",
                    f"tenants/demo/andina/documentos/pagare_demo_{customer.document}.pdf",
                    project_id=customer.project_id,
                    customer_id=customer.id,
                )
            if judicialized:
                legal_case = _ensure_legal_case(db, andina, customer, lawyer, global_index)
                _ensure_activity(db, customer, lawyer, typifications.get("ESCALAR_JURIDICO"), "email", "Escalamiento juridico", f"DEMO FASE 5 escalamiento juridico {customer.document}", 1)
                _ensure_document(
                    db,
                    andina,
                    lawyer,
                    "demanda",
                    f"demanda_demo_{customer.document}.pdf",
                    f"tenants/demo/andina/juridico/demanda_demo_{customer.document}.pdf",
                    project_id=customer.project_id,
                    customer_id=customer.id,
                    legal_case_id=legal_case.id,
                )
            global_index += 1

    andina_customers = list(db.scalars(select(Customer).where(Customer.tenant_id == andina.id).order_by(Customer.id)))
    _ensure_operational_sheet_rows(db, andina, andina_customers, {user.id: user for user in users.values()})
    _ensure_sales_demo(db, andina, projects[0], commercial)
    _seed_phase8b_collection_demo(db, andina, projects, users)
    _seed_secondary_demo_tenants(db, tenants, modules)

def bootstrap_platform(db: Session) -> None:
    if not settings.platform_admin_email or not settings.platform_admin_password:
        return

    modules = _seed_modules(db)
    _seed_plans(db)
    roles = _seed_roles_and_permissions(db, modules)
    _seed_menu(db, modules)
    _seed_functional_configuration(db)

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
        _seed_functional_configuration(db, existing_tenant)

    _seed_tenant_modules(db, modules)
    if settings.enable_demo_seeds or settings.enable_demo_data:
        _seed_phase5_demo_data(db, modules, tenant)
    if settings.enable_pilot_icodeup_seed:
        seed_pilot_icodeup_advisors(db, modules, roles)

    for existing_user in db.scalars(select(User)):
        sync_user_profile(db, existing_user)

    db.commit()
