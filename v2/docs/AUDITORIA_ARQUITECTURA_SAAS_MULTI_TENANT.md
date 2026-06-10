# Auditoria Arquitectura SaaS Multi-Tenant

Fecha: 2026-06-10  
Rama auditada: `feature/deploy-test-server`  
Producto: Icodeup 360 ERP/CRM SaaS

## 1. Resumen ejecutivo

La arquitectura actual de Icodeup 360 opera como SaaS multiempresa con modelo **shared database / shared schema**. Todas las empresas comparten una misma base PostgreSQL y una misma estructura de tablas; el aislamiento se implementa mediante `tenant_id` en las entidades operativas, validaciones de permisos, modulos activos, alcance por rol y filtros en routers/servicios.

No existe hoy una base independiente por empresa. Tampoco existe un router dinamico que cambie `DATABASE_URL` por tenant. La opcion database-per-tenant queda como evolucion futura para clientes Enterprise, no como arquitectura actual.

Decision tecnica: la arquitectura es correcta para MVP comercial, demo, servidor test y una primera produccion controlada, siempre que se mantengan pruebas permanentes de aislamiento y configuracion productiva estricta.

## 2. Modelo SaaS actual

| Pregunta | Respuesta |
|---|---|
| Usa base por empresa | No |
| Usa base compartida | Si |
| Usa schema compartido | Si |
| Clave de aislamiento | `tenant_id` |
| Configuracion declarada | `tenant_mode = shared_schema` en codigo/base de ejemplo; `.env` local puede diferir |
| Base dedicada Enterprise implementada | No |
| Base dedicada Enterprise posible a futuro | Si, con cambios de provisioning, session routing, migracion y backups |

## 3. Evidencia tecnica

- `v2/backend/app/core/config.py` define `tenant_mode: str = "shared_schema"`.
- `v2/backend/.env.example` incluye `TENANT_MODE=shared_schema`.
- El `.env` local revisado declara `TENANT_MODE=row_level`, pero el codigo no implementa politicas PostgreSQL RLS, `SET LOCAL app.tenant_id`, ni filtros automáticos en la sesion. Por lo tanto, el comportamiento real sigue siendo **shared schema con aislamiento por aplicacion**.
- `v2/backend/app/db/session.py` crea un solo `engine` usando `settings.database_url`.
- No hay factory de engines por tenant ni conexion dinamica por empresa.
- Los modelos operativos principales tienen `tenant_id`.
- `require_tenant`, `require_module`, `require_permission` y helpers de acceso centralizan parte del control.

## 4. Entidades criticas con tenant_id

Tienen `tenant_id` directo:

- usuarios y perfiles: `users`, `user_profiles`
- operacion de cartera: `customers`, `customer_obligations`, `management_activities`
- recaudo: `payment_promises`, `payments`, `payment_agreements`
- cargas y Excel Web: `upload_batches`, `operational_sheet_rows`, `saved_data_views`, `data_export_logs`
- documentos: `documents`, `operational_files`
- juridico: `legal_cases`, `legal_actions`, `legal_hearings`, `legal_deadlines`
- ventas: `leads`, `opportunities`
- integraciones: `integration_providers`, `channel_configurations`, `communication_templates`, `webhook_configurations`, `channel_event_logs`
- gobierno tenant: `tenant_configurations`, `tenant_modules`, `tenant_subscriptions`
- auditoria y alertas: `audit_logs`, `generated_alerts`

No tienen `tenant_id` directo porque son globales o hijos con alcance por padre:

- globales: `tenants`, `modules`, `permissions`, `saas_plans`, `menu_items`
- pivotes/hijos por relacion: `role_permissions`, `payment_agreement_installments`, `typification_tree_nodes`, `workflow_stages`, `workflow_transitions`

## 5. Controles de aislamiento actuales

