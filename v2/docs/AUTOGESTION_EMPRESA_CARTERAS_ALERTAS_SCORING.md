# Autogestion Empresa, Carteras, Alertas y Scoring

## Objetivo

Sprint A incorpora una capa de autogestion operativa para IEP / Collects 360 sin crear un modulo paralelo ni duplicar tablas. La empresa contratante puede administrar carteras, lideres, gestores, reglas de scoring y alertas de inicio usando la estructura existente de tenant, proyectos, usuarios, roles, permisos y asignaciones.

## Jerarquia Operativa

1. Icodeup Advisors / IEP administra el SaaS general, empresas, licencias, modulos y gobierno global.
2. Cada empresa contratante opera dentro de su `tenant_id`.
3. Cada empresa puede tener multiples carteras o proyectos en `projects`.
4. Cada cartera puede tener clientes, obligaciones, lideres, gestores, reglas, alertas, reportes y futuras campanas.
5. Lideres y gestores pueden pertenecer a varias carteras mediante `user_project_assignments`.

## Modelos Reutilizados

- `tenants`: empresa contratante.
- `projects`: cartera o proyecto operativo.
- `users`, `roles`, `permissions`, `user_profiles`: identidad, perfiles y permisos.
- `user_project_assignments`: asignacion flexible usuario-cartera-rol-estado.
- `business_rules`: reglas configurables de scoring de gestiones.
- `alert_rules`: parametros de alertas por empresa o globales.
- `workflow_definitions`, `workflow_stages`: base para estados y flujos operativos.
- `management_activities`: gestiones registradas por cliente, obligacion y usuario.
- `payment_promises`, `payments`, `payment_agreements`: compromisos, pagos y acuerdos.
- `customer_obligations`: obligaciones detalladas.
- `tenant_modules`: modulos activos o pendientes de configuracion.

No se agregaron migraciones en Sprint A.

## Endpoints

- `GET /api/teams/operational-center`: centro operativo por tenant/cartera con carteras, asignaciones, modulos, reglas de scoring, alertas y resumen de usuarios.
- `GET /api/teams/users/{user_id}/projects`: carteras asignadas a un usuario.
- `POST /api/teams/projects/{project_id}/users`: crea o reactiva asignacion usuario-cartera.
- `PATCH /api/teams/project-users/{assignment_id}`: activa/desactiva o cambia rol operativo.
- `GET /api/alerts/session-summary`: prioridades de inicio por rol.
- `GET /api/crm/customers/{customer_id}/management-insights`: mejores gestiones del cliente.
- `GET /api/crm/users/{user_id}/management-insights`: resumen de scoring/productividad del asesor.

Todos los endpoints respetan `tenant_id`, alcance por rol, permisos existentes y limite visible de 10 filas cuando aplica.

## Flujos por Rol

### Admin IEP / Platform Admin

- Puede consultar empresas y operar con `tenant_id` cuando entra en soporte operativo.
- Ve centro operativo de la empresa seleccionada.
- Puede detectar carteras sin lider, sin gestores, modulos pendientes y alertas criticas.

### Admin Empresa

- Administra carteras de su tenant.
- Asigna lideres y gestores por cartera.
- Consulta reglas de scoring y alertas activas.
- Ve usuarios activos, inactivos y sin asignacion.

### Lider / Coordinador

- Ve carteras donde tiene asignacion activa o equipo directo.
- Consulta cartera, equipo, ranking y prioridades del dia.
- Detecta gestores sin actividad, clientes sin gestion, promesas por vencer y clientes sin responsable.

### Gestor / Asesor

- Ve solo clientes y carteras asignadas.
- Recibe prioridades de inicio: clientes sin gestion del mes, promesas vencidas/proximas, saldos altos sin contacto y buenas gestiones del mes anterior sin continuidad.
- Consulta mejores gestiones del cliente en drawer operativo.

## Scoring de Gestiones

El scoring lee reglas activas en `business_rules` con:

- `module`: `collections` o `crm`
- `rule_type`: `management_scoring` o `activity_scoring`
- `condition_json`: condiciones por resultado, canal, saldo, mora, riesgo u obligacion.
- `action_json`: puntos configurables mediante `score` o `points`.

Ejemplo:

```json
{
  "condition_json": { "result_contains_any": ["promesa", "acuerdo"], "channel_any": ["phone", "whatsapp"] },
  "action_json": { "score": 80 }
}
```

Si el tenant aun no tiene reglas activas, el servicio usa una base de emergencia marcada como `fallback` para no dejar la UI vacia. La recomendacion es parametrizar reglas reales desde el Centro de Configuracion.

Etiquetas:

- `excelente`: 85+
- `alta`: 65-84
- `media`: 40-64
- `baja`: menos de 40

## Mejores Gestiones

Para cada cliente se exponen:

- mejor gestion del mes actual.
- mejor gestion del mes anterior.
- mejor gestion historica.
- ultimas gestiones puntuadas.

Para asesor se exponen:

- actividades de hoy.
- actividades del mes.
- gestiones efectivas del mes.
- promesas, pagos y acuerdos del mes.
- mejor gestion actual e historica.

## Alertas de Inicio

`GET /api/alerts/session-summary` agrupa prioridades por rol y usa `alert_rules` para umbrales:

- `max_days_without_management`
- `min_effective_score`
- `promise_due_in_days`
- `min_critical_balance`
- `min_critical_dpd`

Si no hay reglas, se aplican valores de referencia para mostrar prioridades. La UI lo consume como dato opcional: si falla por modulo, permiso o reinicio temporal, no cierra sesion.

