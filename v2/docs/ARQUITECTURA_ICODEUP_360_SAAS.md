# Arquitectura Icodeup 360 SaaS

## Objetivo

Icodeup 360 evoluciona como una plataforma SaaS modular tipo Business Operating System / Operational Intelligence Platform. La arquitectura conserva FastAPI, SQLAlchemy, PostgreSQL y frontend HTML/CSS/JS, evitando una reconstruccion desde cero.

## Decision multitenant

La fase actual usa **shared database / shared schema**.

Todos los registros viven en la misma base de datos y el aislamiento se aplica mediante `tenant_id`. La opcion de base dedicada por cliente Enterprise queda como evolucion futura, no implementada en esta fase.

## Capas principales

```text
v2/backend/app/
  api/routes/
    auth.py
    menu.py
    dashboard.py
    governance.py
    administration.py
    subscriptions.py
    crm/
    legal.py
    documents.py
    sales.py
  models/
    tenant.py
    identity.py
    security.py
    subscription.py
    menu.py
    configuration.py
    party.py
    audit.py
    crm.py
    legal.py
    documents.py
    sales.py
  services/
    access_control.py
    menu_service.py
    dashboard_service.py
    audit_service.py
    bootstrap_service.py
```

## Core SaaS

El Core SaaS concentra:

- Tenants / empresas.
- Usuarios y perfiles.
- Roles.
- Permisos.
- Planes.
- Suscripciones.
- Modulos.
- Activacion de modulos por empresa.
- Menu dinamico.
- Dashboard por audiencia.
- Configuracion tenant.
- Auditoria.
- Party / tercero maestro.

## Modulos actuales

- CRM 360.
- Cobranzas.
- Juridico.
- Documentos.
- Ventas.
- BI.
- Integraciones base.

## Modulos preparados a futuro

- Recursos Humanos.
- Finanzas.
- Operaciones industriales.

Estos modulos solo quedan registrados en el catalogo SaaS. No se construyen funcionalmente en Fase 1.

## Seguridad transversal

`services/access_control.py` centraliza:

- `get_current_tenant`.
- `user_has_permission`.
- `user_has_module`.
- `require_tenant`.
- `require_module`.
- `require_permission`.
- `validate_record_belongs_to_tenant`.

Las rutas operativas pueden validar tenant, modulo y permiso sin duplicar logica.

## Menu dinamico

`GET /api/menu/me` retorna el menu permitido por:

- usuario,
- tenant,
- rol,
- permisos,
- modulos activos,
- audiencia del usuario.

El frontend renderiza el menu con esa respuesta y oculta modulos no contratados.

### Flujo de navegacion por rol

- **SuperAdmin Icodeup:** `governance`, `tenants`, `plans`, `subscriptions`, `modules`, `users`, `projects`, `typifications`, `audit`, `system-health`.
- **Admin Empresa:** `dashboard`, `tenant-settings`, `company-users`, `roles-permissions`, `tenant-modules`, `branding`, `customers`, `parties`, operacion, reportes y auditoria del tenant.
- **Lider operativo:** inicio, cola, clientes, terceros, promesas, pagos, acuerdos, juridico, documentos, ventas y reportes autorizados.
- **Usuario operativo:** inicio, mi operacion, clientes/terceros, tareas y documentos autorizados.

No se debe confiar solo en el menu: los endpoints tambien validan tenant, modulo y permiso.

## Dashboard por rol

`GET /api/dashboard/me` retorna una lectura distinta para:

- platform admin,
- company admin,
- lider operativo,
- usuario operativo.

## Compatibilidad

La fase mantiene:

- `User.role` como compatibilidad legacy.
- `tenant_id` existente en tablas operativas.
- rutas actuales de CRM, legal, documents, sales y BI.
- frontend estatico actual.

## Evolucion recomendada

1. Convertir compat migrations a Alembic.
2. Convertir roles custom en una experiencia completa de edicion/duplicado/versionado.
3. Migrar progresivamente clientes a `Party`.
4. Agregar workflows/estados configurables.
5. Migrar frontend a React/Vite en V3.

## Reglas de exportes seguros

- Todo exporte operativo debe validar permiso `*.export`.
- Los usuarios cliente exportan solo su `tenant_id`.
- Platform admin puede exportar globalmente solo desde rutas autorizadas.
- Si se recibe `tenant_id` por parametro, solo platform admin puede usarlo para cambiar alcance.
- Los exportes agregados en Fase 2 usan consultas filtradas por `customer_query` o por tenant validado.
