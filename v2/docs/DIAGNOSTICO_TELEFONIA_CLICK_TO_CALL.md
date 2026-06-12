# Diagnostico Telefonia Click-to-Call

## 1. Estado actual de telefonia

Icodeup 360 no tenia un modulo dedicado de telefonia IP. La operacion de cobranza ya contaba con acciones de canal desde la ficha o cola del cliente, pero el enlace telefonico dependia del esquema `tel:` del navegador y por tanto del sistema operativo o de un softphone externo instalado en el equipo.

Con esta fase se incorpora una base SaaS multi-tenant para configurar proveedores, extensiones por usuario e historial de llamadas. La marcacion real queda fuera de alcance hasta conectar una PBX, API externa o softphone WebRTC.

## 2. Click-to-call existente

Antes de esta fase, el boton de llamada abria una aplicacion externa mediante `tel:`. No existia:

- registro corporativo de intentos de llamada,
- extension asignada al usuario,
- control por proveedor,
- auditoria propia de telefonia,
- validacion por tenant/modulo/permiso,
- base para llamada embebida.

## 3. Campos de extension existentes

No habia una entidad formal para extensiones telefonicas por usuario. Se crea `TelephonyExtension` para asociar usuario, empresa, proveedor, numero de extension, usuario SIP no sensible, dominio SIP, estado y metadatos no sensibles.

No se guardan contrasenas SIP, tokens ni secretos. Cualquier credencial real debe vivir en un vault o servicio seguro en una fase posterior.

## 4. Canales e integraciones reutilizables

El CRM ya cuenta con patrones reutilizables:

- permisos granulares,
- modulos por tenant,
- auditoria operativa,
- actividades de gestion,
- ficha de cliente y cola de gestion,
- configuracion por tenant,
- frontend monolitico modular por secciones.

Telefonia reutiliza estos patrones y registra cada click-to-call como `CallLog` y como `ManagementActivity` de canal `phone`.

## 5. Integracion PBX

La integracion PBX puede evolucionar por fases:

1. Manual/simulada: registra la llamada sin marcar realmente.
2. API externa: invoca un proveedor de telefonia cloud cuando exista contrato y credenciales seguras.
3. Asterisk AMI: origina llamadas desde la PBX hacia la extension del agente y luego al cliente.
4. Asterisk ARI: controla llamadas con mayor granularidad y eventos.
5. WebRTC SIP: embebe un softphone en el navegador usando SIP sobre WebSocket.

La implementacion actual permite configurar `provider_type`, `host`, `port`, `websocket_url`, `api_url` y `config_json` sin secretos.

## 6. Integracion WebRTC

La ruta WebRTC requiere:

- PBX compatible con SIP sobre WebSocket,
- HTTPS obligatorio,
- certificados validos,
- servidor STUN/TURN para NAT,
- control seguro de credenciales,
- permisos de microfono del navegador,
- manejo de eventos de llamada,
- almacenamiento seguro de grabaciones si aplica.

Esta fase solo deja la base de datos, permisos, UI y endpoints para que WebRTC se integre sin redisenar el CRM.

## 7. Riesgos tecnicos

- Guardar credenciales SIP o API en texto plano abriria un riesgo alto.
- Una PBX mal segmentada podria permitir llamadas cruzadas entre tenants.
- WebRTC sin HTTPS o sin TURN puede fallar en redes corporativas.
- Grabaciones reales requieren politica de privacidad, retencion y permisos.
- La marcacion real debe controlar limites, horarios, auditoria y trazabilidad.

## 8. Recomendacion por fases

| Fase | Objetivo | Riesgo |
| --- | --- | --- |
| 1 | Click-to-call simulado con logs y extensiones | Bajo |
| 2 | Proveedor manual/API externa controlada | Medio |
| 3 | Integracion PBX AMI/ARI en ambiente test | Medio |
| 4 | Softphone WebRTC embebido | Alto |
| 5 | Grabaciones, monitoreo y reportes de llamadas | Medio |

La recomendacion es validar primero la operacion simulada, luego conectar una PBX de prueba por tenant y finalmente habilitar WebRTC en un ambiente con HTTPS y STUN/TURN.
