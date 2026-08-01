# Diagnostico funcional CRM cobranzas SaaS - IEP

Fecha de revision: 2026-08-01
Producto: IEP - Icodeup Enterprise Platform
Alcance: diagnostico por inspeccion de codigo, rutas, frontend estatico y pruebas existentes. No se hicieron cambios funcionales.

## 1. Resumen ejecutivo

IEP ya funciona como una base preproductiva real para un SaaS multiempresa y CRM de cobranzas. No es solamente una interfaz visual: existe backend FastAPI, modelos SQLAlchemy, rutas protegidas, menu dinamico por rol/modulo, cargas masivas con preview/confirmacion, cola de gestion, detalle de cliente, gestiones, promesas, pagos, acuerdos, auditoria, telefonia simulada y pruebas automatizadas orientadas a tenant, permisos y flujos operativos.

El estado actual es bueno para demo interna, piloto controlado y pruebas preproductivas. Para venderlo como producto operativo de cobranza completo, todavia hay brechas funcionales importantes:

- PayControl 360 registra pagos a nivel cliente, pero no persiste relacion directa con obligacion ni actualiza saldos de obligaciones.
- Clientes no tienen unicidad de base de datos por `tenant_id + document`, lo que puede generar duplicados y asociaciones ambiguas.
- Telefonia, WhatsApp, chatbot e integraciones estan en modo estructura/preparacion/simulacion, no en integracion real.
- El drawer de cliente ayuda a operar sin perder contexto, pero aun no cubre detalle completo por pestanas ni carga todos los registros relacionados por cliente.
- Varias pruebas de integracion existen, pero requieren servidor, base seed y variables de entorno para ejecutarse; la suite completa no corre sola en local sin preparacion.

Conclusion: IEP esta en estado "preproductivo funcional con brechas de hardening". La base es solida, pero antes de produccion comercial conviene cerrar pagos por obligacion, unicidad de cliente, flujos omnicanal reales, QA browser y hardening de datos.

## 2. Estado general del producto

| Area | Estado | Evidencia revisada | Comentario |
| --- | --- | --- | --- |
| SaaS multiempresa | Funcional preproductivo | `v2/backend/app/services/access_control.py`, `v2/backend/app/api/routes/governance.py`, `v2/backend/tests/test_saas_tenant_isolation_deep.py` | Usa shared schema con `tenant_id`, permisos, modulos y menu por usuario. |
| Gobierno SaaS | Funcional | `v2/backend/app/api/routes/governance.py`, `v2/backend/app/api/routes/administration.py` | Permite roles, permisos, modulos, settings, auditoria, usuarios y resumen comercial. |
| Administracion empresa | Funcional parcial/alta | `v2/backend/app/api/routes/teams.py`, `v2/backend/app/api/routes/governance.py` | Usuarios, roles, permisos, proyectos, lideres, gestores y asignaciones existen. |
| CRM cobranzas | Funcional | `v2/backend/app/api/routes/crm/*`, `v2/frontend/static/assets/app.js` | Clientes, cola, filtros, obligaciones, gestiones, promesas, pagos y acuerdos conectados. |
| Cargas masivas | Funcional preproductivo | `v2/backend/app/api/routes/uploads.py`, `v2/backend/tests/test_sprint4_uploads_repartos.py` | Preview, mapeo, errores, confirmacion, templates y lotes auditables. |
| PayControl 360 | Parcial | `v2/backend/app/models/crm.py`, `v2/backend/app/api/routes/crm/payments.py` | Registra pagos por cliente; falta obligacion, conciliacion avanzada y soporte real. |
| Telefonia | Simulada/preparada | `v2/backend/app/api/routes/telephony.py`, `v2/backend/tests/test_telephony_click_to_call.py` | Click-to-call crea `CallLog` y gestion, pero `real_call_executed=false`. |
| ChatBOX 360 / Integraciones | Estructura preparada | `v2/backend/app/api/routes/integrations.py` | Canales, proveedores, plantillas, webhooks y eventos; pruebas simuladas. |
| UX operativa | Buena base, incompleta | `v2/frontend/static/index.html`, `v2/frontend/static/assets/app.js` | Hay drawer de cliente y secciones operativas; falta detalle por tabs/subdrawers. |
| Auditoria | Funcional amplia | `v2/backend/app/services/audit_service.py`, rutas principales | Muchas acciones trazan auditoria; hay algunas operaciones que requieren cierre. |
| Tests | Buena base, no suite completa autoejecutable | `v2/backend/tests/*`, `v2/backend/tests/conftest.py` | Integracion condicionada por env y credenciales; `safe_static` corre sin servidor. |

