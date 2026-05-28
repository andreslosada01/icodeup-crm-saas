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
