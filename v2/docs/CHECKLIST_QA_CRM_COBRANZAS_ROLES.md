# Checklist QA por rol - CRM cobranzas SaaS IEP

Fecha: 2026-08-01
Producto: IEP - Icodeup Enterprise Platform
Objetivo: validar en navegador que la experiencia operativa respeta rol, tenant, permisos y flujo de cobranza.

## Preparacion

- Usar ambiente interno/test con datos seed seguros.
- Confirmar que cada usuario tiene tenant, rol, perfil y proyecto/cartera asignados.
- No usar datos reales ni credenciales productivas.
- Registrar evidencias de pantalla por rol.
- Para pruebas de API o integracion, confirmar variables `ICODEUP_RUN_INTEGRATION_TESTS`, `ICODEUP_TEST_PLATFORM_PASSWORD` y `ICODEUP_TEST_TENANT_PASSWORD` solo en ambiente seguro.

## SuperAdmin IEP

| Paso | Validacion | Esperado |
| --- | --- | --- |
| 1 | Login SuperAdmin | Ingresa correctamente y ve branding IEP. |
| 2 | Menu visible | Ve Gobierno SaaS, empresas, planes, suscripciones, modulos, auditoria y salud. |
| 3 | Menu no operativo | No debe quedar forzado a cola de gestor como vista principal. |
| 4 | Listar empresas | Ve tenants cliente y datos comerciales globales. |
| 5 | Crear/editar tenant de prueba | Permite alta/edicion y registra auditoria. |
| 6 | Planes/suscripciones | Lista planes, suscripciones y modulos activos por empresa. |
| 7 | Activar/desactivar modulo | Cambio aplica a menu del tenant y rutas protegidas. |
| 8 | Roles/permisos | Ve permisos reservados y puede configurar roles globales/tenant. |
| 9 | Seguridad | Puede consultar effective access e insights de seguridad. |
| 10 | Auditoria | Ve eventos recientes, filtra por tenant/modulo/usuario. |
| 11 | Aislamiento | Al seleccionar tenant especifico, datos deben corresponder al tenant elegido. |
| 12 | Salud sistema | Verifica estado API/base sin exponer informacion excesiva en vista publica. |

Riesgos a observar:

- Que SuperAdmin pueda operar tenants cliente sin indicar contexto.
- Que modulos de subscriptions y governance muestren catalogos distintos.
- Que health publico revele mas informacion de la necesaria.

## Admin empresa

| Paso | Validacion | Esperado |
| --- | --- | --- |
| 1 | Login Admin empresa | Ingresa a su tenant y no ve Gobierno SaaS global. |
| 2 | Menu visible | Ve dashboard, settings empresa, roles/permisos, usuarios, equipos, cargas, reportes y operacion contratada. |
| 3 | Menu oculto | No ve empresas globales ni suscripciones globales. |
| 4 | Settings tenant | Puede ver/editar nombre, logo, colores y textos permitidos. |
| 5 | Usuarios | Lista solo usuarios de su empresa. |
| 6 | Crear usuario | Usuario queda en tenant correcto y con rol/perfil esperado. |
| 7 | Proyectos/carteras | Lista y asigna usuarios a proyectos de su tenant. |
| 8 | Lideres/gestores | Puede asociar lider y agente; ambos quedan en proyecto/cartera. |
| 9 | Roles/permisos | No ve ni asigna permisos reservados de plataforma. |
| 10 | Carga clientes/reparto | Preview valida archivo, confirma y crea/actualiza clientes/obligaciones. |
| 11 | Carga demograficos | Se vincula al cliente correcto del tenant. |
| 12 | Carga pagos | Pago aparece en PayControl 360 y dashboard; anotar que falta obligacion si aplica. |
| 13 | Auditoria tenant | Acciones se registran bajo su tenant. |
| 14 | Manipular tenant_id | Cambiar `tenant_id` por URL/API no debe exponer otro tenant. |

Riesgos a observar:

- Que pueda ver datos de otro tenant por filtros.
- Que cree clientes duplicados con mismo documento.
- Que pago por numero de obligacion no impacte saldo de obligacion.

## Lider operativo

| Paso | Validacion | Esperado |
| --- | --- | --- |
| 1 | Login Lider | Entra al panel de equipo. |
| 2 | Menu visible | Ve dashboard, cola, clientes, equipos/carteras, promesas, pagos, acuerdos y reportes segun permisos. |
| 3 | Menu oculto | No ve Gobierno SaaS global ni administracion global. |
| 4 | Equipo | Ve agentes directos y/o usuarios de proyectos asignados. |
| 5 | Cola | Ve casos de su equipo/cartera, no toda la empresa si no corresponde. |
| 6 | Filtros | Filtra por proyecto, gestor, estado y riesgo. |
| 7 | Abrir cliente | Drawer abre sin perder contexto. |
| 8 | Obligaciones | Ve obligaciones asociadas y gestor/lider asignado. |
| 9 | Gestion | Puede registrar gestion si tiene permiso; historial se actualiza. |
| 10 | Promesa | Puede crear promesa y verla en dashboard/listado. |
| 11 | Pago | Puede registrar pago si permiso; valida saldo cliente y listado. |
| 12 | Telefono | Con extension activa puede iniciar click-to-call simulado. |
| 13 | Logs llamadas | Ve llamadas propias/equipo segun permisos. |
| 14 | Exportar | Solo exporta si el permiso esta asignado. |

