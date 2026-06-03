# Matriz Permisos Endpoints V2

## Principios

- El menu dinamico oculta opciones por audiencia, modulo y permiso.
- El backend valida permiso aunque el menu no muestre la opcion.
- `User.role` se conserva como fallback legacy, pero la fuente objetivo es `Role`, `Permission`, `RolePermission` y `UserProfile`.
- Platform admin puede todo.
- Admin empresa opera solo su tenant.
- Agent opera solo informacion asignada cuando el modelo lo permite.

## Matriz principal

| Modulo | Endpoint | Permiso requerido | Modulo requerido | Roles legacy compatibles | Tenant |
| --- | --- | --- | --- | --- | --- |
| core | `GET /api/menu/me` | `menu.view` | core | todos autenticados con fallback | menu filtrado por tenant, permisos y modulos |
| core | `GET /api/dashboard/me` | `crm.dashboard.view` o perfil admin | core | platform_admin, tenant_admin, coordinator, agent, quality_supervisor | datos agregados por tenant salvo platform |
| governance | `GET /api/governance/permissions` | `roles.view` o admin empresa | administration | platform_admin, tenant_admin | admin empresa no ve permisos reservados |
| governance | `GET /api/governance/roles` | `roles.view` | administration | platform_admin, tenant_admin | target tenant obligatorio |
| governance | `POST /api/governance/roles` | `roles.create` | administration | platform_admin, tenant_admin | no permite permisos reservados a cliente |
| governance | `PATCH /api/governance/roles/{role_id}` | `roles.update` | administration | platform_admin, tenant_admin | roles de sistema solo Icodeup |
| governance | `PUT /api/governance/roles/{role_id}/permissions` | `roles.configure` | administration | platform_admin, tenant_admin | no permisos platform para clientes |
| governance | `PUT /api/governance/users/{user_id}/role` | `users.assign` | administration | platform_admin, tenant_admin | usuario y rol del mismo tenant |
| governance | `GET /api/governance/modules` | `modules.view` | administration | platform_admin, tenant_admin | admin cliente solo consulta su tenant |
| governance | `PUT /api/governance/modules/{tenant_id}` | platform admin | administration | platform_admin | solo Icodeup activa/desactiva |
| governance | `GET /api/governance/settings` | `tenant.settings.view` | administration | platform_admin, tenant_admin | tenant propio salvo platform |
| governance | `PATCH /api/governance/settings` | `tenant.settings.configure` | administration | platform_admin, tenant_admin | tenant propio salvo platform |
| audit | `GET /api/governance/audit-logs` | `audit.logs.view` | administration | platform_admin, tenant_admin | platform global, cliente solo tenant |
| parties | `GET /api/governance/parties` | `parties.view` | administration | platform_admin, tenant_admin, coordinator, agent | tenant obligatorio |
| parties | `POST /api/governance/parties` | `parties.create` | administration | platform_admin, tenant_admin, coordinator | tenant obligatorio |
| parties | `PATCH /api/governance/parties/{party_id}` | `parties.update` | administration | platform_admin, tenant_admin, coordinator | tenant obligatorio |
| crm | `GET /api/crm/options` | `crm.read` | crm | todos operativos | opciones por tenant visible |
| crm | `GET /api/crm/dashboard` | `crm.dashboard.view` | crm | todos operativos autorizados | agregado por tenant/asignacion |
| crm | `GET /api/crm/customers` | `crm.clients.view` | crm | platform_admin, tenant_admin, coordinator, quality_supervisor, agent | agente por asignacion |
| crm | `POST /api/crm/customers` | `crm.clients.create` | crm | tenant_admin, coordinator, agent | valida proyecto, tenant y limite plan |
| crm | `GET /api/crm/customers/export` | `crm.clients.export` | crm | platform_admin, tenant_admin | export filtrado por tenant |
| crm | `POST /api/crm/customers/import` | `crm.clients.import` | crm | tenant_admin, coordinator | valida tenant, asignacion y limite plan |
| collections | `GET /api/crm/queue` | `collections.queue.view` | collections | todos operativos autorizados | cliente/asignacion |
| collections | `GET /api/crm/promises` | `collections.promises.view` | collections | todos operativos autorizados | cliente/asignacion |
| collections | `POST /api/crm/promises` | `collections.promises.create` | collections | tenant_admin, coordinator, agent | cliente permitido |
| collections | `GET /api/crm/payments` | `collections.payments.view` | collections | todos operativos autorizados | cliente/asignacion |
| collections | `POST /api/crm/payments` | `collections.payments.create` | collections | tenant_admin, coordinator, agent | cliente permitido |
| collections | `GET /api/crm/payments/export` | `collections.payments.export` | collections | platform_admin, tenant_admin | export filtrado por tenant |
| collections | `GET /api/crm/agreements` | `collections.agreements.view` | collections | todos operativos autorizados | cliente/asignacion |
| collections | `POST /api/crm/agreements` | `collections.agreements.create` | collections | tenant_admin, coordinator, agent | cliente permitido |
| collections | `PATCH /api/crm/agreements/{agreement_id}/installments/{installment_id}` | `collections.agreements.update` | collections | tenant_admin, coordinator, agent | acuerdo permitido |
| legal | `GET /api/legal/cases` | `legal.cases.view` | legal | platform_admin, tenant_admin, coordinator, quality_supervisor, agent | cliente visible |
| legal | `POST /api/legal/cases` | `legal.cases.create` | legal | platform_admin, tenant_admin, coordinator | customer y abogado mismo tenant |
| legal | `PATCH /api/legal/cases/{case_id}` | `legal.cases.update` | legal | platform_admin, tenant_admin, coordinator | caso mismo tenant |
| legal | `GET /api/legal/deadlines` | `legal.deadlines.view` | legal | autorizados de lectura | casos visibles |
| documents | `GET /api/documents` | `documents.view` | documents | autorizados de lectura | tenant y cliente asignado si agente |
| documents | `POST /api/documents` | `documents.create` | documents | platform_admin, tenant_admin, coordinator | valida relaciones y storage plan |
| documents | `PATCH /api/documents/{document_id}` | `documents.update` | documents | platform_admin, tenant_admin, coordinator | documento mismo tenant |
| sales | `GET /api/sales/leads` | `sales.leads.view` | sales | autorizados de ventas | tenant/asignacion |
| sales | `POST /api/sales/leads` | `sales.leads.create` | sales | platform_admin, tenant_admin, coordinator | tenant/proyecto/usuario |
| sales | `GET /api/sales/opportunities` | `sales.opportunities.view` | sales | autorizados de ventas | tenant/asignacion |
| sales | `POST /api/sales/opportunities` | `sales.opportunities.create` | sales | platform_admin, tenant_admin, coordinator | tenant y relaciones |