## 3. Mapa de modulos

| Modulo / producto | Estado actual | Pantallas/rutas relacionadas | Observacion |
| --- | --- | --- | --- |
| IEP Gobierno SaaS | Funcional | `/api/governance/*`, `/api/admin/*`, `/api/subscriptions/*` | Control global de tenants, modulos, planes, roles y auditoria. |
| Collects 360 | Funcional | `/api/crm/*`, `/api/uploads/*`, `/api/teams/*` | CRM de cobranzas operativo con cola, clientes, obligaciones y gestiones. |
| PayControl 360 | Parcial | `/api/crm/payments`, `/api/uploads` tipo `pagos` | Pago cliente funciona; falta pago-obligacion y conciliacion. |
| Analytics 360 | Funcional basico | `/api/crm/dashboard`, `/api/crm/bi`, `/api/dashboard/me` | Dashboards, BI y KPIs por rol. |
| ChatBOX 360 | Preparado/simulado | `/api/integrations/*`, `/api/crm/channels` | Configuracion y pruebas simuladas, no envio real WhatsApp/chatbot. |
| Telefonia | Simulada/preparada | `/api/telephony/*`, `/api/recordings/*` | Extension, click-to-call, logs y grabaciones metadata; falta PBX/WebRTC real. |
| Documentos | Funcional metadata | `/api/documents/*`, drawer cliente | Registro documental y relacion con cliente/proyecto; no se valido almacenamiento binario real. |
| Legal / Sales | Funcional como modulos anexos | `/api/legal/*`, `/api/sales/*` | Existen dashboards y CRUD operativo basico. |
| Mi Excel Web | Funcional operativo parcial | `/api/excel-web/*` | Consulta, filas operativas, vistas y exportacion segun permisos. |
| Configuracion | Funcional | `/api/configuration/*`, `/api/typifications/*` | Catalogos, reglas, workflows, arboles y combinaciones. Integracion con gestion aun mixta. |

## 4. Matriz de roles vs funcionalidades

| Funcionalidad | SuperAdmin IEP | Admin empresa | Lider operativo | Gestor cobranza | Calidad/Auditor |
| --- | --- | --- | --- | --- | --- |
| Ver Gobierno SaaS global | Si | No | No | No | No |
| Crear/listar tenants | Si | No | No | No | No |
| Planes/suscripciones globales | Si | Solo lectura propia parcial | No | No | No |
| Activar modulos tenant | Si | No | No | No | No |
| Configuracion tenant | Si segun tenant | Si propia empresa | Limitado | No | Lectura si permiso |
| Roles/permisos | Si | Si sin permisos reservados | No | No | No |
| Usuarios y proyectos | Si | Si propia empresa | Lectura/gestion de equipo segun permisos | No | Lectura segun permisos |
| Cola de cobranza | Segun alcance global | Toda empresa | Equipo/carteras | Propia asignacion | Lectura |
| Clientes | Global/tenant | Empresa | Equipo/cartera | Asignados | Lectura |
| Obligaciones | Global/tenant | Empresa | Equipo/cartera | Asignadas/cliente propio | Lectura |
| Crear gestion | Si | Si | Si | Si propia asignacion | No escritura |
| Promesas | Si | Si | Si | Si propias | Lectura |
| Pagos | Si | Si | Si | Crear segun permiso | Lectura |
| Acuerdos | Si | Si | Si | Crear segun permiso | Lectura |
| Cargas masivas | Si | Si | Repartos/demograficos segun permisos | No general | No general |
| Telefonia click-to-call | Si | Si | Si | Si con extension activa | Logs/lectura |
| Integraciones/ChatBOX | Si | Si segun permisos | No habitual | No | No |
| Exportaciones | Si | Si segun permisos | Parcial | Restringido | Restringido |