Riesgos a observar:

- Que el lider vea agentes fuera de su equipo.
- Que no pueda distinguir datos completos del cliente por limitaciones del drawer.
- Que click-to-call parezca llamada real cuando es simulada.

## Gestor / Agente de cobranza

| Paso | Validacion | Esperado |
| --- | --- | --- |
| 1 | Login Gestor | Entra a "Mi operacion" o dashboard operativo. |
| 2 | Menu visible | Ve cola/clientes propios, promesas, pagos, acuerdos, documentos si aplica y telefonia. |
| 3 | Menu oculto | No ve gobierno, tenant settings, roles/permisos, cargas generales, integraciones ni grabaciones por defecto. |
| 4 | Cola asignada | Solo muestra clientes asignados a su usuario. |
| 5 | Buscar | Busca por documento, nombre o telefono dentro de su alcance. |
| 6 | Abrir cliente | Drawer lateral muestra resumen sin cambiar de pantalla. |
| 7 | Gestion por obligacion | Selecciona obligacion, canal, resultado, nota y guarda. |
| 8 | Nota obligatoria | Si falta nota, UI debe advertir antes de guardar. |
| 9 | Estado cliente | Luego de guardar, cambia estado/proxima accion/historial. |
| 10 | Promesa desde gestion | Monto + fecha crea promesa y aparece en lista si entra en limite visible. |
| 11 | Crear acuerdo | Si tiene permiso, crea acuerdo desde drawer. |
| 12 | Pago manual | Si tiene permiso, registra pago; si no, endpoint debe devolver 403. |
| 13 | Click-to-call sin extension | Debe mostrar error claro de extension no configurada. |
| 14 | Click-to-call con extension | Crea llamada simulada y gestion "Click to call iniciado". |
| 15 | Cliente ajeno | Intentar abrir cliente de otro gestor debe devolver 403 o no aparecer. |
| 16 | Exportaciones | Deben estar ocultas o prohibidas si no tiene permisos. |

Riesgos a observar:

- Que el gestor vea clientes ajenos por filtros o cache.
- Que el drawer muestre pagos/promesas incompletos por listas de 20.
- Que canales externos WhatsApp/email salgan del flujo auditado si se usan directamente.

## Calidad / Auditor

| Paso | Validacion | Esperado |
| --- | --- | --- |
| 1 | Login Calidad/Auditor | Entra a vista de lectura operacional. |
| 2 | Menu visible | Ve dashboard, clientes/cola segun permisos, actividades, pagos/promesas/acuerdos en lectura, reportes y logs permitidos. |
| 3 | Menu oculto | No ve gobierno global ni acciones administrativas sensibles. |
| 4 | Cliente | Puede abrir detalle para revisar gestiones. |
| 5 | Crear gestion | Debe estar bloqueado si el rol es solo lectura. |
| 6 | Promesas/pagos/acuerdos | Puede consultar, no modificar si no tiene permiso. |
| 7 | Grabaciones | Si tiene permiso, puede ver/reproducir; debe auditar acceso. |
| 8 | Descargas/exportes | Solo disponibles con permiso explicito. |
| 9 | Aislamiento tenant | No ve datos de otra empresa. |
| 10 | Trazabilidad | Accesos sensibles quedan en auditoria. |

Riesgos a observar:

- Que calidad pueda escribir gestiones.
- Que pueda descargar grabaciones/exportes sin permiso.
- Que el acceso a playback no registre auditoria.

## Checklist transversal de cargas

| Paso | Tipo de carga | Esperado |
| --- | --- | --- |
| 1 | Descargar plantilla | CSV incluye columnas esperadas. |
| 2 | Preview sin columnas requeridas | Devuelve errores por fila y no procesa registros. |
| 3 | Preview con proyecto ajeno | Debe fallar por aislamiento. |
| 4 | Preview con gestor ajeno | Debe fallar por tenant. |
| 5 | Confirmar `create_records=false` | Crea lote validado sin crear registros. |
| 6 | Confirmar `create_records=true` | Crea/actualiza registros y lote auditable. |
| 7 | Descargar resultado | Devuelve CSV con filas procesadas. |
| 8 | Descargar errores | Devuelve CSV con detalle de errores. |
| 9 | Repetir carga | Debe actualizar o marcar duplicados segun regla esperada. |
| 10 | Rol sin permiso | Preview/confirm devuelven 403. |

## Checklist transversal de seguridad

- Probar URL con `tenant_id` de otro tenant para clientes, obligaciones, promesas, pagos, acuerdos, documentos, demograficos, batches, legal y sales.
- Probar acceso directo por ID de cliente/obligacion/batch extranjero.
- Confirmar que menu dinamico no muestra secciones sin modulo contratado.
- Confirmar que API tambien bloquea aunque se fuerce la URL.
- Confirmar que roles no administradores no ven permisos reservados.
- Confirmar que acciones criticas quedan en auditoria.

## Resultado esperado antes de produccion

- Todos los checks de aislamiento pasan.
- Todos los checks de permisos pasan.
- Pago queda asociado a obligacion cuando aplique.
- Cliente duplicado por documento queda bloqueado.
- Omnicanalidad real se etiqueta correctamente como real o simulada.
- Drawer cliente muestra datos completos por cliente, no solo caches limitadas.
- Suite de integracion corre contra ambiente interno con credenciales seguras.
