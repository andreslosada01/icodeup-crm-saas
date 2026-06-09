# Matriz de permisos pre-productiva

## Criterio de validacion

Cada entrada debe cumplir tres controles:

1. El menu solo aparece si el modulo esta activo y el usuario tiene permiso.
2. El endpoint valida permiso en backend.
3. El alcance tenant/ownership se valida aunque el usuario manipule parametros.

| Permiso | Modulo | Endpoints principales | Roles que lo tienen | Roles que no lo deben tener | Estado |
| --- | --- | --- | --- | --- | --- |
| platform.governance.view | core | /api/governance/*, /api/admin/* | platform_admin | tenant_admin, coordinator, agent, lawyer, sales_advisor | Validado por tests |
| health.view | core | /api/health, seccion salud | platform_admin | operativos sin permiso | Validado funcional |
| tenant.settings.view | administration | /api/governance/settings | tenant_admin | agent, lawyer, sales_advisor | Validado por menu |
| users.view/users.manage | administration | /api/governance/users, /api/admin/users | tenant_admin, platform_admin | agent, lawyer, sales_advisor | Validado por menu/endpoints |
| roles.view/roles.manage | administration | /api/governance/roles | tenant_admin, platform_admin | agent, lawyer, sales_advisor | Validado por tests 403 |
| modules.view/modules.configure | administration | /api/governance/modules, /api/subscriptions/modules | tenant_admin lectura, platform_admin configura | operativos | Validado funcional |
| teams.view/teams.manage | administration | /api/teams/* | tenant_admin, collections_leader | agent sin admin | Validado por tests |
| crm.clients.view | crm | /api/crm/customers | tenant_admin, leader, agent, lawyer, sales | roles sin CRM | Validado por tests |
| crm.clients.export | crm | /api/crm/customers/export | admin autorizado | agent, lawyer, sales_advisor | Validado por tests |
| crm.activities.create | crm | /api/crm/customers/{id}/activities | agent, leader, tenant_admin | roles sin operacion | Validado por E2E gestor |
| collections.queue.view | collections | /api/crm/customers?queue, dashboard cola | tenant_admin, leader, agent | lawyer, sales_advisor | Validado por menu |
| collections.promises.view/create/update | collections | /api/crm/promises | tenant_admin, leader, agent | lawyer, sales_advisor | Validado funcional |
| collections.payments.view/create/export | collections | /api/crm/payments | tenant_admin, leader, agent crea segun permiso | lawyer/sales sin export | Validado por tests |
| collections.agreements.view/create/update | collections | /api/crm/agreements | tenant_admin, leader, agent segun permiso | perfiles sin cobranza | Validado funcional |
| uploads.view/preview/confirm/download | collections | /api/uploads/* | tenant_admin, leader autorizado | agent, lawyer, sales_advisor | Validado por tests |
| demographics.view/manage | collections | /api/uploads/demographics | tenant_admin, leader autorizado | roles sin permiso | Validado funcional |
| legal.cases.view/create/update | legal | /api/legal/cases | tenant_admin, legal_director, lawyer | sales_advisor, agent sin permiso | Validado por tests |
| legal.deadlines.view | legal | /api/legal/deadlines | abogado, legal_director, tenant_admin | sales_advisor | Validado funcional |
| documents.view/create/update | documents | /api/documents | tenant_admin, lawyer segun permiso | sales_advisor sin documents | Validado por tests |
| sales.leads.view/create/update | sales | /api/sales/leads | sales_leader, sales_advisor, tenant_admin | lawyer, agent sin sales | Validado por tests |
| sales.opportunities.view/create/update | sales | /api/sales/opportunities | sales_leader, sales_advisor, tenant_admin | lawyer, agent sin sales | Validado por tests |
| excel_web.view/query | bi | /api/excel-web/query | tenant_admin, leader, agent | roles sin BI | Validado por tests |
| audit.logs.view | administration | /api/governance/audit-logs | platform_admin, tenant_admin | agent, lawyer, sales_advisor | Validado funcional |

## Observaciones

- `User.role` se mantiene como fallback legacy. La fuente principal debe seguir migrando a `UserProfile.role_id` + `RolePermission`.
- Los permisos de exportacion deben revisarse antes de habilitar clientes reales.
- Platform admin conserva visibilidad global por diseno SaaS.