## 5. Flujo end-to-end esperado

1. SuperAdmin crea tenant, plan, suscripcion y modulos contratados.
2. Admin empresa configura branding, usuarios, roles, permisos, proyectos/carteras y lideres/gestores.
3. Admin o lider carga clientes, obligaciones, reparto, datos demograficos, telefonos, emails, direcciones, pagos y novedades.
4. El sistema valida archivo, muestra preview, detecta errores, permite confirmar y deja lote auditable.
5. Gestor entra a cola asignada, busca por documento/nombre/telefono, filtra por riesgo/estado/cartera y abre detalle sin perder contexto.
6. Gestor llama, registra gestion por cliente u obligacion, selecciona tipificacion, fecha siguiente, observacion y promesa si aplica.
7. Lider monitorea equipo, promesas, pagos, acuerdos, gestiones, productividad y alertas.
8. Admin empresa y SuperAdmin revisan auditoria, permisos, modulos, datos y salud.
9. Omnicanalidad real envia/recibe WhatsApp/chatbot/telefonia, guarda eventos y enlaza cada interaccion al cliente, obligacion y gestion.

## 6. Flujo end-to-end soportado actualmente

Actualmente se soporta:

- Login y sesion JWT.
- Menu dinamico desde `/api/menu/me` con producto, tenant, usuario, items visibles y modulos.
- Dashboard por rol desde `/api/dashboard/me`.
- Gobierno de roles, permisos, modulos, settings, auditoria, parties, suscripciones e insights de seguridad.
- Administracion SuperAdmin de tenants, proyectos y usuarios.
- Administracion por empresa/equipo desde `/api/teams/*`.
- CRM con clientes paginados, filtros, exportacion, cola y obligaciones.
- Drawer de gestion de cliente con resumen, obligaciones, gestion, promesas/pagos visibles, acuerdo, soporte documental, demograficos y grabaciones si el modulo esta visible.
- Creacion de gestion, actualizacion de estado, `last_contact_at`, `next_contact_at`, prioridad y promesa opcional.
- Promesas, acuerdos e installments.
- Pagos manuales y pagos por carga.
- Cargas CSV por JSON (`csv_text`) con templates, mapeo sugerido, preview, confirmacion, errores y resultados.
- Telefonia con proveedores, extensiones, click-to-call simulado, call logs y finalizacion de llamada.
- Integraciones con proveedores, canales, plantillas, webhooks y eventos simulados.

No se soporta aun como flujo real completo:

- Marcacion real PBX/WebRTC/softphone.
- WhatsApp/chatbot real con proveedor externo.
- Relacion persistida pago-obligacion.
- Conciliacion bancaria, soporte de pago adjunto y validacion financiera avanzada.
- Carga asincrona de archivos grandes con almacenamiento fisico/versionado.
- Cliente detalle por tabs con carga completa de todos los relacionados.

## 7. Hallazgos criticos

### C1. PayControl 360 no guarda relacion pago-obligacion

`Payment` no tiene `obligation_id` y `PaymentCreate/PaymentOut` tampoco lo exponen. La carga de `pagos` acepta `numero_obligacion` en plantilla, pero `_create_payment` solo crea un pago asociado al cliente y no actualiza `CustomerObligation.current_balance`.

Impacto: en carteras multiobligacion no se puede saber a que obligacion aplica el pago, los saldos por obligacion quedan desalineados y la visualizacion del detalle puede ser incorrecta para recuperacion real.

Recomendacion: agregar `obligation_id` a pagos, actualizar saldo de obligacion y cliente de forma consistente, crear constraint/indice e incluir pruebas de pago por obligacion.

### C2. Cliente no tiene unicidad fuerte por tenant y documento

`Customer` no declara `UniqueConstraint("tenant_id", "document")`. El upload usa `_find_customer(tenant_id, document)`, pero si existen duplicados previos o concurrencia, la asociacion de demograficos, pagos, obligaciones y novedades puede quedar ambigua. `POST /api/crm/customers` tampoco valida duplicado de documento antes de crear.

