# Benchmark CRMnex y roadmap IEP / Collects 360

Fecha de revision: 2026-08-02  
Producto destino: IEP - Icodeup Enterprise Platform  
Modulo principal: Collects 360  
Fuente revisada: `C:\Users\RALL2\Downloads\CRMnex.docx`

## 0. Nota de alcance

Este documento usa CRMnex como benchmark funcional y visual. No se debe copiar marca, identidad, nombres comerciales, composicion exacta, iconografia propietaria ni diseno especifico. La implementacion debe mantener la identidad de IEP - Icodeup Enterprise Platform, con la linea visual premium ya definida para Icodeup Advisors.

El archivo de referencia contiene poco texto editable y 48 capturas de pantalla. Las conclusiones se basan en observacion visual de esas capturas y en comparacion contra el estado actual del repositorio IEP.

## 1. Funcionalidades observadas en CRMnex

### 1.1 Home con campanas asignadas

- Pantalla inicial orientada al usuario operativo.
- Mensaje de bienvenida personalizado.
- Cards de campanas asignadas con marca de la entidad, estado activo y acceso directo.
- Buscador por nombre o ID de campana.
- Sensacion de "elige la operacion/campana y empieza a gestionar".

### 1.2 Perfil operativo del usuario

- Dashboard por usuario con KPIs de clientes, obligaciones, proyeccion y pagos.
- Grafica de productividad.
- Resumen de actividad de llamadas entrantes/salientes.
- Estado telefonico visible en topbar: proveedor, extension y disponibilidad.
- Alertas de permisos de microfono y estado de conexion.

### 1.3 Telefonia, extensiones, colas, grabaciones y reportes

- Hub de configuracion de telefonia.
- Gestion de extensiones.
- Gestion de colas y enrutamiento.
- Grabaciones.
- Encuestas post-llamada.
- Reporte de llamadas.
- Niveles de atencion.
- Reportes inbound.
- Monitor AMI en tiempo real con agentes, disponibilidad, espera, ocupacion, abandono, ACW, AHT y llamadas en cola.
- Botones de acciones de llamada desde cliente.

### 1.4 Administracion de usuarios, roles, permisos y sesion

- Gestion de usuarios con estado, rol, extension y acciones.
- Resumen de usuarios en linea, activos y desconectados.
- Filtros por rol y estado.
- Parametros de sesion por usuarios y administradores: tiempo de actividad, notificacion, espera y desconexion.
- Roles con cards por perfil y conteo de usuarios.
- Permisos granulares con asignacion a roles.
- Permisos especificos visibles: Ley 2300, reporte de acuerdos, evaluacion de llamadas, recepcion, telefonia, reportes de productividad y rango de extensiones.

### 1.5 Administracion de cartera

- Vista de cartera con pestanas operativas: archivos, real time, predictivo, WhatsApp y clientes.
- Filtros por ultimo perfil, mejor perfil, contactos, asesor, estado, fecha de promesa, fecha de gestion y orden.
- Tabla de clientes con identificacion, nombre, perfiles, asesor, fecha de gestion, total promesas y fecha promesa.
- Colores de riesgo por antiguedad o gestion: hoy, menor a 5 dias, mayor a 5 dias y sin gestion.
- Acciones de retiro y gestion adicional desde cliente.

### 1.6 Productos/procesos manuales y predictivos

- Panel de tareas asignadas con separacion entre manuales y predictivas.
- Subfiltros de tareas generales y especificas.
- Progreso de cada tarea con porcentaje y conteos.
- Vista predictiva dentro de cartera.
- Configuracion estrategica con pausas, ACW, arbol de tipificacion, acuerdos y modulo de pagos.

### 1.7 Acciones asignadas, calendario y agendamientos

- Calendario de agendamientos por mes, semana y dia.
- Filtros por asesores y perfiles.
- Estados de agenda: pendiente, completado y eliminado.
- Agendamientos visibles dentro del calendario con nombre de cliente y hora.
- Panel de tareas asignadas accesible desde topbar.

### 1.8 Cargue masivo y archivos

