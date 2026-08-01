# Telefonia funcional IpCom y click-to-call

## Alcance de esta fase

Esta fase prepara IEP - Icodeup Enterprise Platform para operar telefonia configurable por tenant sin ejecutar llamadas reales por defecto.

El objetivo es que `Telefonia` permita administrar proveedores, extensiones de usuario, reglas de marcado y logs de llamadas. El click-to-call sigue siendo seguro/simulado mientras `TELEPHONY_REAL_CALLS_ENABLED` sea `false`.

No se guardan secretos en base de datos ni archivos versionados. Credenciales AMI, API o WebRTC deben vivir en variables de entorno o en un vault en una fase posterior.

## Arquitectura recomendada

Flujo recomendado para IpCom:

```text
IEP CRM -> Backend Telefonia -> Asterisk/FreePBX via AMI -> Troncal SIP IpCom -> Red telefonica
```

En esta fase el backend solo:

- valida permisos y tenant,
- obtiene la extension activa del usuario,
- selecciona el proveedor principal activo del tenant,
- normaliza el telefono destino,
- construye el `dial_string`,
- registra `CallLog`,
- crea `ManagementActivity`,
- deja metadata para trazabilidad.

La ejecucion real queda pendiente para un conector AMI/WebRTC/API.

## Configuracion observada de IpCom

Datos no sensibles configurables en el proveedor:

| Campo | Valor observado |
| --- | --- |
| `trunk_name` | `IpCom` |
| `provider_type` | `sip_trunk` |
| `host` | `35.192.135.117` |
| `port` | `5060` |
| `dtmf_mode` | `rfc2833` |
| `nat` | `force_rport,comedia` |
| `insecure` | `port,invite` |
| `codecs` | `ulaw,alaw,g729` |
| `external_prefix` | `0218739#` |
| `mobile_prepend` | `000157` |
| `mobile_match_pattern` | `3XXXXXXXXX` |
| `country_context` | `Colombia` |
| `outbound_enabled` | `true` |
| `priority` | `1` |
| `is_primary` | `true` |

La UI incluye un boton `Preset IpCom` que carga estos valores no sensibles. Deben revisarse antes de guardar.

## Diferencias tecnicas

| Tipo | Uso | Estado en IEP |
| --- | --- | --- |
| SIP trunk | Troncal del carrier, por ejemplo IpCom. Normalmente no origina directo desde el CRM. | Configurable como proveedor. |
| PBX | Central telefonica que controla extensiones y rutas salientes. | Recomendado como capa entre IEP e IpCom. |
| Asterisk AMI | Interfaz para originar llamadas desde Asterisk/FreePBX. | Preparado por variables de entorno, sin llamada real aun. |
| WebRTC SIP | Softphone embebido en navegador con SIP sobre WebSocket. | Fase futura. |
| Proveedor API | CPaaS/API externa que origina llamadas por HTTP. | Fase futura. |

## Regla de marcado movil

La normalizacion de destino:

1. Limpia espacios, guiones y parentesis.
2. Acepta celular colombiano de 10 digitos que inicia por `3`.
3. Si llega con prefijo `57` y tiene 12 digitos, lo convierte a numero nacional.
4. Aplica `external_prefix + mobile_prepend + phone`.

Ejemplo:

```text
phone = 3001234567
external_prefix = 0218739#
mobile_prepend = 000157
dial_string = 0218739#0001573001234567
```

Si el numero no cumple la regla, el endpoint rechaza la solicitud y no registra llamada.

## Variables de entorno

Valores de ejemplo en `v2/.env.example`:

```env
TELEPHONY_REAL_CALLS_ENABLED=false
ASTERISK_AMI_HOST=
ASTERISK_AMI_PORT=5038
ASTERISK_AMI_USERNAME=
ASTERISK_AMI_SECRET=
ASTERISK_AMI_ORIGINATE_CONTEXT=from-internal
ASTERISK_AMI_ORIGINATE_TIMEOUT_MS=30000
```

`ASTERISK_AMI_SECRET` queda vacio en versionado. No debe escribirse en `config_json`.

## Flujo click-to-call

1. El gestor presiona `Llamar` desde el drawer del cliente.
2. El frontend llama a `POST /api/telephony/click-to-call`.
3. El backend exige `telephony.call`.
4. El backend busca la extension activa del usuario autenticado.
5. El backend busca el proveedor principal activo y con salida habilitada para el tenant.
6. Si no hay proveedor principal, usa el proveedor activo asociado a la extension.
7. Normaliza el telefono y genera el `dial_string`.
8. Registra `CallLog` con metadata:
   - telefono original,
   - telefono normalizado,
   - `dial_string`,
   - modo,
   - proveedor,
   - extension,
   - `real_call_executed=false`,
   - `source`.
9. Crea `ManagementActivity` asociada al cliente y obligacion, si aplica.
10. Devuelve mensaje claro a la UI.

Mensaje cuando el modo real no esta habilitado:

```text
Llamada registrada en modo simulado. Para marcacion real, active integracion PBX/AMI/WebRTC.
```

## Activar o desactivar proveedores

Desde `Telefonia > Proveedores`:

- `Activar`: habilita el proveedor para uso operativo.
- `Desactivar`: lo inhabilita y, si era principal, deja de ser principal.
- `Principal`: marca el proveedor como principal saliente y desmarca otros principales del mismo tenant.
- `Probar`: genera una prueba segura con telefono demo `3000000000`; no ejecuta llamada real.

Un proveedor principal debe estar activo y con salida habilitada.

## Pasos para modo real futuro

1. Crear PBX de prueba o usar FreePBX/Asterisk controlado.
2. Configurar troncal IpCom en la PBX, no en el frontend.
3. Crear usuario AMI con permisos minimos para `Originate`.
4. Definir variables de entorno reales fuera de git.
5. Activar `TELEPHONY_REAL_CALLS_ENABLED=true` solo en ambiente controlado.
6. Implementar servicio backend de originate con timeouts, retries, auditoria y manejo de eventos.
7. Validar grabaciones, estados de llamada y finalizacion.
8. Repetir pruebas por tenant antes de produccion.

## Riesgos y pendientes

- NAT/SIP puede requerir ajustes de red en PBX.
- G.729 puede requerir codec/licencia segun la PBX.
- WebRTC necesita HTTPS, SIP sobre WebSocket y STUN/TURN.
- AMI debe protegerse con red privada, firewall y usuario minimo.
- Falta implementar originate real, eventos de llamada y reconciliacion de estados.
- Falta estrategia de vault para secretos productivos.

## Checklist QA manual

- Crear proveedor IpCom con preset y confirmar que no guarda secretos.
- Marcar IpCom como principal y verificar que otros principales pasan a secundario.
- Desactivar proveedor principal y confirmar que deja de ser principal.
- Crear extension para un usuario del mismo tenant.
- Intentar crear extension con usuario de otro tenant y confirmar rechazo.
- Ejecutar `Probar` proveedor y revisar `dial_string`.
- Ejecutar click-to-call con `3001234567` y confirmar `CallLog`.
- Revisar metadata: `dial_string`, `mode=simulated`, `real_call_executed=false`.
- Intentar click-to-call con `2012345678` y confirmar error sin llamada.
- Confirmar que no existen enlaces `tel:`, `sip:` o `callto:` en frontend.
