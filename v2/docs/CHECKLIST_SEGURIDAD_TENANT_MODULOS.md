# Checklist Seguridad Tenant y Modulos

## Autenticacion

- Login exitoso retorna token y datos de tenant.
- Login fallido retorna 401.
- Usuario inactivo no puede iniciar sesion.
- Token invalido no permite acceder a APIs protegidas.

## Tenant

- Usuario cliente solo consulta registros de su `tenant_id`.
- Admin empresa no puede consultar datos de otra empresa usando parametros por URL.
- Agent solo ve clientes asignados cuando aplica.
- Platform admin puede ver gobierno global.
- Admin empresa no puede acceder a `/api/admin/tenants`.

## Modulos

- Modulo activo aparece en `/api/menu/me`.
- Modulo inactivo no aparece en `/api/menu/me`.
- Acceso por URL a modulo inactivo retorna 403.
- Rutas de CRM validan modulo `crm`.
- Rutas juridicas validan modulo `legal`.
- Rutas documentales validan modulo `documents`.
- Rutas comerciales validan modulo `sales`.

## Permisos

- Menu respeta `required_permission_code`.
- Menu respeta `required_permission`.
- Platform admin tiene permisos globales.
- Admin empresa ve solo menu de empresa.
- Lider ve menu operativo autorizado.
- Usuario operativo ve solo su operacion.
- Usuario sin permiso recibe 403 aunque intente entrar por URL.
- Permisos por accion validan `view`, `create`, `update`, `export`, `assign` y `configure` segun modulo.

## Gobierno SaaS vs tenant

- SuperAdmin ve `governance`, `plans`, `subscriptions`, `modules`, `audit` y `system-health`.
- Admin Empresa no ve `governance`, `plans`, `subscriptions` ni `system-health`.
- Admin Empresa ve `tenant-settings`, `company-users`, `roles-permissions`, `tenant-modules`, `branding` y auditoria de su tenant.
- Usuario operativo no ve secciones administrativas.
- Admin Empresa no puede activar modulos por URL.

## Exportes

- `/api/crm/customers/export` exige `crm.clients.export`.
- `/api/crm/payments/export` exige `collections.payments.export`.
- Agent recibe 403 en exportes si no tiene permiso.
- Admin Empresa exporta solo datos de su tenant.
- Platform admin puede exportar globalmente o filtrar por tenant cuando la ruta lo permita.

## Auditoria

- Crear usuario registra auditoria.
- Crear rol registra auditoria.
- Asignar rol registra auditoria.
- Cambiar permisos de rol registra auditoria.
- Cambiar branding/configuracion tenant registra auditoria.
- Activar/desactivar modulo registra auditoria.
- Crear tercero maestro registra auditoria.
- Crear cliente registra auditoria.
- Importar clientes registra auditoria.
- Crear promesa registra auditoria.
- Crear pago registra auditoria.
- Crear acuerdo registra auditoria.
- Crear documento registra auditoria.
- Crear lead registra auditoria.
- Crear oportunidad registra auditoria.

## Frontend

- Menu lateral se construye desde `/api/menu/me`.
- No se muestran modulos no autorizados.
- Dashboard inicial cambia por tipo de usuario.
- Login usa posicionamiento Icodeup 360 y no textos de cobranzas.
- Branding aplica colores de tenant cuando existen.

## Regresion

- Dashboard CRM existente carga.
- Cola de gestion carga.
- Clientes carga.
- Promesas carga.
- Pagos carga.
- Acuerdos responde.
- Juridico responde.
- Documentos responde.
- Ventas responde.
- Reportes BI responde.

## Fase 3 - Matriz por experiencia

| Experiencia | Debe ver | Debe bloquear |
| --- | --- | --- |
| SuperAdmin Icodeup | Gobierno SaaS, tenants, planes, suscripciones, modulos, auditoria global, salud | Nada global si no esta autenticado |
| Admin Empresa | Mi empresa, usuarios, roles, permisos, modulos contratados, branding, auditoria tenant, reportes tenant | Gobierno global, inventario comercial global, activar modulos por URL |
| Usuario Operativo | Inicio, cola, clientes/terceros autorizados, tareas, documentos y reportes permitidos | Gobierno, roles, permisos, settings globales, exportes sin permiso |