Impacto: alto riesgo de duplicar deudores y cruzar datos operativos dentro del mismo tenant.

Recomendacion: depurar duplicados, agregar constraint unico, manejar error 409 y probar create/upload con documento existente.

### C3. Omnicanalidad comercial aun es simulada/preparada

`/api/telephony/click-to-call` guarda `CallLog`, crea gestion y deja metadata con `real_call_executed: False`. Integraciones registra pruebas de canal/webhook con `status="simulated"`. No hay envio real WhatsApp, chatbot, PBX o WebRTC embebido.

Impacto: para demo funciona; para cliente real debe comunicarse como "preparado para integracion" hasta conectar proveedor.

Recomendacion: cerrar fase de proveedor real por capas: PBX/WebRTC, WhatsApp Business/API, eventos entrantes, trazabilidad de delivery y retries.

## 8. Hallazgos medios

### M1. Detalle de cliente depende de listas globales limitadas

El drawer filtra `state.crm.promises`, `state.crm.payments` y `state.ops.demographics`, pero esas colecciones se cargan como listas generales limitadas. Si un cliente no aparece dentro de esos primeros registros, su detalle puede mostrar "sin datos" aunque existan registros.

Recomendacion: crear endpoint o carga dedicada por cliente para promesas, pagos, acuerdos, demograficos, llamadas y documentos al abrir drawer.

### M2. Promesas vencidas no parecen recalcularse automaticamente

El dashboard y alertas consultan estados como `Vencida`, pero no se observo una tarea/scheduler que marque promesas vencidas por `due_date`. Si nadie actualiza el estado, KPIs de vencidas pueden quedar incompletos.

Recomendacion: job diario o calculo dinamico por fecha, con auditoria o marca de sistema.

### M3. Duplicidad de pagos solo se controla por aplicacion

En carga de pagos se evita duplicar por `tenant_id + customer_id + reference`, pero no hay constraint unico en modelo. Manualmente tambien se puede repetir referencia si el flujo lo permite.

Recomendacion: definir regla de negocio de unicidad por `tenant_id + reference` o `tenant_id + customer_id + reference`, y reforzarla en base de datos.

### M4. Cargas masivas son sincronas y en memoria

El frontend lee CSV y envia `csv_text` por JSON. El backend procesa en la misma peticion y almacena resumen/errores/resultados dentro de `UploadBatch.summary_json`, con limites de errores/resultados.

Recomendacion: para archivos grandes usar almacenamiento temporal, job asincrono, idempotency key, progreso, cancelacion y retencion de archivos/error files.

### M5. Dos modelos de tipificacion conviven

El flujo de gestion usa `TypificationNode`. Tambien existen arboles avanzados (`TypificationTree`, `TypificationTreeNode`, `TypificationCombinationRule`) con UI, pero la creacion de gestion no aplica aun las reglas avanzadas de combinacion.

Recomendacion: unificar el motor operativo de tipificacion para que el drawer use arboles/combinaciones y valide campos requeridos.

### M6. Endpoint de health es publico

`/api/health` no requiere autenticacion. Puede ser valido para balanceador, pero expone `app`, `environment`, `port` y estado de base.

Recomendacion: definir politica: health publico minimo para infraestructura y health detallado autenticado para Gobierno SaaS.

### M7. Subscriptions y governance tienen caminos solapados para modulos

`/api/governance/modules/{tenant_id}` opera sobre catalogo `Module`; `/api/subscriptions/modules/{tenant_id}` valida contra `SUPPORTED_MODULES` hardcodeado que no refleja necesariamente todos los modulos visibles como Telefonia.

Recomendacion: usar una sola fuente de verdad para catalogo de modulos.

## 9. Hallazgos menores

- Existen textos/semillas demo en plantillas y placeholders; aceptable para test, pero deben separarse de datos productivos.
- Las tablas y endpoints suelen limitar a 10/20 registros; bueno para UI, insuficiente para auditorias operativas grandes sin filtros/exportaciones.
- El drawer existe, pero no tiene tabs claras ni subdrawer por obligacion/pago/promesa/llamada.
- Las grabaciones tienen playback placeholder si no hay URL del proveedor.
- Exportaciones existen para clientes y pagos; faltan exportes dedicados de promesas/acuerdos en rutas revisadas.
- Algunas acciones de actualizacion, como completar promesa, agregan gestion pero requieren revisar auditoria explicita consistente.