- Almacen de archivos con conteos por tipo: imagenes, PDF, documentos, Excel/CSV, otros y almacenamiento.
- Filtros por fecha, nombre, identificacion y tipo de cargue.
- Seleccion de archivo.
- Tabla de archivos con descripcion, tipo, peso, usuario, identificacion, tipo de cargue, fecha y opciones.

### 1.9 Reportes operativos e inteligencia de negocio

- Reportes operativos por llamadas, productividad, niveles de atencion e inbound.
- Pantalla de Inteligencia de Negocio con boton Power BI, actualizacion de datos y area embebida.
- Manejo visual de error de conexion con el servicio de reportes.

### 1.10 Ley 2300 y reglas de contacto

- Modulo dedicado de configuracion Ley 2300.
- Activacion/desactivacion global.
- Tipo de alerta: mostrar cada vez o limitar alertas por dia.
- Bloqueo diario o semanal.
- Acciones por canal: llamada, WhatsApp, correo y SMS.
- Resumen de configuracion.
- Banner visible en la ficha del cliente con horario legal permitido.
- Modal de advertencia Ley 2300 antes de continuar con la gestion.

### 1.11 Calidad y auditoria

- Menu de Calidad y Auditoria.
- Evaluacion de llamadas.
- Evaluacion de desempeno.
- Evaluacion de chats.
- Relacion natural con grabaciones y encuestas.

### 1.12 WhatsApp / ChatBOX / EIKO

- Administracion de WhatsApp con plantillas.
- Motivos de finalizacion.
- Configuracion de visibilidad y acceso.
- Horario de acceso.
- Cuentas WhatsApp.
- Envio masivo WhatsApp.
- Reportes.
- Asignacion de conversaciones.
- Centro de mensajes con conversaciones personales y grupales.

### 1.13 Vista cliente completa

- Ficha con datos personales, identificacion, ciudad y estado por mora.
- Informacion de gestion: agente, ultimo perfil, mejor perfil, fecha de gestion, fecha de agendado, fecha promesa y valor promesa.
- Tabla de obligaciones con columnas financieras y scroll horizontal.
- Cards por canal: llamadas, correo, SMS y WhatsApp.
- Acuerdos de pago con cuotas, valores, vigencia, PDF y acciones.
- Historial de gestiones por color/estado.
- Contactos directos y WhatsApp como tabs.
- Cronometro de gestion visible.
- Alertas de cumplimiento legal dentro de la ficha.

### 1.14 Gestion adicional, notas y tareas

- Modal de gestion adicional con seleccion de canal: llamada, WhatsApp, email o SMS.
- Bloc de notas personal del asesor.
- Panel de tareas asignadas con manuales y predictivas.
- Acciones rapidas desde topbar.

## 2. Que ya existe en IEP

IEP ya cuenta con una base importante y no parte desde cero.

### 2.1 Plataforma y gobierno

- Login y branding IEP.
- Menu dinamico por usuario, rol, audiencia, tenant y modulos contratados.
- Gobierno SaaS con empresas, usuarios, roles, permisos, modulos, planes, suscripciones, auditoria y salud.
- Administracion de tenants, proyectos y usuarios.
- Aislamiento por `tenant_id` y validaciones por permiso/modulo.

### 2.2 Collects 360

- Dashboard general.
- Cola de gestion paginada.
- Clientes con filtros y detalle en drawer.
- Obligaciones detalladas por cliente.
- Actividades/gestiones con tipificacion.
- Promesas de pago.
- Pagos asociados a cliente y obligacion.
- Acuerdos de pago con cuotas.
- Datos demograficos.
- Soportes documentales metadata.
- Cargas y repartos.
- Equipos, lideres, agentes y asignaciones.

### 2.3 Telefonia

- Modulo Telefonia transversal.
- Proveedores, extensiones, extension propia, call logs y click-to-call simulado.
- Asociacion de llamada con tenant, proyecto, cliente, obligacion y usuario.
- Grabaciones como metadata.
- Configuracion segura para evitar llamadas reales si `TELEPHONY_REAL_CALLS_ENABLED=false`.

### 2.4 Configuracion, alertas y tipificaciones

- Catalogos.
- Reglas.
- Alertas.
- Workflows.
- Arboles de tipificacion y combinaciones.

### 2.5 Analytics 360 / BI

