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