## 10. Riesgos de datos, tenant y permisos

| Riesgo | Severidad | Estado observado | Recomendacion |
| --- | --- | --- | --- |
| Duplicados de cliente por documento | Alta | No hay unique DB por `tenant_id + document` | Constraint, limpieza y pruebas. |
| Pago sin obligacion | Alta | Modelo pago solo tiene cliente | Agregar `obligation_id` y actualizar saldos. |
| Saldo obligacion no cambia con pagos | Alta | Pago actualiza `Customer.balance` | Aplicar pagos a obligacion y recalcular cliente. |
| Integraciones simuladas confundidas como reales | Alta comercial | Mensajes dicen simulado/preparado | Etiquetado claro por ambiente y proveedor. |
| Health detallado publico | Media | `/api/health` sin auth | Separar health publico/detallado. |
| Carga masiva grande bloquea request | Media | `csv_text` sin cola asincrona | Worker/job y almacenamiento de archivo. |
| Roles legacy amplios | Media | Insights detectan roles legacy | Migrar a roles especializados por tenant. |
| Datos demo en ambiente no productivo | Media | Config/semillas soportan demo | Check preproduccion antes de publicar. |
| Registros relacionados con listas limitadas | Media | Drawer filtra cache limitada | Fetch por cliente. |
| Permisos UI vs API | Media | Menu filtra, API valida permisos | Mantener tests por endpoint y rol. |

El aislamiento por tenant tiene buena base: `require_tenant`, `require_module`, `require_permission`, `customer_query`, `obligation_query`, rutas de gobierno y pruebas de tenant isolation cubren los casos principales. Aun asi, antes de produccion conviene una auditoria endpoint por endpoint con datos cruzados reales.

## 11. Diagnostico de cargas masivas

| Tipo | Campos requeridos | Que hace hoy | Duplicados/actualizacion | Auditoria/impacto UI | Estado |
| --- | --- | --- | --- | --- | --- |
| `clientes` | `document`, `name` | Crea/actualiza cliente, asigna proyecto/gestor/lider si vienen columnas | Upsert por busqueda `tenant_id + document`, sin unique DB | `UploadBatch`, auditoria, aparece en clientes/cola/dashboard | Funcional con riesgo de duplicado DB |
| `obligaciones` | `document`, `obligation_number` | Asegura cliente y crea/actualiza obligacion | Obligacion unica por `tenant_id + obligation_number`; valida si pertenece a otro cliente | Aparece en detalle cliente y matriz obligaciones | Funcional |
| `reparto_cartera` | `document` | Crea/actualiza cliente, obligacion opcional, gestor/lider/proyecto | Igual que clientes/obligaciones | Impacta cola, asignaciones y team/project | Funcional |
| `demograficos` | `document` | Agrega/actualiza telefono, email, direccion, ciudad, empleador, referencias, score | Upsert por tenant+cliente+source+phone+email+address, sin unique DB | Visible en cargas y drawer si cae en lista cargada | Funcional parcial UI |
| `telefonos_emails_direcciones` | `document` | Misma ruta de demograficos enfocada en contactabilidad | Igual que demograficos | Mejora datos complementarios | Funcional |
| `pagos` | `document`, `amount` | Crea pago por cliente, baja saldo de cliente y registra gestion | Evita duplicado por referencia en aplicacion | Visible en pagos/dashboard/drawer si esta en lista | Parcial por falta obligacion |
| `novedades_operativas` | `document`, `result` | Crea gestion y actualiza estado/siguiente accion de cliente | Siempre crea actividad | Visible en historial de gestiones | Funcional |

Capacidades de carga confirmadas:

