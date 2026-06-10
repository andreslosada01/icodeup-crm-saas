# Matriz Tenant ID por Modelos SaaS

Fecha: 2026-06-10  
Rama auditada: `feature/deploy-test-server`

## Criterio

En el modelo actual `shared_schema`, todo registro operativo debe tener `tenant_id` directo o pertenecer a una entidad padre que lo tenga y sea validada por endpoint/servicio.

## Matriz principal solicitada

| Modelo / tabla | Tiene tenant_id | Motivo si no tiene | Riesgo | Correccion recomendada | Bloqueante produccion |
|---|---|---|---|---|---|
| Tenant / `tenants` | No | Es la raiz de tenancy. | Bajo | Mantener `slug` unico y estado. | No |
| TenantConfiguration / `tenant_configurations` | Si | N/A | Bajo | Mantener unique `(tenant_id, key)`. | No |
| TenantModule / `tenant_modules` | Si | N/A | Bajo | Mantener validacion de modulo activo. | No |
| TenantSubscription / `tenant_subscriptions` | Si | N/A | Bajo | Mantener suscripcion por tenant. | No |
| User / `users` | Si | N/A | Bajo | Mantener `tenant_id` obligatorio. | No |
| UserProfile / `user_profiles` | Si | Nullable por compatibilidad/plataforma. | Bajo/Medio | En futura migracion, validar perfiles sin tenant salvo plataforma. | No |
| Role / `roles` | Si | Nullable para roles globales de sistema. | Bajo | Mantener roles globales solo Icodeup. | No |
| Permission / `permissions` | No | Catalogo global de permisos. | Bajo | Mantener codigos unicos. | No |
| RolePermission / `role_permissions` | No | Pivot por `role_id`; hereda tenant de Role. | Bajo/Medio | Auditar que roles tenant no mezclen permisos reservados. | No |
| Project / `projects` | Si | N/A | Bajo | Mantener unique `(tenant_id, code)`. | No |
| UserProjectAssignment / `user_project_assignments` | Si | Nullable historico en modelo/migracion de compatibilidad. | Medio | En futura migracion, hacer `tenant_id` NOT NULL tras limpieza. | No para test |
| Customer / `customers` | Si | N/A | Bajo | Mantener filtros por tenant y asignacion. | No |
| CustomerObligation / `customer_obligations` | Si | N/A | Bajo | Mantener unique `(tenant_id, obligation_number)`. | No |
| ManagementActivity / `management_activities` | Si | N/A | Bajo | Mantener validacion por cliente/obligacion. | No |
| PaymentPromise / `payment_promises` | Si | N/A | Bajo | Mantener acceso por cliente visible. | No |
| Payment / `payments` | Si | N/A | Bajo | Mantener export seguro por cliente visible. | No |
| PaymentAgreement / `payment_agreements` | Si | N/A | Bajo | Mantener acceso por cliente visible. | No |
| PaymentAgreementInstallment / `payment_agreement_installments` | No | Hijo de `payment_agreements`. | Bajo/Medio | Opcional: agregar `tenant_id` redundante para auditoria/reportes. | No |
| Document / `documents` | Si | N/A | Bajo | Mantener validacion de relaciones cruzadas. | No |
| CustomerDemographic / `customer_demographics` | Si | N/A | Bajo | Mantener customer del mismo tenant. | No |
| UploadBatch / `upload_batches` | Si | N/A | Bajo | Mantener `_resolve_scope` y descargas por batch. | No |
| OperationalFile / `operational_files` | Si | N/A | Bajo | Mantener storage path por tenant. | No |
| SavedDataView / `saved_data_views` | Si | N/A | Bajo | Mantener vista publica solo dentro del tenant. | No |
| DataExportLog / `data_export_logs` | Si | N/A | Bajo | Mantener logs de export por tenant. | No |
| IntegrationProvider / `integration_providers` | Si | N/A | Bajo | Mantener secretos enmascarados. | No |
| ChannelConfiguration / `channel_configurations` | Si | N/A | Bajo | Validar proveedor del mismo tenant si aplica. | No |
| CommunicationTemplate / `communication_templates` | Si | N/A | Bajo | Mantener plantillas por tenant. | No |
| WebhookConfiguration / `webhook_configurations` | Si | N/A | Bajo/Medio | En produccion cifrar secretos reales. | No para test |
| Alert / `generated_alerts` | Si | N/A | Bajo | Mantener filtros por usuario/tenant. | No |
| LegalCase / `legal_cases` | Si | N/A | Bajo | Mantener customer y abogado del mismo tenant. | No |
| SalesLead / `leads` | Si | N/A | Bajo | Mantener asignacion por tenant. | No |
| Opportunity / `opportunities` | Si | N/A | Bajo | Mantener lead/customer del mismo tenant. | No |
| AuditLog / `audit_logs` | Si | Nullable para eventos plataforma o login fallido. | Bajo | Mantener redaccion de campos sensibles. | No |