- Dashboard por rol.
- Dashboard CRM.
- Endpoint BI de cobranzas.
- Cards de KPIs e insights.
- Reportes internos basicos.

### 2.6 ChatBOX 360 / Integraciones

- Canales CRM: WhatsApp, email y telefonia.
- Proveedores de integracion.
- Plantillas.
- Webhooks.
- Eventos.
- Contratos dry-run para PayControl 360 y QAudit 360.

### 2.7 Modulos anexos

- Legal.
- Sales.
- Documents.
- Excel Web operativo.
- Auditoria tecnica.

## 3. Que falta frente al benchmark

| Area | Estado IEP | Brecha frente al benchmark | Prioridad |
| --- | --- | --- | --- |
| Home de campanas | Parcial por proyectos/carteras | Falta campana como experiencia inicial asignada con cards, logos, busqueda y entrada directa | Alta |
| Perfil operativo | Parcial | Falta dashboard personal diario con rendimiento, extension, tareas, campanas y disponibilidad | Alta |
| Telefonia real time | Parcial/simulado | Faltan colas, estados agente, pausas, ACW, AMI, inbound, SLA telefonico y reportes avanzados | Alta |
| Grabaciones | Parcial metadata | Falta playback, filtros operativos, evaluacion y relacion con calidad | Media-alta |
| Usuarios/roles | Fuerte | Falta parametrizacion visible de sesion por tipo de usuario/admin y UX tipo panel operativo | Media |
| Cartera | Buena base | Faltan filtros avanzados por perfiles, aging visual, campana activa y estado legal/contactabilidad | Alta |
| Procesos manual/predictivo | Parcial | Faltan tareas manuales/predictivas como entidad, progreso y asignacion masiva | Alta |
| Calendario | Bajo/parcial | Falta agenda calendario mensual/semanal/diaria de seguimientos | Alta |
| Cargue masivo | Bueno | Falta almacen visual de archivos por tipo, storage, descargas y jobs grandes asincronos | Media |
| Reportes operativos | Parcial | Faltan reportes de llamadas, productividad por hora/dia/perfil/campana y niveles de atencion | Alta |
| Ley 2300 | Generico en reglas | Falta modulo formal de cumplimiento con limites por canal, horario, bloqueos y banners en cliente | Muy alta |
| Calidad/auditoria | Parcial | Falta evaluacion de llamadas/chats/desempeno y scorecards | Media-alta |
| BI | Parcial | Falta embed/report catalog, refresh control, errores amigables y permisos por reporte | Media |
| WhatsApp/ChatBOX | Preparado | Falta conversacion real, plantillas aprobadas, asignacion, masivos, horarios y cierre | Alta |
| Cliente 360 | Buena base drawer | Falta vista tabulada completa, cronometro, banners legales, historial expandible y acciones por canal | Muy alta |
| Gestion adicional | Parcial | Falta modal unificado por canal con validaciones legales y contexto de obligacion | Alta |
| Notas | Parcial en actividades | Falta bloc personal/operativo persistente separado de gestion oficial | Media |
| Tareas asignadas | Basico | Falta modulo de tareas manuales/predictivas con progreso, prioridad y vencimiento | Alta |
| Atencion al cliente | No formal | Falta modulo dedicado de casos/tickets. Propuesto: CareFlow 360 | Alta |

## 4. Mejoras UX/UI recomendadas

### 4.1 Principios visuales para IEP

- Mantener el estilo IEP: premium, claro, enterprise, verde/azul/morado como acento.
- No copiar estructura visual exacta de CRMnex.
- Usar un shell interno claro, con cards densas pero limpias.
- Priorizar operacion diaria: menos marketing, mas velocidad, foco y escaneo.

### 4.2 Home operativo

- Convertir el dashboard del gestor en "Mi operacion".
- Primera vista: campanas/carteras asignadas, tareas del dia, clientes pendientes, promesas vencidas, llamadas del dia y alertas legales.
- Cards de campana con nombre, entidad, estado, clientes asignados, mora, promesas y accion "Entrar".

### 4.3 Cliente 360