## Observaciones

- Los helpers legacy `ensure_read_access` y `ensure_manage_access` siguen como segunda barrera de compatibilidad.
- La siguiente fase debe mover mas ownership hacia permisos explicitos y reducir checks directos por `User.role`.
- Los exportes reforzados son clientes y pagos; otros exportes futuros deben seguir el mismo patron.
## Actualizacion Fase 8 - Configuracion, alertas, juridico y ventas

| Modulo | Endpoint | Permiso requerido | Modulo requerido | Roles legacy compatibles | Restricciones tenant | Observaciones |
|---|---|---|---|---|---|---|
| configuration | `GET /api/configuration/catalogs` | `configuration.view` | administration | platform_admin, tenant_admin | Global + tenant propio; platform puede filtrar tenant | Lista catalogos funcionales globales y tenant. |
| configuration | `POST /api/configuration/catalogs` | `configuration.catalogs.manage` | administration | platform_admin, tenant_admin | Admin Empresa solo crea en su tenant | No permite modificar plantillas globales desde tenant. |
| configuration | `GET /api/configuration/rules` | `configuration.view` | administration | platform_admin, tenant_admin | Global + tenant propio | Reglas de negocio parametrizables. |
| configuration | `POST /api/configuration/rules` | `configuration.rules.manage` | administration | platform_admin, tenant_admin | Admin Empresa solo crea en su tenant | Preparado para SLAs y escalamiento. |
| configuration | `GET /api/configuration/alert-rules` | `configuration.view` | administration | platform_admin, tenant_admin | Global + tenant propio | Reglas fuente del motor de alertas. |
| configuration | `POST /api/configuration/alert-rules` | `configuration.alerts.manage` | administration | platform_admin, tenant_admin | Admin Empresa solo crea en su tenant | Parametriza severidad y rol objetivo. |
| configuration | `GET /api/configuration/workflows` | `configuration.view` | administration | platform_admin, tenant_admin | Global + tenant propio | Workflows juridico/comercial. |
| configuration | `POST /api/configuration/workflows` | `configuration.workflows.manage` | administration | platform_admin, tenant_admin | Admin Empresa solo crea en su tenant | Define flujo funcional. |
| alerts | `GET /api/alerts` | `alerts.view` | bi | platform_admin, tenant_admin, coordinator, agent | Platform global; tenant/usuarios por alcance asignado | Alertas calculadas dinamicamente. |
| alerts | `GET /api/alerts/summary` | `alerts.view` | bi | platform_admin, tenant_admin, coordinator, agent | Respeta tenant y permisos | Resumen por severidad y modulo. |
| legal | `GET /api/legal/dashboard` | `legal.cases.view` | legal | platform_admin, tenant_admin, coordinator, agent con permiso | Abogado solo casos asignados | KPIs juridicos. |
| legal | `GET /api/legal/kanban` | `legal.cases.view` | legal | platform_admin, tenant_admin, coordinator, agent con permiso | Abogado solo casos asignados | Usa workflow juridico si existe. |
| legal | `GET /api/legal/cases/{id}/progress` | `legal.cases.view` | legal | platform_admin, tenant_admin, coordinator, agent con permiso | Valida caso del tenant/asignacion | Avance procesal. |
| legal | `GET /api/legal/cases/{id}/timeline` | `legal.cases.view` | legal | platform_admin, tenant_admin, coordinator, agent con permiso | Valida caso del tenant/asignacion | Timeline de expediente. |
| sales | `GET /api/sales/dashboard` | `sales.leads.view` | sales | platform_admin, tenant_admin, coordinator, agent con permiso | Asesor comercial solo asignado | KPIs comerciales. |
| sales | `GET /api/sales/pipeline` | `sales.opportunities.view` | sales | platform_admin, tenant_admin, coordinator, agent con permiso | Asesor comercial solo asignado | Valor por etapa. |
| sales | `GET /api/sales/kanban` | `sales.opportunities.view` | sales | platform_admin, tenant_admin, coordinator, agent con permiso | Asesor comercial solo asignado | Kanban comercial. |