## Modelos adicionales detectados

| Modelo / tabla | Tiene tenant_id | Motivo si no tiene | Riesgo | Recomendacion |
|---|---|---|---|---|
| SaasPlan / `saas_plans` | No | Catalogo comercial global. | Bajo | Solo platform admin modifica. |
| Module / `modules` | No | Catalogo global de modulos. | Bajo | Solo platform admin modifica activaciones. |
| MenuItem / `menu_items` | No | Catalogo global de navegacion. | Bajo | Visibilidad por audiencia, modulo y permiso. |
| Party / `parties` | Si | N/A | Bajo | Usar como tercero maestro futuro. |
| TypificationNode / `typification_nodes` | Si | N/A | Bajo | Mantener tipificaciones por tenant/proyecto. |
| TypificationTree / `typification_trees` | Si | N/A | Bajo | Mantener arbol por tenant/proyecto/modulo. |
| TypificationTreeNode / `typification_tree_nodes` | No | Hijo de `typification_trees`. | Bajo/Medio | Validar siempre el arbol padre. |
| TypificationCombinationRule / `typification_combination_rules` | Si | N/A | Bajo | Mantener tree del mismo tenant. |
| FunctionalCatalog / `functional_catalogs` | Si | Puede ser global si `tenant_id` null. | Bajo | Solo Icodeup modifica globales. |
| BusinessRule / `business_rules` | Si | Puede ser global si `tenant_id` null. | Bajo | Solo Icodeup modifica globales. |
| AlertRule / `alert_rules` | Si | Puede ser global si `tenant_id` null. | Bajo | Solo Icodeup modifica globales. |
| WorkflowDefinition / `workflow_definitions` | Si | Puede ser global si `tenant_id` null. | Bajo | Validar modificaciones globales. |
| WorkflowStage / `workflow_stages` | No | Hijo de `workflow_definitions`. | Bajo/Medio | Validar workflow padre. |
| WorkflowTransition / `workflow_transitions` | No | Hijo de `workflow_definitions`. | Bajo/Medio | Validar workflow padre. |
| LegalAction / `legal_actions` | Si | N/A | Bajo | Mantener caso del mismo tenant. |
| LegalHearing / `legal_hearings` | Si | N/A | Bajo | Mantener caso del mismo tenant. |
| LegalDeadline / `legal_deadlines` | Si | N/A | Bajo | Mantener caso del mismo tenant. |
| CallRecording / `call_recordings` | Si | N/A | Bajo/Medio | Storage real debe ser por tenant. |
| RecordingAccessLog / `recording_access_logs` | Si | N/A | Bajo | Mantener auditoria de reproduccion/descarga. |
| ChannelEventLog / `channel_event_logs` | Si | N/A | Bajo | Redactar payloads sensibles si entran integraciones reales. |
| OperationalSheetRow / `operational_sheet_rows` | Si | N/A | Bajo | Mantener filtros por usuario/equipo/proyecto. |
| ImportBatch / `import_batches` | Si | N/A | Bajo | Mantener CSV fuera de auditoria completa. |

## Hallazgos clave

1. La cobertura de `tenant_id` es alta en las entidades operativas.
2. Las tablas globales sin `tenant_id` son esperadas para un SaaS con catalogos comunes.
3. Las tablas hijas sin `tenant_id` directo dependen de validacion del padre. No bloquean servidor test, pero se recomienda agregar `tenant_id` redundante a cuotas, nodos y workflows si crece el volumen o la auditoria regulatoria.
4. `UserProjectAssignment.tenant_id` aun es nullable por compatibilidad; conviene endurecerlo en una migracion futura.
5. El modelo es compatible con shared schema productivo inicial.
