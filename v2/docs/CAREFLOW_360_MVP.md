# CareFlow 360 MVP

## Objetivo

CareFlow 360 es el modulo activable de IEP para atencion al cliente, casos, solicitudes, SLA y seguimiento omnicanal. Complementa Collects 360 sin reemplazar cobranzas, pagos, telefonia, documentos ni reportes existentes.

## Alcance MVP

- Crear y consultar casos de atencion por tenant.
- Asociar caso opcionalmente a cartera (`project_id`) y cliente (`customer_id`).
- Asignar responsable operativo.
- Controlar estado, prioridad, canal, categoria y vencimiento/SLA.
- Registrar historial de eventos/notas.
- Cerrar o resolver casos.
- Mostrar resumen y alertas si el modulo esta activo.
- Mantener `page_size` maximo 10.

## Modelos y Tablas

- `care_cases`: caso principal con `tenant_id`, `project_id`, `customer_id`, `case_number`, titulo, descripcion, canal, tipo/categoria, prioridad, estado, responsable, creador, cierre, SLA y metadata.
- `care_case_events`: historial auditable de notas, asignaciones, cambios de estado, cierres, reaperturas o adjuntos.
- `care_case_categories`: categorias operativas por tenant con prioridad y SLA por defecto.

La migracion es no destructiva y no elimina datos en `downgrade`.

## Endpoints

- `GET /api/careflow/cases`
- `GET /api/careflow/cases/{id}`
- `POST /api/careflow/cases`
- `PATCH /api/careflow/cases/{id}`
- `POST /api/careflow/cases/{id}/events`
- `POST /api/careflow/cases/{id}/assign`
- `POST /api/careflow/cases/{id}/close`
- `GET /api/careflow/summary`
- `GET /api/careflow/categories`
- `POST /api/careflow/categories`

Filtros disponibles en listado: `status`, `priority`, `channel`, `assigned_user_id`, `project_id`, `customer_id`, `search`, `page`, `page_size`.

## Roles y Permisos

- `platform_admin`: acceso global y configuracion, con posibilidad de acotar por `tenant_id`.
- `tenant_admin`: todos los casos del tenant, configuracion, reportes y asignacion.
- `coordinator`: casos de sus carteras, equipo, casos creados por el o sin responsable dentro del alcance operativo.
- `agent`: solo casos asignados a el o creados por el; puede crear, actualizar, agregar notas y cerrar casos de su alcance.
- `quality_supervisor`: lectura/evaluacion y notas, sin administracion destructiva.

Permisos base:

- `careflow.view`
- `careflow.create`
- `careflow.update`
- `careflow.assign`
- `careflow.close`
- `careflow.events.create`
- `careflow.configure`
- `careflow.reports.view`

## Flujo Operativo

1. El tenant contrata/activa `careflow` en `tenant_modules`.
2. El usuario ve el menu CareFlow segun su audiencia.
3. Un admin, lider o agente crea un caso.
4. El caso se puede asignar, comentar, actualizar y cerrar.
5. El historial queda en `care_case_events`.
6. Resumen y prioridades se actualizan sin mezclar tenants.

## Integracion con Alertas

CareFlow se agrega a `Prioridades de hoy` y `/api/alerts` solo cuando `tenant_modules.careflow` esta activo.

- Agente: casos vencidos, proximos a vencer y nuevos asignados.
- Coordinador: vencidos del equipo, casos sin responsable y criticos abiertos.
- Admin tenant: vencidos, sin asignacion y volumen critico.

## Seed TEST

Seed seguro:

```powershell
cd v2/backend
.\.venv\Scripts\python.exe -m app.seeds.careflow_demo --tenant-slug andina-servicios-financieros --confirm-test
```

Modo inspeccion:

```powershell
.\.venv\Scripts\python.exe -m app.seeds.careflow_demo --tenant-slug andina-servicios-financieros --dry-run
```

El seed:

- crea/actualiza `modules.code='careflow'`.
- activa `tenant_modules.careflow` para el tenant demo.
- crea categorias base.
- crea casos `CF-DEMO-001` a `CF-DEMO-004`.
- crea eventos demo idempotentes.
- no borra datos y no escribe sin `--confirm-test`.

## Checklist QA

- El modulo no aparece en menu si `tenant_modules.careflow` esta desactivado.
- `GET /api/careflow/cases?page_size=50` debe rechazar o limitar por validacion `le=10`.
- Agente no ve configuracion CareFlow.
- Agente solo ve casos asignados o creados por el.
- Coordinador ve casos de equipo/cartera y sin responsable dentro de su alcance.
- Tenant admin ve todos los casos de su tenant.
- Platform admin no mezcla tenants cuando filtra por `tenant_id`.
- Crear caso exige `tenant_id` valido cuando aplica.
- Asignar responsable valida que el usuario sea del mismo tenant.
- Cliente/cartera deben pertenecer al tenant del caso.
- Prioridades CareFlow no aparecen si el modulo esta inactivo.

## Siguientes Fases

- Adjuntos reales conectados a Documentos.
- SLA configurable por categoria y calendario laboral.
- Encuestas/calidad de atencion.
- Integracion con ChatBOX 360 y WhatsApp/EIKO.
- Automatizaciones por cambio de estado.
- Dashboard avanzado por canal, categoria, responsable y tiempo de resolucion.
- Exportaciones operativas y auditoria de SLA.
