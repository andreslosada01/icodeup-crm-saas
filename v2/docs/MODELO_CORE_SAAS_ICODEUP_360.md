# Modelo Core SaaS Icodeup 360

## Tenant / Company

Tabla: `tenants`

Campos endurecidos:

- `name`
- `slug`
- `document_type`
- `document_number`
- `tax_id` legacy
- `status`
- `plan_id`
- `logo_url`
- `primary_color`
- `secondary_color`
- `timezone`
- `created_at`
- `updated_at`

## Usuario y perfil

`users` conserva identidad, autenticacion y compatibilidad legacy.

`user_profiles` agrega contexto SaaS:

- `user_id`
- `tenant_id`
- `role_id`
- `is_platform_admin`
- `is_company_admin`
- `active_project_id`
- `status`
- timestamps

## Roles y permisos

Tablas:

- `roles`
- `permissions`
- `role_permissions`

Los roles legacy se mantienen como string en `users.role`, pero la autorizacion nueva puede usar `UserProfile.role_id` y `RolePermission`.

Roles sistema:

- `platform_admin`
- `tenant_admin`
- `coordinator`
- `quality_supervisor`
- `agent`

## Matriz de permisos por modulo

| Modulo | Permisos base |
| --- | --- |
| Core | `menu.view`, `platform.governance.view`, `platform.governance.configure`, `health.view` |
| Administracion | `tenant.settings.view`, `tenant.settings.configure`, `users.view`, `users.create`, `users.update`, `users.assign`, `roles.view`, `roles.create`, `roles.update`, `roles.configure`, `modules.view`, `modules.configure`, `audit.logs.view`, `audit.logs.export` |
| CRM | `crm.dashboard.view`, `crm.clients.view`, `crm.clients.create`, `crm.clients.update`, `crm.clients.delete`, `crm.clients.import`, `crm.clients.export`, `parties.view`, `parties.create`, `parties.update`, `parties.export` |
| Cobranzas | `collections.queue.view`, `collections.promises.view/create/update/export`, `collections.payments.view/create/export`, `collections.agreements.view/create/update/export` |
| Juridico | `legal.cases.view/create/update/export`, `legal.deadlines.view` |
| Documentos | `documents.view/create/update/export` |
| Ventas | `sales.leads.view/create/update/export`, `sales.opportunities.view/create/update/export` |
| BI | `reports.view`, `reports.export` |
| Integraciones | `integrations.channels.view/create/update` |

Los permisos legacy (`crm.read`, `crm.manage`, `collections.read`, etc.) se conservan para compatibilidad durante la transicion.

## Planes y suscripciones

Tablas:

- `saas_plans`
- `tenant_subscriptions`

Planes base:

- Starter.
- Professional.
- Business.
- Enterprise.

## Modulos

Tablas:

- `modules`
- `tenant_modules`

Modulos registrados:

- `core`
- `administration`
- `crm`
- `collections`
- `legal`
- `documents`
- `sales`
- `bi`
- `integrations`
- `hr`
- `finance`
- `industrial`

Los modulos futuros quedan registrados pero no desarrollados funcionalmente en esta fase.

## Reglas de activacion de modulos

- El catalogo global vive en `modules`.
- La contratacion por empresa vive en `tenant_modules`.
- `enabled` e `is_enabled` deben estar activos para permitir acceso.
- Si un tenant antiguo no tiene filas en `tenant_modules`, el sistema conserva comportamiento permisivo para no bloquear instalaciones heredadas.
- Solo SuperAdmin Icodeup puede activar/desactivar modulos desde `/api/governance/modules/{tenant_id}`.
- Admin Empresa puede consultar sus modulos, pero no activar capacidades no contratadas.

## Menu dinamico

Tabla: `menu_items`

Campos:

- `label`
- `route_name`
- `url`
- `icon`
- `module_id`
- `module_code`
- `parent_id`
- `order`
- `is_active`
- `required_permission_code`
- `audience`

Audiencias:

- `platform_admin`
- `company_admin`
- `operational_leader`
- `operational_user`

## Configuracion tenant

Tabla: `tenant_configurations`

Uso:

- branding,
- textos de login,
- colores,
- parametros operativos futuros.

## Party / Tercero maestro

Tabla: `parties`

Permite representar:

- persona natural,
- empresa,
- cliente,
- deudor,
- proveedor,
- empleado,
- contacto,
- prospecto.

En Fase 1 se crea el modelo, pero no se migra todavia la data de `customers`.

## Auditoria

Tabla: `audit_logs`

Campos reforzados:

- `tenant_id`
- `user_id`
- `action`
- `module`
- `object_type`
- `object_id`
- `old_value`
- `new_value`
- `ip_address`
- `user_agent`
- `created_at`

Se conservan `entity_type`, `entity_id`, `before_json` y `after_json` por compatibilidad.

## Pantallas administrativas Fase 2

- Gobierno SaaS global.
- Planes.
- Suscripciones.
- Modulos por empresa.
- Mi empresa.
- Usuarios de empresa.
- Roles y permisos.
- Branding.
- Auditoria.
- Terceros maestros.