- Evolucionar el drawer a vista tabulada:
  - Resumen.
  - Obligaciones.
  - Gestiones.
  - Promesas/acuerdos/pagos.
  - Contactos/demograficos.
  - Documentos.
  - Llamadas/grabaciones.
  - Notas/tareas.
  - Cumplimiento.
- Incluir banner Ley 2300 cuando aplique.
- Mostrar cronometro de gestion opcional.
- Mantener acciones rapidas visibles sin recargar.

### 4.4 Telefonia

- Topbar con estado de extension, disponibilidad, pausa, microfono y proveedor.
- Vista de monitoreo tipo operaciones: agentes, estado, llamadas hoy, espera, abandono, AHT y ACW.
- Boton de llamada debe reflejar estado: disponible, sin extension, modulo pendiente, fuera de horario legal o sin telefono valido.

### 4.5 Administracion

- Separar "Gobierno SaaS IEP" de "Administracion de empresa".
- Crear panel de parametros de sesion por rol/tipo de usuario.
- Mejorar permisos con filtros por modulo, riesgo y perfil.

### 4.6 Omnicanalidad

- ChatBOX 360 debe tener bandeja de conversaciones, asignacion, plantillas, horarios, cierres y reportes.
- El panel lateral de mensajes puede inspirar la UX, pero con identidad IEP y sin copiar elementos visuales.

## 5. Priorizacion por fases

### Fase 0 - Cumplimiento, estabilidad y base operativa

Objetivo: no avanzar canales reales sin controles.

- Formalizar modulo Ley 2300 en IEP.
- Reglas por canal, horario, frecuencia diaria/semanal, blacklist y excepciones.
- Bloqueo/advertencia antes de llamada, WhatsApp, SMS o email.
- Guardar trazabilidad de decision: permitido, bloqueado, advertido, forzado por admin.
- Asegurar refresh sin logout ante errores 403/503 opcionales.
- QA de tenant, permisos y modulos.

### Fase 1 - Experiencia diaria Collects 360

- Home "Mi operacion" con campanas asignadas.
- Cliente 360 tabulado.
- Gestion adicional por canal.
- Notas personales y notas operativas.
- Tareas asignadas manuales.
- Calendario de agendamientos.
- Filtros avanzados de cartera.

### Fase 2 - Telefonia operativa

- Estados de agente: disponible, en llamada, pausa, ACW, offline.
- Colas y asignacion de extensiones por tenant/campana.
- Monitor real-time con datos simulados primero y adaptador PBX despues.
- Reporte de llamadas entrantes/salientes.
- Grabaciones con playback seguro y permisos.
- Encuesta post-llamada preparada para QAudit 360.

### Fase 3 - ChatBOX 360 y WhatsApp

- Bandeja de conversaciones.
- Cuentas/canales por tenant.
- Plantillas y aprobaciones.
- Envio masivo controlado.
- Asignacion de conversaciones.
- Motivos de finalizacion.
- Horarios y visibilidad.
- Webhooks entrantes con idempotencia.

### Fase 4 - Calidad, auditoria y QAudit 360

- Evaluacion de llamadas.
- Evaluacion de chats.
- Evaluacion de desempeno por asesor.
- Scorecards configurables.
- Muestras por campana, asesor, canal y resultado.
- Integracion futura QAudit 360 por adaptadores y eventos.

### Fase 5 - Analytics 360 avanzado y predictivo

- Reportes de productividad por hora/dia/campana/perfil.
- Reportes de promesas, acuerdos, pagos y recuperacion.
- Dashboard de telefonia y omnicanalidad.
- Catalogo de reportes embebidos.
- Motor predictivo inicial: siguiente mejor accion, cliente prioritario, probabilidad de contacto y riesgo de incumplimiento.

### Fase 6 - CareFlow 360 MVP

- Lanzar atencion al cliente como modulo independiente, reutilizando usuarios, permisos, canales, documentos y auditoria.
- Permitir convivencia con Collects 360 sin mezclar reglas de cobranza ni datos de soporte.

## 6. MVP CareFlow 360

CareFlow 360 debe ser el modulo de atencion al cliente dentro de IEP. No reemplaza Collects 360: atiende solicitudes, PQRS, soporte, servicio y seguimiento postventa.

