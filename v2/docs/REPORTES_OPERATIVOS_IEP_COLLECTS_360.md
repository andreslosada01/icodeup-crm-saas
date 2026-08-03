# Reportes operativos IEP / Collects 360

## Alcance

Sprint D agrega un centro de reportes operativos dentro de Analytics 360 para consultar datos clave de Collects 360 sin crear tablas nuevas ni migraciones. Los reportes reutilizan clientes, obligaciones, gestiones, promesas, pagos, acuerdos, demograficos, llamadas, asignaciones activas por cartera y casos CareFlow cuando el modulo esta activo.

## Reportes incluidos

- Clientes: empresa, cartera, cliente, documento, estado, saldo, mora, riesgo, asesor, lider, ultima gestion, mejores gestiones, promesa, acuerdo y estado de contacto.
- Gestion: fecha, cliente, obligacion, asesor, lider, cartera, canal, tipificacion, resultado, resumen, score, efectividad, proxima fecha, promesa y cumplimiento de contacto.
- Promesas: cliente, obligacion, asesor, cartera, fecha, valor, estado, vencimiento, cumplimiento, pago asociado y dias vencidos.
- Pagos: cliente, obligacion, asesor, cartera, fecha, valor, origen, estado de validacion, referencia y relacion con promesa/acuerdo.
- Acuerdos: cliente, obligacion, asesor, cartera, fecha, valor, cuotas, cuotas pagadas, cuotas vencidas, estado y proximo vencimiento.
- Productividad por hora: fecha, hora, asesor, cartera, gestiones, llamadas, WhatsApp, email, promesas, pagos, acuerdos, contactos efectivos y score promedio.
- Productividad por asesor: asesor, cartera, gestiones dia/mes, contactos efectivos, promesas, pagos, acuerdos, mejores gestiones, score y efectividad.
- Demograficos/contactabilidad: cliente, telefonos, emails, direcciones, contactabilidad, prioridad, vigencia, ultimo canal, canal recomendado y restricciones.
- Tareas/agendados: usa `management_activities.next_contact_at` como fuente hasta formalizar un modelo de tareas.
- CareFlow 360: agregados por estado, prioridad, canal, responsable, vencidos SLA y tiempo promedio de resolucion si el modulo esta activo.

## Filtros

Filtros comunes: `tenant_id`, `project_id`, `user_id`, `advisor_id`, `leader_id`, `date_from`, `date_to`, `status`, `channel`, `risk`, `search`, `page` y `page_size`.

Filtros especializados: `min_score`, `effective`, `min_dpd`, `max_dpd`, `min_balance`, `max_balance`, `no_management`, `active_promise`, `contact_restriction`, `overdue` y `fulfilled`.

`page_size` esta limitado a maximo 10 en endpoints interactivos.

## Endpoints

- `GET /api/reports/operational/meta`
- `GET /api/reports/operational/clients`
- `GET /api/reports/operational/activities`
- `GET /api/reports/operational/promises`
- `GET /api/reports/operational/payments`
- `GET /api/reports/operational/agreements`
- `GET /api/reports/operational/productivity-hourly`
- `GET /api/reports/operational/productivity-advisor`
- `GET /api/reports/operational/demographics`
- `GET /api/reports/operational/tasks`
- `GET /api/reports/operational/careflow`
- `GET /api/reports/operational/{report_code}/export`

## Permisos por rol

- `platform_admin`: ve reportes globales y puede filtrar por empresa.
- `tenant_admin`: ve reportes de su empresa.
- `coordinator` / `collections_leader`: ve carteras activas asignadas y equipo bajo su liderazgo.
- `quality_supervisor` / `tenant_auditor`: ve lectura para auditoria/calidad, restringida a su empresa y carteras activas si existen.
- `agent` / `collections_agent`: no ve el centro completo de reportes operativos. Mantiene sus vistas operativas existentes.

Todos los endpoints requieren `reports.view` y modulo `bi` activo para perfiles no plataforma.

## Criterios de aislamiento

- Toda consulta parte de clientes visibles por `tenant_id`.
- Los reportes dependientes usan el subalcance visible de clientes antes de consultar gestiones, promesas, pagos, acuerdos, demograficos, tareas o llamadas.
- Lideres y coordinadores se limitan por equipo directo y `user_project_assignments.is_active = true`.
- La productividad por asesor excluye admins y calidad; solo cuenta usuarios `agent` con asignacion activa `role_in_project = "agent"`.
- CareFlow se muestra solo si el modulo esta activo para la empresa seleccionada.

## Exportacion

`/api/reports/operational/{report_code}/export` genera CSV usando los mismos filtros y permisos del endpoint interactivo. La exportacion queda acotada por seguridad y no mezcla tenants ni carteras.

## Limitaciones

- El reporte de tareas usa `management_activities.next_contact_at`; un modelo formal de tareas puede agregarse en una fase posterior.
- La relacion pago-promesa/acuerdo se infiere por cliente/obligacion cuando no existe llave formal.
- Algunos calculos de score usan reglas configurables actuales y fallback existente.

## Checklist QA

- Validar que `tenant_admin` solo vea su empresa.
- Validar que `coordinator` solo vea carteras activas y equipo autorizado.
- Validar que `quality_supervisor` tenga lectura y no aparezca como asesor productivo.
- Validar que `agent` no tenga menu `reports` ni pueda llamar `/api/reports/operational/*`.
- Validar que `page_size` mayor a 10 sea rechazado por FastAPI.
- Validar que CareFlow no aparezca en metadata si el modulo esta inactivo.
- Validar export CSV con los mismos filtros de pantalla.
- Validar que Analytics 360 predictivo siga cargando.

## Siguientes fases

- Modelo formal de tareas y agenda.
- Exportes asincronos con auditoria detallada y retencion.
- Plantillas de reportes guardadas por usuario.
- Dashboards de calidad y reporteria Ley 2300 avanzada.
- Cubos agregados para cargas con alto volumen.