## Actualizacion Fase 8B - Collection CRM operativo

| Modulo | Endpoint | Permiso requerido | Modulo requerido | Roles compatibles | Restricciones |
|---|---|---|---|---|---|
| crm | `POST /api/crm/customers/{id}/activities` | `crm.activities.create` fallback `crm.clients.update` | crm/collections | agent, coordinator, tenant_admin | cliente asignado para gestor |
| typifications | `GET /api/typifications/trees` | `typifications.view` | collections | tenant_admin, coordinator | filtra tenant |
| typifications | `POST /api/typifications/trees` | `typifications.trees.manage` | collections | tenant_admin | tenant/proyecto validado |
| typifications | `POST /api/typifications/combinations` | `typifications.combinations.manage` | collections | tenant_admin | path y arbol del mismo tenant |
| recordings | `GET /api/recordings` | `recordings.view` | collections | tenant_admin, coordinator, agent, auditor | filtra tenant y usuario si aplica |
| recordings | `GET /api/recordings/{id}/playback` | `recordings.playback` | collections | tenant_admin, coordinator, agent, auditor | audita acceso |
| recordings | `GET /api/recordings/{id}/download` | `recordings.download` | collections | tenant_admin | audita descarga |
| uploads | `POST /api/uploads/preview` | `uploads.view` | collections | tenant_admin, coordinator | no persiste archivo real |
| uploads | `POST /api/uploads/confirm` | `uploads.manage` / especifico | collections | tenant_admin, coordinator | registra lote y auditoria |
| uploads | `GET /api/uploads/demographics` | `demographics.view` | collections | tenant_admin, coordinator, agent | filtra tenant |
| excel_web | `POST /api/excel-web/query` | `excel_web.query` | bi | tenant_admin, coordinator, agent | fuentes seguras, sin SQL libre |
| excel_web | `POST /api/excel-web/export` | `excel_web.export` | bi | tenant_admin | registra export log |
| integrations | `GET /api/integrations/providers` | `integrations.providers.view` | integrations | tenant_admin | secretos enmascarados |
| integrations | `POST /api/integrations/channels/{id}/test` | `integrations.channels.update` | integrations | tenant_admin | prueba simulada |