### 6.1 Alcance MVP

- Casos/tickets por tenant y proyecto.
- Canales: manual, telefono, WhatsApp, email, web, API.
- Tipo de caso: consulta, reclamo, solicitud, soporte, PQRS, escalamiento, retencion.
- Estado: nuevo, abierto, en proceso, esperando cliente, escalado, resuelto, cerrado, reabierto.
- Prioridad: baja, media, alta, critica.
- SLA basico por tipo/prioridad: primera respuesta y resolucion.
- Responsable asignado y equipo.
- Notas internas y notas visibles.
- Adjuntos/documentos.
- Historial completo de eventos.
- Relacion opcional con cliente, contacto, obligacion, pago, acuerdo, oportunidad o caso legal.
- Dashboard de casos por estado, SLA vencido, responsable, canal y tendencia.

### 6.2 Modelo de datos sugerido

- `care_cases`: tenant_id, project_id, case_number, subject, description, customer_id, contact_id, source_channel, case_type, priority, status, owner_user_id, team_id, due_at, first_response_due_at, resolved_at, closed_at, metadata_json.
- `care_case_events`: tenant_id, case_id, user_id, event_type, note, previous_status, new_status, channel, metadata_json.
- `care_case_notes`: tenant_id, case_id, user_id, visibility, body, created_at.
- `care_case_attachments`: tenant_id, case_id, document_id, file_name, mime_type, size_bytes.
- `care_sla_policies`: tenant_id, case_type, priority, first_response_minutes, resolution_minutes, calendar_json, is_active.

### 6.3 Permisos MVP

- `careflow.view`
- `careflow.create`
- `careflow.update`
- `careflow.assign`
- `careflow.close`
- `careflow.notes.internal`
- `careflow.attachments.manage`
- `careflow.reports.view`
- `careflow.admin`

### 6.4 UX MVP

- Menu: CareFlow 360.
- Pantallas:
  - Dashboard de atencion.
  - Casos.
  - Mi bandeja.
  - Calendario/SLA.
  - Configuracion SLA.
  - Reportes.
- Drawer/vista de caso:
  - Header con estado, prioridad, SLA, canal y responsable.
  - Timeline de eventos.
  - Notas.
  - Adjuntos.
  - Cliente relacionado.
  - Acciones: responder, asignar, escalar, cerrar, reabrir.

### 6.5 Integracion con modulos IEP

- ChatBOX 360: crear caso desde conversacion.
- Telefonia: crear caso desde llamada.
- Documents: adjuntos y soportes.
- Analytics 360: metricas de SLA y calidad.
- QAudit 360 futuro: evaluar interacciones de soporte.
- Collects 360: si el caso pertenece a cobranza, enlazar cliente/obligacion sin convertir el ticket en gestion de cobranza.

## 7. Riesgos

- Riesgo legal: implementar canales reales sin Ley 2300 puede exponer a incumplimiento.
- Riesgo de tenant: cada entidad nueva debe validar `tenant_id` y relaciones cruzadas.
- Riesgo UX: copiar demasiado la referencia diluye identidad Icodeup; la guia debe inspirar flujos, no apariencia exacta.
- Riesgo de alcance: telefonia real, WhatsApp real, BI embebido y CareFlow pueden crecer mucho si no se separan por fases.
- Riesgo de datos: cargas masivas grandes requieren procesamiento asincrono, idempotencia y retencion controlada.
- Riesgo de permisos: nuevos modulos necesitan permisos explicitos y pruebas por rol.
- Riesgo de rendimiento: reportes operativos por llamada/gestion pueden necesitar indices, agregados o tablas resumen.
- Riesgo de grabaciones: audio y adjuntos pueden contener datos personales; se requiere storage seguro, expiracion y auditoria.
- Riesgo de integraciones: PBX, WhatsApp y BI deben entrar via adapters con flags, dry-run y retries.

## 8. Checklist QA

### QA funcional