## Fase 3 - Matriz por modulo

| Modulo | Validaciones obligatorias |
| --- | --- |
| core | usuario autenticado, tenant valido, menu por audiencia |
| administration | admin empresa o platform admin, tenant propio, permisos de configuracion |
| collections | modulo activo, permisos por accion, customer visible |
| legal | modulo activo, permisos juridicos, customer y abogado mismo tenant |
| documents | modulo activo, relaciones mismo tenant, limite storage |
| sales | modulo activo, permisos comerciales, asignacion/tenant |
| bi | permisos `reports.view` y `reports.export`, datos filtrados |
| integrations | permisos de canales, no exponer secretos |

## Fase 3 - Permisos criticos

- Exportes: requieren permiso `*.export` y filtro por tenant.
- Usuarios: crear/actualizar exige rol administrativo y limite de plan.
- Roles: clientes no asignan permisos `platform.*`, `modules.configure` ni `health.view`.
- Modulos: solo SuperAdmin Icodeup activa/desactiva.
- Auditoria: admin empresa solo ve su tenant.
- Juridico: casos y responsables deben pertenecer al mismo tenant.
- Documentos: metadata valida relaciones y no cruza tenants.

## Fase 3 - Validaciones obligatorias

- Aislamiento por tenant en query params y relaciones.
- Modulo activo antes de permitir URL directa.
- Permiso activo antes de accion.
- Rol/perfil compatible como fallback legacy.
- Ownership/asignacion para agente.
- No fuga por `tenant_id` en exportes.
- No fuga documental por `customer_id`, `legal_case_id`, `payment_id` o `agreement_id`.
- Auditoria sin passwords, tokens, secretos ni payload CSV completo.

## Pre-merge a main

- `python -m compileall .\v2\backend\app`
- `node --check .\v2\frontend\static\assets\app.js`
- `pytest`
- Backend local inicia en `http://127.0.0.1:8020/`
- `/api/health` responde.
- Login por SuperAdmin, Admin Empresa y Agent.
- Menu por rol correcto.
- Modulo desactivado no aparece y bloquea URL.
- Exportes de clientes y pagos requieren permiso.
- Auditoria registra login, exportes y cambios criticos.
- No versionar `.env`, bases locales, logs, media real ni secretos.
## Checklist adicional Fase 8

- Validar que `GET /api/configuration/catalogs` responda solo a perfiles con `configuration.view`.
- Validar que Admin Empresa no cree ni modifique configuraciones de otro tenant.
- Validar que Admin Empresa no pueda modificar plantillas globales `tenant_id = null`.
- Validar que `GET /api/alerts` no exponga alertas de otro tenant.
- Validar que agente vea solo alertas asignadas o de su operacion.
- Validar que abogado vea alertas/casos juridicos asignados o permitidos.
- Validar que comercial vea pipeline propio o tenant segun permisos.
- Validar que `GET /api/legal/cases/{id}/timeline` bloquee casos de otro tenant.
- Validar que `GET /api/legal/kanban` use solo casos visibles.
- Validar que `GET /api/sales/pipeline` y `GET /api/sales/kanban` respeten asignacion y tenant.
- Validar que Centro de Configuracion no aparezca en menu de usuarios operativos sin permiso.
- Validar que Alertas aparezca solo con `alerts.view`.
- Validar que el badge de alertas no bloquee navegacion ni rompa responsive.

## Checklist adicional Fase 8B

- Validar que el gestor solo registre gestiones sobre clientes asignados.
- Validar que `crm.activities.create` no habilite edicion global de clientes.
- Validar que arboles y combinaciones de tipificacion no crucen tenant/proyecto.
- Validar que grabaciones no expongan `recording_url` sin permiso de playback/download.
- Validar que cada playback/download de grabacion registre log.
- Validar que cargas no persistan archivos reales ni CSV completo en auditoria.
- Validar que demograficos no dupliquen datos identicos por cliente/fuente.
- Validar que Mi Excel Web no permita SQL libre.
- Validar que exportes de Mi Excel Web requieran `excel_web.export`.
- Validar que integraciones enmascaren secretos y usen pruebas simuladas.