- Autenticacion JWT en rutas operativas mediante `current_user`.
- Validacion de tenant con `require_tenant`.
- Validacion de modulo activo con `require_module` y `require_active_module`.
- Validacion granular con `require_permission` y `user_has_permission`.
- Menus dinamicos por audiencia, modulo y permiso.
- Filtros por tenant en routers CRM, documentos, juridico, ventas, cargas, Excel Web, integraciones, alertas, configuracion y governance tenant.
- Acceso por ID directo validado con helpers como `customer_for_access`, `legal_case_for_access`, `document_for_access`, `_project_for_access`, `_leader_for_access`.
- Auditoria de eventos operativos y exportes.
- Tests de aislamiento existentes y nueva suite profunda `test_saas_tenant_isolation_deep.py`.

## 6. Riesgo actual de mezcla de empresas

| Area | Riesgo | Evaluacion |
|---|---:|---|
| Tablas operativas sin tenant_id | Bajo | La mayoria tiene `tenant_id`; hijos sin tenant directo dependen de padre validado. |
| Consultas operativas globales | Bajo/Medio | Los endpoints revisados aplican filtros; se corrigio alcance interno de lideres. |
| Acceso por ID directo | Bajo | Hay validaciones especificas en clientes, documentos, juridico, cargas, Excel Web y equipos. |
| SuperAdmin Icodeup | Controlado | Puede ver global por diseno. |
| Admin empresa | Bajo | `target_tenant` y `require_tenant` limitan alcance. |
| Gestor | Bajo | Clientes y operaciones se filtran por asignacion. |
| Lider operativo | Medio reducido | Se ajusto para evitar consulta de otros lideres por URL sin alcance administrativo. |
| Configuracion productiva | Medio | `DEBUG`, `ALLOWED_ORIGINS` y storage estan documentados, pero algunos aun no tienen enforcement activo. |

## 7. Database-per-tenant futuro

Para soportar base dedicada por empresa se requeriria:

1. Provisioning de base por tenant y registro de conexion segura.
2. Resolver tenant antes de abrir sesion, por subdominio, header firmado o dominio.
3. Session/engine factory por tenant.
4. Migraciones Alembic por base.
5. Backups y restore por tenant.
6. Observabilidad y healthcheck por tenant.
7. Jobs de migracion desde shared schema hacia base dedicada.
8. Politica de data residency y cifrado por cliente.
9. Pruebas de regresion para ambos modos.

No se recomienda implementar esto antes del servidor test. Para el producto inicial es mas seguro mantener shared schema y reforzar pruebas.

## 8. Configuracion productiva revisada

Para produccion real:

- `APP_ENV=production`.
- `SECRET_KEY` obligatorio, largo y unico.
- `DATABASE_URL` obligatorio, apuntando a base productiva separada de test.
- `TENANT_MODE=shared_schema` mientras no exista implementacion real de Row Level Security en PostgreSQL.
- `ENABLE_DEMO_DATA=false`.
- `ENABLE_DEMO_SEEDS=false`.
- No usar usuarios ni passwords demo.
- Limitar origenes HTTP reales cuando se implemente middleware CORS.
- Mantener logs sin secretos.
- Definir storage real por ambiente.
- Ejecutar `alembic upgrade head` antes del arranque.

## 9. Observaciones tecnicas

- `init_database()` aun ejecuta `Base.metadata.create_all` y `apply_compatibility_migrations` en startup. Es util en local/test, pero en produccion debe gobernar Alembic.
- `apply_compatibility_migrations` debe conservarse temporalmente como compatibilidad, pero no debe ser el mecanismo principal de cambios futuros.
- `User.role` continua como fallback legacy; la fuente de permisos ya se apoya en `UserProfile`, `Role` y `Permission`.
- Variables como `DEBUG` y `ALLOWED_ORIGINS` estan documentadas en `.env.example`, pero no tienen enforcement activo en la app actual.

## 10. Decision de readiness

Estado para servidor test: **Listo con observaciones**.

No se identifico una razon para bloquear el despliegue en servidor test. Si se despliega con base limpia, demo controlada y variables correctas, el producto puede validar multiempresa sin mezclar datos.

Estado para produccion publica: **Apto para preparacion, no para salida sin hardening operativo final**.

Antes de produccion publica se recomienda completar enforcement de CORS/origenes, politica de cookies seguras si se usa sesion web, apagar demo, usar Alembic como fuente formal y definir backups/restore probados.