## UX/UI Implementada

- Panel `Prioridades de hoy` en dashboard, cerrable por dia.
- Centro operativo dentro de `Equipos y carteras`.
- Selector de cartera activa.
- KPIs de cartera, clientes, obligaciones y saldo.
- Chips de modulos activos/inactivos.
- Lista de reglas de scoring y alertas parametrizadas.
- Acciones rapidas para activar/desactivar asignaciones y cambiar rol a lider/agente.
- Drawer de cliente con mejores gestiones.

## Hardening QA por Rol

- El asesor/agente operativo no ve el catalogo corporativo de modulos en el dashboard.
- El nav lateral del agente oculta `Documentos`, `Telefonia` y `Mi Excel Web` como modulos independientes.
- Telefonia se mantiene como accion operativa de click-to-call cuando el modulo y la extension estan disponibles.
- Documentos se mantienen como soporte asociado al cliente dentro del drawer, no como modulo corporativo del agente.
- `Equipos y carteras` acepta modulo `administration` o `collections`, evitando pantallas vacias para lideres operativos cuando no tienen licenciamiento administrativo completo.
- `role_in_project` soporta roles explicitos: `admin`, `coordinator`, `leader`, `agent`, `quality`, `quality_supervisor`, `lawyer`, `sales`, `auditor`, `viewer`.
- Las carteras cuentan `leader` y `coordinator` como liderazgo operativo para evitar falsos positivos de "cartera sin lider".

## Reglas Demo de Scoring

Los defaults y el seed TEST incluyen reglas idempotentes con `rule_type='scoring'` para:

- contacto efectivo.
- promesa creada.
- pago reportado.
- acuerdo creado.
- escalamiento juridico.
- no contesta.
- numero errado.
- cliente sin contacto.
- soporte cargado.

Estas reglas viven en `business_rules`, son editables por configuracion y evitan que el scoring dependa exclusivamente del fallback de lectura.

Cuando existen reglas globales (`tenant_id IS NULL`) y reglas del tenant con el mismo `code`, el servicio prioriza la regla del tenant y no duplica la regla global en la UI. Prioridad: tenant > global fallback. La regla global queda como fallback para tenants que todavia no tienen parametrizacion propia.

## Asignaciones Demo por Cartera

Los seeds TEST no deben activar todos los usuarios en todas las carteras. Para usuarios demo con cartera identificable en el correo, por ejemplo `agente1.<tenant>.finlosada@demo.icodeup.local`, el seed:

- activa solo la cartera cuyo codigo/nombre coincide con el sufijo del correo.
- desactiva (`is_active=false`) asignaciones demo cruzadas.
- no elimina filas para conservar trazabilidad.
- no modifica asignaciones de usuarios no-demo o de usuarios demo donde no se puede inferir con seguridad la cartera.

Admins tenant pueden quedar como `admin` en varias carteras para administracion. La productividad y los conteos de asesores excluyen `admin`, `coordinator` y `quality_supervisor`; solo `role_in_project='agent'` cuenta como asesor operativo.

## QA Checklist

- SuperAdmin en soporte operativo ve centro de la empresa seleccionada.
- Admin empresa ve solo su tenant.
- Lider ve carteras/equipo dentro de su alcance.
- Gestor no puede modificar asignaciones.
- Gestor no ve tarjetas de modulos corporativos o licenciamiento en dashboard.
- Gestor no ve Documentos/Telefonia/Excel como modulos laterales independientes.
- Crear asignacion no duplica `user_project_assignments`.
- Desactivar asignacion mantiene trazabilidad y no borra datos.
- Cambiar rol actualiza `role_in_project` y mantiene `tenant_id`.
- Coordinador queda como `coordinator` o `leader`; calidad queda como `quality_supervisor` o `quality`; admin empresa no queda como `agent` por seed/demo.
- Usuarios demo con sufijo de cartera no quedan activos en carteras cruzadas.
- Reglas de scoring se muestran sin duplicar global/tenant; tenant tiene prioridad sobre global.
- `session-summary` no cierra sesion ante 403/503 cuando se consume opcionalmente desde frontend.
- Drawer muestra mejores gestiones cuando existen actividades.
- Todas las tablas visibles mantienen maximo 10 filas.

## Riesgos

- El modelo actual no guarda `assigned_by` en `user_project_assignments`; la trazabilidad de quien asigno queda en auditoria.
- `AlertRule.threshold_days` se reutiliza como umbral numerico tambien para balance y mora, aunque el nombre historico del campo diga `days`.
- El scoring historico se calcula en lectura; para grandes volumenes puede requerir cache o persistencia posterior.
- Reglas de scoring reales dependen de parametrizacion en `business_rules`.

## Siguientes Fases

1. UI CRUD guiada para reglas de scoring con condiciones visuales.
2. Persistencia opcional del score en nuevas columnas si el volumen lo exige.
3. Campanas y tareas asignadas por cartera.
4. Reportes comparativos de mejores gestiones por asesor, cartera y mes.
5. Auditoria visual de cambios en asignaciones por cartera.
6. SLA y calendarios de seguimiento integrados con CareFlow 360.

## Recomendacion de Implementacion

Mantener Sprint A como capa incremental: leer y escribir solo sobre tablas existentes, preservar endpoints actuales y usar `business_rules` / `alert_rules` como fuente configurable. Cualquier persistencia adicional debe entrar en una migracion posterior, justificada por rendimiento o trazabilidad formal.