- El gestor ve solo campanas/carteras asignadas.
- El admin empresa ve usuarios, equipos, permisos y modulos de su tenant.
- El SuperAdmin ve gobierno global sin contaminar datos entre tenants.
- Cliente 360 carga obligaciones, pagos, acuerdos, promesas, demograficos, llamadas, documentos, notas y tareas por cliente real.
- Gestion adicional exige canal y respeta reglas Ley 2300.
- Boton llamar cambia segun extension, modulo, telefono y horario legal.
- Calendario muestra agendamientos por asesor, perfil, estado y fecha.
- Tareas manuales/predictivas se asignan y actualizan progreso.
- Cargas masivas detectan errores, permiten preview, confirmacion y auditoria.
- Reportes operativos respetan permisos y filtros por tenant/campana/asesor.

### QA legal y seguridad

- Ley 2300 bloquea o advierte por canal segun configuracion.
- Toda accion bloqueada queda auditada.
- No se puede llamar/contactar cliente de otro tenant.
- No se pueden consultar grabaciones, archivos o tickets de otro tenant.
- Los permisos nuevos no quedan expuestos por fallback accidental.
- No se guardan secretos en configuraciones visibles.

### QA UX

- Home operativo abre rapido y muestra tareas claras.
- Los estados usan texto y color, no solo color.
- Los empty states explican que falta configurar o cargar.
- La vista cliente no pierde contexto al registrar gestion.
- Los errores opcionales de telefonia, BI o integraciones no cierran sesion.
- Las tablas mantienen paginacion maximo 10 donde aplique.

### QA tecnico

- `python -m compileall app`.
- `node --check v2/frontend/static/assets/app.js`.
- `alembic upgrade head`.
- `pytest -m safe_static`.
- Tests de tenant isolation para nuevas rutas.
- Tests de permisos por rol para CareFlow 360.
- Tests de Ley 2300 por canal y horario.
- `git diff --check`.

## 9. Recomendacion de implementacion sin romper lo actual

1. Mantener Collects 360 funcionando como esta y agregar cambios por capas.
2. Crear nuevas entidades con migraciones aditivas; no renombrar ni eliminar campos existentes.
3. Introducir feature flags por modulo:
   - `LAW_2300_RULES_ENABLED`
   - `TELEPHONY_REALTIME_ENABLED`
   - `CHATBOX_WHATSAPP_ENABLED`
   - `CARE_FLOW_ENABLED`
   - `PREDICTIVE_ACTIONS_ENABLED`
4. Reutilizar servicios actuales de acceso:
   - `require_tenant`
   - `require_module`
   - `require_permission`
   - helpers de cliente/obligacion.
5. Agregar permisos antes de exponer pantallas nuevas.
6. Implementar primero UI con datos simulados/controlados cuando haya integracion externa.
7. Mantener adaptadores para PBX, WhatsApp, Power BI, QAudit y PayControl.
8. Usar idempotencia en todo evento externo.
9. Agregar seeds TEST idempotentes y no automaticos.
10. Documentar cada fase con comandos de prueba y rollback operativo.

## 10. Roadmap recomendado resumido

| Fase | Entrega | Valor | Riesgo |
| --- | --- | --- | --- |
| 0 | Ley 2300 formal + errores/session hardening | Reduce riesgo legal y operativo | Alto impacto, bajo alcance |
| 1 | Home campanas + Cliente 360 + tareas/calendario | Mejora operacion diaria | Medio |
| 2 | Telefonia real-time + colas + reportes | Acerca a call center real | Alto por integracion |
| 3 | ChatBOX 360 WhatsApp/conversaciones | Omnicanalidad comercial | Alto por proveedor |
| 4 | Calidad/QAudit 360 | Control y mejora de asesores | Medio |
| 5 | Analytics predictivo | Diferenciador ejecutivo | Medio-alto |
| 6 | CareFlow 360 MVP | Nuevo modulo de atencion al cliente | Medio |

## 11. Decision sugerida

La siguiente implementacion deberia empezar por Fase 0 y Fase 1:

- Fase 0 asegura cumplimiento legal, evita contactos indebidos y prepara cualquier canal real.
- Fase 1 entrega valor visible inmediato: home de campanas, cliente 360, tareas, agenda y gestion adicional.

Telefonia avanzada, WhatsApp real, calidad y CareFlow 360 deben avanzar despues sobre esa base, con feature flags y sin modificar el comportamiento estable actual de Collects 360.
