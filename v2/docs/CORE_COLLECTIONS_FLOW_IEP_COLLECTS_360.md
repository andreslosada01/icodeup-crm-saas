# Core funcional Collects 360 para IEP

## Diagnostico

La aplicacion ya tenia la base de clientes, actividades, promesas, pagos, acuerdos, demograficos y telefonia, pero el flujo operativo aun no estaba completo para un CRM de cobranzas real:

- Los pagos no podian quedar asociados a una obligacion especifica.
- Las obligaciones no tenian prioridad ni fechas operativas visibles para reparto y seguimiento.
- Los datos demograficos no distinguian contactabilidad, prioridad ni vigencia.
- La pantalla de acuerdos de pago seguia como placeholder.
- Telefonia no dejaba trazado el proyecto en el `CallLog`.
- Las futuras integraciones con App Pagos y QAudit necesitaban contratos internos seguros sin llamar servicios reales.

## Migracion

Se agrega la migracion aditiva `20260612_0007_collections_core_data_flow.py`.

Cambios:

- `payments.obligation_id` para asociar pagos a obligacion.
- `call_logs.project_id` para trazabilidad por proyecto.
- `customer_obligations.priority`, `due_date`, `assignment_date`.
- `customer_demographics.contactability`, `priority`, `valid_from`, `valid_until`.

La migracion no elimina datos. El `downgrade` queda no destructivo para proteger informacion operativa.

## Seed TEST incremental

El seed es idempotente y solo debe ejecutarse en TEST. No borra datos existentes y evita duplicados mediante llaves estables y `SEED_MARKER`.

Dry run:

```powershell
cd C:\Users\RALL2\Documents\Codex\2026-05-06\icodeup-crm-saas\v2\backend
.\.venv\Scripts\python.exe -m app.seeds.collects_core_demo --dry-run --limit-customers 10
```

Aplicar en TEST:

```powershell
cd C:\Users\RALL2\Documents\Codex\2026-05-06\icodeup-crm-saas\v2\backend
.\.venv\Scripts\python.exe -m app.seeds.collects_core_demo --confirm-test --limit-customers 10
```

Aplicar a una empresa especifica:

```powershell
.\.venv\Scripts\python.exe -m app.seeds.collects_core_demo --confirm-test --tenant-slug andina-servicios --limit-customers 10
```

Conteos esperados:

- El comando imprime JSON con `before`, `after` y `created` por tenant.
- Obligaciones: hasta 2 nuevas por cliente seleccionado.
- Demograficos: hasta 1 nuevo por cliente seleccionado.
- Acuerdos: hasta 5 acuerdos nuevos por tenant, con 3 cuotas cada uno.
- Telefonia: proveedor `IpCom Demo TEST` y extensiones demo `1001` y `1002` si hay usuarios coordinador/gestor.
- Modulo Telefonia: activa `tenant_modules.telephony` para el tenant demo con `enabled=true`, `is_enabled=true`, `enabled_at` y configuracion demo/simulated.
- En una segunda ejecucion, `created` debe tender a cero porque el seed es idempotente.

Validar Andina Servicios Integrales despues del seed:

```sql
select tm.module_code, tm.enabled, tm.is_enabled, tm.enabled_at, tm.configuration_json
from tenant_modules tm
join tenants t on t.id = tm.tenant_id
where t.name = 'Andina Servicios Integrales'
  and tm.module_code = 'telephony';
```

El resultado esperado es `enabled=true`, `is_enabled=true`, `enabled_at` informado y `configuration_json` con modo `simulated`.

## Pruebas funcionales manuales

Obligaciones:

- Entrar a Collects 360 y abrir un cliente.
- Ver matriz de obligaciones con numero, producto, saldo, mora, riesgo, prioridad y fecha de vencimiento.
- Registrar actividad sobre "Cliente completo" o una obligacion especifica.

Demograficos:

- Abrir drawer del cliente.
- Validar telefono, correo, direccion, ciudad, contactabilidad, prioridad y vigencia.
- Verificar que no se confundan con los datos base del cliente.

Acuerdos:

- Ir a la pantalla de acuerdos.
- Seleccionar cliente y, si aplica, obligacion.
- Crear un acuerdo con monto, cuotas y fecha inicial.
- Revisar tabla, estado y detalle de cuotas.

Pagos:

- Crear pago seleccionando cliente y obligacion.
- Confirmar que el payload envia `obligation_id`.
- Verificar que baja el saldo de la obligacion y se recalcula el saldo del cliente.

Telefonia:

- Con `TELEPHONY_REAL_CALLS_ENABLED=false`, iniciar click-to-call desde un cliente.
- Confirmar respuesta simulada segura.
- Revisar que `CallLog` quede con tenant, proyecto, cliente, obligacion si aplica, usuario y telefono.
- Si el modulo aun no esta activo, la ficha del cliente debe mostrar `Telefonia pendiente` y no el boton normal `Llamar`.
- Si el servicio TEST se esta reiniciando, refrescar la pagina debe conservar la sesion y mostrar un aviso temporal. Solo un 401 real debe enviar al login.

Integraciones futuras:

- `GET /api/integrations/readiness` muestra contratos internos de PayControl 360 y QAudit 360.
- `POST /api/integrations/paycontrol/payments/dry-run` valida payload de App Pagos sin llamar servicios reales.
- `POST /api/integrations/qaudit/evaluations/dry-run` valida payload de QAudit sin llamar servicios reales.
- Ambos dry-runs guardan `ChannelEventLog` con llave de idempotencia y separacion por tenant.

## Seguridad

- No ejecutar este seed automaticamente en produccion.
- No requiere secretos, `.env` reales ni credenciales externas.
- No conecta App Pagos, QAudit ni PBX real.
- Mantiene separacion por `tenant_id` y `project_id`.
