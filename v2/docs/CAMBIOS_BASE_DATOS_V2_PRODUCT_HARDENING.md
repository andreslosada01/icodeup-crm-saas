# Cambios Base de Datos V2 Product Hardening

Fecha: 2026-05-28  
Rama: `feature/product-hardening-collection-legal-crm`

## Politica aplicada

- No se eliminaron tablas.
- No se eliminaron columnas existentes.
- No se hicieron migraciones destructivas.
- Los modelos nuevos son aditivos.
- Los tenants sin plan o modulos configurados conservan comportamiento permisivo.
- Para produccion se recomienda convertir estos cambios a migraciones Alembic versionadas antes de desplegar.

## Tablas nuevas

### Core SaaS Icodeup 360

- `modules`
- `roles`
- `permissions`
- `role_permissions`
- `user_profiles`
- `menu_items`
- `tenant_configurations`
- `parties`

### SaaS comercial

- `saas_plans`
- `tenant_subscriptions`
- `tenant_modules`

### Cobranzas

- `payment_agreements`
- `payment_agreement_installments`

### Juridico

- `legal_cases`
- `legal_actions`
- `legal_hearings`
- `legal_deadlines`

### Documentos

- `documents`

### Ventas

- `leads`
- `opportunities`

### Auditoria

- `audit_logs`

## Impacto operativo esperado

- La operacion actual de clientes, promesas, pagos, cola, BI, canales y tipificaciones no cambia.
- `Base.metadata.create_all` crea las tablas nuevas en desarrollo local.
- Se agregan validaciones de modulos activos para CRM, juridico, documentos y ventas.
- Los tenants sin modulos configurados conservan comportamiento permisivo para evitar bloquear instalaciones antiguas.
- Los endpoints nuevos validan tenant y rol para evitar acceso cruzado.

## Columnas aditivas Fase 1 Core SaaS

### `tenants`

- `document_type`
- `document_number`
- `plan_id`
- `logo_url`
- `primary_color`
- `secondary_color`
- `timezone`
- `updated_at`

### `users`

- `updated_at`

### `saas_plans`

- `base_price`
- `max_storage_mb`
- `max_records`
- `includes_ai`
- `includes_advanced_bi`
- `is_active`
- `updated_at`

### `tenant_subscriptions`

- `renewal_date`
- `updated_at`

### `tenant_modules`

- `module_id`
- `is_enabled`
- `enabled_at`
- `configuration_json`

### `audit_logs`

- `module`
- `object_type`
- `object_id`
- `old_value`
- `new_value`

## Recomendacion para test y produccion

1. Crear revision Alembic con estas tablas.
2. Probar migracion en base de test con copia anonima.
3. Ejecutar checklist de regresion.
4. Habilitar modulos por tenant gradualmente.
5. Agregar indices adicionales si el volumen real supera la data demo.