- Plantillas por tipo en `/api/uploads/templates/{upload_type}`.
- Deteccion de delimitador coma/punto y coma.
- Mapeo sugerido por sinonimos.
- Preview con columnas, muestra, requeridos, opcionales y errores por fila.
- Confirmacion con `create_records` true/false.
- Lotes con estado `completed` o `completed_with_errors`.
- Descarga logica de errores y resultados como CSV desde endpoints de batch.
- Validacion de tenant/proyecto/gestor/lider.

Brechas de carga:

- No hay procesamiento asincrono.
- No hay idempotency key por archivo/lote.
- No hay versionado/almacenamiento real del archivo original.
- La validacion de duplicados no esta reforzada siempre con constraints.
- Los resultados se guardan resumidos, no como detalle relacional por fila.

## 12. Diagnostico de gestiones, promesas y pagos

Gestiones:

- `POST /api/crm/customers/{customer_id}/activities` crea `ManagementActivity`.
- Valida acceso al cliente y obligacion.
- Permite tipificacion simple.
- Actualiza estado, ultima fecha de contacto, proxima fecha, siguiente accion y prioridad.
- Puede crear promesa si hay monto y fecha.
- Registra auditoria.

Promesas:

- `GET /api/crm/promises` lista promesas segun `customer_query`.
- `POST /api/crm/promises` crea promesa asociada a cliente y opcionalmente obligacion.
- `PATCH /api/crm/promises/{promise_id}/complete` marca como cumplida y crea gestion.
- Falta recalculo automatico de vencidas y revisar auditoria explicita al completar.

Pagos / PayControl 360:

- `GET /api/crm/payments` lista pagos segun clientes visibles.
- `POST /api/crm/payments` registra pago manual por cliente.
- `GET /api/crm/payments/export` exporta CSV y audita.
- Carga `pagos` tambien crea pago y gestion.
- Falta relacion con obligacion, soporte/comprobante, conciliacion, validacion de referencia fuerte y update de saldos de obligacion.

Acuerdos:

- `POST /api/crm/agreements` crea acuerdo con cuotas automaticas o payload de installments.
- `GET /api/crm/agreements` y `GET /api/crm/agreements/{id}` listan/detallan.
- `PATCH /api/crm/agreements/{agreement_id}/installments/{installment_id}` actualiza cuota.
- Asociacion a obligacion existe.

## 13. Diagnostico de omnicanalidad

Telefonia:

- Proveedores: CRUD basico con validacion para no guardar secretos en config.
- Extensiones: asignacion por usuario/tenant/proveedor.
- Mi extension: endpoint para saber si el usuario puede llamar.
- Click-to-call: valida extension, acceso al cliente/obligacion, crea `CallLog` y `ManagementActivity`.
- Estado real: simulado. No invoca PBX, WebRTC, SIP ni API externa real.

Grabaciones:

- Se registran como metadata (`CallRecording`) con acceso, playback/download y logs de acceso.
- Para gestor cobranza esta bloqueado por demo en ruta.
- Playback puede devolver placeholder si no hay URL real.

ChatBOX 360 / Canales / WhatsApp:

- Hay proveedores, canales, plantillas, webhooks y eventos.
- `test_channel` y `test_webhook` crean eventos simulados.
- No se observo envio real, recepcion real, chatbot, conversacion persistente ni webhooks entrantes con firma validada.

Clasificacion:

- Funcional actualmente: configuracion de proveedores/canales, plantillas, webhooks, eventos simulados, click-to-call simulado, call logs.
- Simulado: pruebas de canal/webhook, click-to-call, telefonia sin proveedor real.
- Estructura preparada: PBX/WebRTC/API externa, WhatsApp/email/SMS/webhook, templates.
- Pendiente de integracion real: marcacion, softphone embebido, WhatsApp Business, chatbot, eventos entrantes, delivery/read receipts.

## 14. Diagnostico UX, drawers y subventanas

Lo que ya existe:

- Layout interno con sidebar/topbar y secciones por modulo.
- Cola de gestion con seleccion de cliente y panel de detalle.
- Drawer lateral `managementDrawer` al abrir cliente.
- Drawer conserva contexto de la pantalla principal.
- Acciones rapidas: llamar, WhatsApp, email, registrar llamada, crear promesa, crear acuerdo, escalar juridico.
- Resumen de cliente, obligaciones, actividad reciente, promesas/pagos, acuerdo, soporte documental, demograficos y grabaciones.

