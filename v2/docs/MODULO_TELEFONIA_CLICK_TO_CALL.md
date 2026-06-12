# Modulo Telefonia Click-to-Call

## 1. Objetivo

Agregar a Icodeup 360 una base corporativa para llamadas de cobranza desde la ficha del cliente, con extensiones por usuario, proveedores configurables por tenant, historial de llamadas y preparacion para telefonia embebida WebRTC.

## 2. Alcance actual

Incluye:

- modelos `TelephonyProvider`, `TelephonyExtension` y `CallLog`,
- migracion Alembic no destructiva,
- permisos `telephony.*`,
- menu dinamico para Telefonia,
- endpoints `/api/telephony`,
- UI base para proveedores, extensiones, mi telefono e historial,
- boton `Llamar` desde cola/ficha de gestion,
- click-to-call simulado o manual,
- auditoria de creacion/actualizacion y llamadas.

No incluye aun:

- llamada real contra PBX,
- softphone WebRTC activo,
- credenciales SIP,
- grabacion real,
- monitoreo en vivo de llamadas.

## 3. Click-to-call simulado

Cuando el usuario pulsa `Llamar`, el backend:

1. valida modulo `telephony`,
2. valida permiso `telephony.call`,
3. valida tenant,
4. valida extension activa del usuario,
5. valida cliente y obligacion si aplica,
6. crea un `CallLog` con estado `initiated`,
7. crea una `ManagementActivity` de canal `phone`,
8. registra auditoria,
9. responde que la llamada fue registrada en modo simulado.

Si no hay proveedor real o el proveedor es `manual`, no se ejecuta llamada real.

Si el usuario no tiene extension activa, la UI muestra un solo mensaje claro para que solicite configuracion al administrador. El boton queda bloqueado mientras la accion se procesa para evitar llamadas o toasts duplicados.

El frontend no debe renderizar `tel:`, `sip:` ni `callto:` para el boton `Llamar`. La accion debe ejecutarse siempre dentro del CRM mediante `POST /api/telephony/click-to-call`; asi se evita que el navegador abra el dialogo del sistema operativo para escoger una aplicacion externa.

## 3.1. Diferencia entre click-to-call simulado, integracion PBX y softphone web nativo

| Escenario | Estado | Que hace | Que no hace |
| --- | --- | --- | --- |
| Click-to-call simulado/manual | Actual | Valida usuario, tenant, permiso, extension y cliente. Registra `CallLog`, actividad y auditoria. | No origina una llamada real, no abre protocolos externos y no usa credenciales SIP. |
| Integracion PBX | Fase posterior | Conecta el evento interno con una PBX/API de prueba o produccion por tenant. | No debe exponer secretos en frontend ni mezclar extensiones entre tenants. |
| Softphone WebRTC embebido | Fase avanzada | Permite hablar desde el navegador con SIP sobre WebSocket, HTTPS y STUN/TURN. | No depende de Zoiper, MicroSIP, X-Lite ni prompts del sistema operativo. |

## 4. Que falta para llamada real

Para llamadas reales se requiere:

- proveedor PBX/API configurado por tenant,
- credenciales seguras en vault,
- motor que origine llamadas,
- eventos de estado,
- control de errores y reintentos,
- limites de uso,
- politicas de grabacion,
- pruebas en ambiente test.

## 5. Configurar extensiones

Un administrador de empresa o SuperAdmin puede:

1. entrar a `Telefonia`,
2. crear proveedor manual o PBX/API,
3. abrir `Extensiones`,
4. ver usuarios del tenant y su estado de extension,
5. crear extension para un usuario sin extension,
6. editar numero, nombre visible, proveedor, usuario SIP y dominio SIP,
7. activar o desactivar una extension.

El gestor ve su panel `Mi telefono` con la extension asignada. Si no tiene extension activa, el click-to-call devuelve un mensaje claro.

En local/demo se asegura un proveedor idempotente:

- Nombre: `Telefonia simulada local`
- Tipo: `manual`
- Estado: activo
- Llamada real: no ejecutada

Extensiones simuladas principales:

| Tenant | Usuario | Extension |
| --- | --- | --- |
| Andina demo | coord.cobranzas.andina@demo.icodeup.local | 1000 |
| Andina demo | gestor1.andina@demo.icodeup.local | 1001 |
| Andina demo | gestor2.andina@demo.icodeup.local | 1002 |
| Andina demo | admin.andina@demo.icodeup.local | 1099 |
| Icodeup Advisors piloto | lider.cobranzas.icodeup@demo.icodeup.local | 2000 |
| Icodeup Advisors piloto | gestor1.icodeup@demo.icodeup.local | 2001 |
| Icodeup Advisors piloto | gestor2.icodeup@demo.icodeup.local | 2002 |
| Icodeup Advisors piloto | gestor3.icodeup@demo.icodeup.local | 2003 |
| Icodeup Advisors piloto | gestor4.icodeup@demo.icodeup.local | 2004 |
| Icodeup Advisors piloto | gestor5.icodeup@demo.icodeup.local | 2005 |
| Icodeup Advisors piloto | admin.icodeup@demo.icodeup.local | 2099 |

## 6. Conexion a PBX

Los proveedores permiten parametrizar:

- `provider_type`,
- `host`,
- `port`,
- `websocket_url`,
- `api_url`,
- `config_json` sin secretos.

La integracion PBX real debera implementarse como servicio separado, idealmente desacoplado del endpoint de click-to-call para manejar latencia, eventos y reintentos.

## 7. Evolucion a WebRTC

La evolucion esperada es:

1. extension y proveedor manual,
2. PBX de test,
3. eventos de llamada,
4. softphone WebRTC embebido,
5. grabaciones y reportes avanzados.

WebRTC debe operar con HTTPS, SIP sobre WebSocket y STUN/TURN.

## 8. Seguridad

La implementacion actual:

- valida tenant en proveedores, extensiones, clientes y logs,
- valida permisos por accion,
- evita guardar claves sensibles en `config_json` y `metadata_json`,
- no guarda contrasenas SIP,
- no ejecuta llamadas reales sin integracion explicita,
- audita cambios y llamadas.

## 9. Limitaciones

- El modo actual es manual/simulado.
- No hay softphone web activo.
- No hay control de grabaciones reales.
- El consumo de llamadas no descuenta limites comerciales.
- Las metricas avanzadas de telefonia quedan para una fase posterior.
- La configuracion de proveedor no debe incluir contrasenas, tokens ni credenciales reales.

## 10. Proximos pasos

1. Configurar una PBX de prueba por tenant.
2. Definir vault de credenciales.
3. Implementar origen real de llamadas en ambiente test.
4. Agregar eventos de llamada y cierre automatico de `CallLog`.
5. Implementar softphone WebRTC MVP.
6. Agregar reporteria de llamadas, calidad y productividad.
