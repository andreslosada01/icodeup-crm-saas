# Arquitectura Softphone WebRTC Icodeup 360

## Vision

El objetivo futuro es que Icodeup 360 tenga un telefono web nativo dentro del navegador, sin depender como unica opcion de softphones instalados como Zoiper, MicroSIP o X-Lite.

La implementacion real debe hacerse por fases para proteger seguridad, estabilidad y aislamiento multi-tenant.

## Componentes

1. Frontend Icodeup 360: panel de telefono, estado de extension, controles de llamada y eventos.
2. API FastAPI: valida usuario, tenant, modulo, permiso y genera tokens/configuracion temporal.
3. PBX compatible: Asterisk, FreePBX, Issabel u otro proveedor con SIP sobre WebSocket.
4. WebSocket SIP: canal de senalizacion entre navegador y PBX.
5. WebRTC media: audio entre navegador y PBX.
6. STUN/TURN: soporte para NAT y redes corporativas.
7. Vault de secretos: custodia segura de credenciales SIP/API.
8. Auditoria y logs: trazabilidad de llamadas, fallos y eventos.

## SIP sobre WebSocket

El navegador no usa SIP UDP/TCP tradicional. Para WebRTC se requiere SIP sobre WebSocket, normalmente expuesto por la PBX en una URL `wss://`.

La extension del usuario debe estar autorizada para WebRTC y asociada al tenant correcto. La aplicacion no debe exponer credenciales permanentes en el frontend.

## HTTPS obligatorio

WebRTC requiere contexto seguro para microfono y medios. En test y produccion debe usarse HTTPS con certificado valido. En local puede usarse una excepcion controlada, pero no debe ser criterio de produccion.

## STUN/TURN

STUN ayuda a descubrir rutas de red. TURN relaya audio cuando el usuario esta detras de NAT, firewall o VPN restrictiva. Sin TURN, muchas redes corporativas tendran llamadas sin audio o con fallos intermitentes.

## Seguridad de credenciales

No guardar en base de datos:

- contrasenas SIP,
- tokens API,
- secrets,
- private keys,
- credenciales de proveedor.

La fase futura debe usar vault o credenciales temporales. El backend deberia entregar al frontend una configuracion temporal y limitada para iniciar sesion WebRTC.

## Flujo de llamada futuro

1. El gestor abre un cliente.
2. El frontend consulta `/api/telephony/my-extension`.
3. El usuario pulsa `Llamar`.
4. El backend valida `telephony.call`, tenant, cliente y extension.
5. Si WebRTC esta activo, el frontend origina la llamada desde el softphone embebido.
6. La PBX emite eventos de ringing, answered, completed o failed.
7. El backend actualiza `CallLog`.
8. Si aplica, se asocia grabacion y actividad de gestion.

## Proveedores posibles

- Asterisk puro.
- FreePBX.
- Issabel.
- Proveedor cloud con API de llamadas.
- Gateway SIP compatible con WebRTC.
- Plataforma CPaaS con SDK WebRTC.

La seleccion debe considerar costos, soporte de grabaciones, seguridad, escalabilidad y experiencia de agentes.

## Fases de implementacion real

| Fase | Alcance |
| --- | --- |
| Base actual | Proveedores, extensiones, logs y click-to-call simulado |
| PBX test | Proveedor de prueba por tenant sin trafico productivo |
| Eventos | Sincronizacion de estados y duracion de llamadas |
| WebRTC MVP | Softphone embebido para un tenant piloto |
| Produccion | Vault, TURN, monitoreo, grabaciones y soporte |

## Riesgos

- Exponer credenciales en navegador.
- Mezclar extensiones entre tenants.
- Fallos de audio por NAT/firewall.
- No cumplir politicas de consentimiento de grabacion.
- Saturar PBX sin limites por plan o tenant.
- Generar costos por llamadas sin controles.

## Decision de esta fase

Esta fase no implementa WebRTC real. Se deja la arquitectura preparada con entidades, permisos, UI, auditoria y endpoints para evolucionar a softphone web sin reescribir el core.

La operacion actual usa proveedor `manual` y extensiones simuladas por tenant demo/piloto. El CRM registra `CallLog` y actividad de gestion, pero no origina trafico SIP, no abre microfono y no usa credenciales reales.

## Diferencia entre click-to-call simulado, integracion PBX y softphone web nativo

El flujo actual de `Llamar` es interno al CRM. No debe usar `tel:`, `sip:`, `callto:`, `window.location` ni `window.open` para abrir aplicaciones externas. El frontend llama a `POST /api/telephony/click-to-call`, y el backend registra una llamada simulada/manual con trazabilidad.

En una integracion PBX futura, el mismo endpoint podra delegar a un servicio desacoplado que origine la llamada mediante una PBX o API autorizada por tenant. Esa fase requiere vault de secretos, control de costos, eventos de llamada y pruebas en servidor test.

En la fase avanzada de softphone WebRTC embebido, el navegador tendra controles de llamada nativos dentro de Icodeup 360. Ese escenario requiere HTTPS, SIP sobre WebSocket, STUN/TURN y credenciales temporales. Incluso en esa fase, la experiencia debe permanecer dentro del CRM y no depender de softphones externos instalados.