Brechas UX:

- El detalle no esta organizado por tabs claras.
- No existe subdrawer/modal especifico para obligacion, pago, promesa, acuerdo, llamada o documento.
- Datos relacionados se filtran desde caches limitadas, no desde endpoints por cliente completos.
- Registrar pago no esta dentro del drawer del cliente ni permite seleccionar obligacion.
- Telefonos/emails/direcciones aparecen como demograficos, pero no como libreta de contacto operativa priorizada.
- Faltan estados vacios y errores por cada subpanel relacionado.

Propuesta UX:

- Drawer cliente con tabs: Resumen, Obligaciones, Contactabilidad, Gestiones, Promesas, Pagos, Acuerdos, Llamadas, Documentos.
- Subdrawer de obligacion con saldo, historial, pagos, promesas y acuerdos.
- Subdrawer de llamada con log, resultado, grabacion y actividad generada.
- Formulario rapido de pago desde cliente/obligacion.
- Carga lazy por tab para no afectar rendimiento.

## 15. Recomendaciones priorizadas

1. Cerrar PayControl por obligacion: modelo, schema, rutas, UI, carga, saldos y pruebas.
2. Agregar unicidad `tenant_id + document` en clientes y limpieza de duplicados.
3. Crear fetch completo por cliente para detalle operacional.
4. Hacer overdue automatico de promesas.
5. Definir health publico minimo vs health detallado protegido.
6. Consolidar catalogo de modulos entre governance/subscriptions/menu.
7. Convertir cargas a job asincrono con idempotencia.
8. Unificar tipificacion simple y arboles avanzados.
9. Implementar integracion PBX/WebRTC real o marcar claramente como modo manual/simulado.
10. Implementar WhatsApp/chatbot real con eventos entrantes, plantillas aprobadas y auditoria.
11. Completar QA browser por roles.
12. Ejecutar suite de integracion contra servidor interno con credenciales controladas.

## 16. Backlog propuesto por fases

### Fase 1: bloqueantes funcionales

- Agregar `Payment.obligation_id`.
- Actualizar saldos cliente/obligacion de forma transaccional.
- Constraint unico de cliente por tenant/documento.
- Constraint/idempotencia para pagos por referencia.
- Endpoint detalle cliente completo.
- Auditoria consistente para completar promesa y cambios sensibles.
- Health detallado protegido o reducido.

### Fase 2: operacion de cobranza completa

- Drawer por tabs y subdrawers por entidad.
- Libreta de contacto priorizada.
- Pago desde detalle de cliente/obligacion.
- Promesas vencidas automaticas.
- Acuerdos con calendario, mora y cumplimiento.
- Exportes de promesas/acuerdos/gestiones.
- Mejorar filtros por cartera, gestor, rango de mora, saldo y promesa.

### Fase 3: omnicanalidad real

- PBX/WebRTC real con proveedor elegido.
- Softphone embebido o bridge seguro.
- Webhooks entrantes de llamadas y grabaciones.
- WhatsApp Business/API real.
- Chatbot y templates aprobadas.
- Delivery/read receipts y timeline conversacional.

### Fase 4: UX premium operativa

- Navegacion por tabs en drawer.
- Subventanas para pagos, promesas, llamadas, documentos y obligaciones.
- Timeline unificado del cliente.
- Atajos operativos para gestor.
- Estados vacios y errores accionables por modulo.
- QA visual responsive por roles.

### Fase 5: hardening SaaS/preproduccion

- Matriz endpoint-permiso automatizada.
- Pruebas E2E con datos seed por rol.
- Pruebas de aislamiento con datos cruzados.
- Observabilidad, logs estructurados y metricas.
- Backups/restore verificados.
- Politica de secretos/vault para proveedores.
- Plan de migracion de tenants piloto.

## 17. Checklist QA manual para navegador

1. Iniciar sesion como SuperAdmin y validar que ve Gobierno SaaS, tenants, planes, suscripciones, modulos, auditoria y salud.
2. Iniciar sesion como Admin empresa y validar que no ve Gobierno SaaS global, pero si settings, usuarios, roles, proyectos, cargas y reportes de su empresa.
3. Iniciar sesion como Lider y validar que ve cola/equipo/carteras y no ve gobierno global.
4. Iniciar sesion como Gestor y validar que solo ve sus clientes asignados, puede abrir drawer y guardar gestion.
5. Iniciar sesion como Calidad/Auditor y validar lectura sin escritura de gestion.
6. Buscar cliente por documento, nombre y telefono.
7. Filtrar por proyecto/cartera, gestor, estado y riesgo.
8. Abrir cliente y validar resumen, obligaciones, actividad, promesas, pagos, demograficos, llamadas/documentos si aplica.
9. Crear gestion con obligacion, tipificacion, canal, nota y proxima fecha.
10. Crear promesa desde gestion y confirmar que aparece en promesas/drawer/dashboard.
11. Crear acuerdo y actualizar cuota.
12. Registrar pago manual y validar saldo de cliente, listado y exportacion.
13. Cargar template de clientes y validar preview.
14. Confirmar carga de reparto con gestor/lider y validar asignacion.
15. Cargar demograficos y validar que aparecen en detalle del cliente.
16. Cargar pagos y validar que aparecen en PayControl 360.
17. Cargar novedades y validar historial de gestion.
18. Intentar manipular `tenant_id` en filtros como Admin/Gestor y confirmar que no hay fuga.
19. Configurar extension y ejecutar click-to-call; confirmar `CallLog` y gestion simulada.
20. Ejecutar prueba de canal/webhook y confirmar evento simulado.

## 18. Casos de prueba recomendados

Backend:

- Crear cliente duplicado mismo tenant/documento debe devolver 409.
- Crear cliente mismo documento en tenant distinto debe permitirse.
- Pago manual con obligacion debe asociar pago y reducir saldo de obligacion.
- Pago por carga con `numero_obligacion` debe actualizar obligacion correcta.
- Pago duplicado por referencia debe ser idempotente.
- Promesa vencida debe calcularse o marcarse automaticamente.
- Completar promesa debe auditar.
- Drawer data endpoint debe retornar todos los relacionados por cliente.
- Admin no debe consultar ni descargar batch de otro tenant.
- Gestor no debe ver cliente de otro gestor.
- Lider debe ver equipo directo y carteras asignadas.
- Calidad debe leer y no escribir gestion.
- Health detallado debe requerir permiso si asi se define.

Frontend/UI:

- Menu visible por cada rol.
- Drawer de cliente mantiene contexto.
- Tabs/subdrawers muestran datos completos por entidad.
- Cargas muestran errores por fila y no permiten confirmar sin permisos.
- Click-to-call no abre protocolo externo y muestra estado simulado.
- Estados vacios por modulo son claros.
- Exportaciones se ocultan o fallan con 403 para roles sin permiso.

Integracion/preproduccion:

- Smoke login/menu/dashboard por rol.
- Carga reparto -> cola -> gestion -> promesa -> pago -> dashboard.
- Tenant isolation con query params manipulados.
- Telefonia simulada con extension activa/inactiva.
- Integraciones simuladas de canal/webhook.
- Exportaciones con auditoria.

## Fuentes revisadas

- `v2/backend/app/api/routes/administration.py`
- `v2/backend/app/api/routes/governance.py`
- `v2/backend/app/api/routes/subscriptions.py`
- `v2/backend/app/api/routes/teams.py`
- `v2/backend/app/api/routes/crm/*.py`
- `v2/backend/app/api/routes/uploads.py`
- `v2/backend/app/api/routes/telephony.py`
- `v2/backend/app/api/routes/integrations.py`
- `v2/backend/app/api/routes/recordings.py`
- `v2/backend/app/api/deps.py`
- `v2/backend/app/services/access_control.py`
- `v2/backend/app/services/menu_service.py`
- `v2/backend/app/services/dashboard_service.py`
- `v2/backend/app/models/*.py`
- `v2/frontend/static/index.html`
- `v2/frontend/static/assets/app.js`
- `v2/backend/tests/*.py`
