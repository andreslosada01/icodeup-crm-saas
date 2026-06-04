# Sprint 4 - Cargas, repartos, demograficos y asignaciones masivas

## Objetivo

Cerrar el flujo funcional inicial para operar cartera desde archivos CSV en Icodeup 360 Collection & Legal CRM, respetando tenant, proyecto/cartera, lider, gestor, permisos y auditoria.

## Flujo funcional

1. El usuario autorizado entra a **Cargas y repartos**.
2. Selecciona tipo de carga y proyecto/cartera opcional.
3. Descarga plantilla o carga un CSV propio.
4. El sistema ejecuta `POST /api/uploads/preview`.
5. El preview devuelve columnas detectadas, muestra maxima de 20 filas, mapeo sugerido, campos requeridos y errores por fila.
6. El usuario confirma con `POST /api/uploads/confirm`.
7. El sistema procesa filas validas, crea `UploadBatch`, registra auditoria y almacena errores/resultados en `summary_json`.
8. El usuario descarga resultados o errores con:
   - `GET /api/uploads/batches/{id}/result`
   - `GET /api/uploads/batches/{id}/errors`

## Endpoints

| Endpoint | Proposito |
| --- | --- |
| `POST /api/uploads/preview` | Previsualiza CSV, sugiere mapeo y valida filas. |
| `POST /api/uploads/confirm` | Confirma carga y procesa registros validos. |
| `GET /api/uploads/templates/{upload_type}` | Devuelve plantilla CSV por tipo de carga. |
| `GET /api/uploads/batches` | Lista lotes paginados maximo 20. |
| `GET /api/uploads/batches/{id}` | Consulta lote individual. |
| `GET /api/uploads/batches/{id}/errors` | Devuelve CSV dinamico de errores. |
| `GET /api/uploads/batches/{id}/result` | Devuelve CSV dinamico de resultados. |
| `GET /api/uploads/demographics` | Lista demograficos por tenant. |

## Permisos

| Accion | Permiso |
| --- | --- |
| Ver modulo | `uploads.view` |
| Previsualizar | `uploads.preview` o permiso compatible de carga |
| Confirmar | `uploads.confirm` + permiso especifico del tipo |
| Cargar clientes/pagos/novedades | `uploads.manage` |
| Cargar obligaciones/repartos | `uploads.repartos.manage` |
| Cargar demograficos/contactos | `uploads.demographics.manage` |
| Descargar resultados/errores | `uploads.download` |

Los gestores operativos no ven el modulo de cargas en el menu y el backend bloquea el acceso si no tienen permisos.

## Tipos de carga implementados

### Clientes

Campos requeridos:

- `document`
- `name`

Campos comunes:

- telefono, email, ciudad, segmento, saldo, dias de mora, estado, riesgo, gestor, cartera/proyecto.

### Obligaciones

Campos requeridos:

- `document`
- `obligation_number`

Actualiza o crea obligaciones por `tenant_id + obligation_number`.

### Reparto de cartera

Campos requeridos:

- `document`

Puede crear/actualizar cliente, obligacion, asignacion a gestor, asignacion a lider y asignacion usuario-proyecto.

### Demograficos

Campos requeridos:

- `document`

Crea o actualiza datos de contacto y enriquecimiento del cliente.

### Telefonos, emails y direcciones

Variante enfocada en contactabilidad. Usa el mismo modelo `CustomerDemographic`.

### Pagos

Campos requeridos:

- `document`
- `amount`

Crea pagos, descuenta saldo del cliente y registra actividad operacional. Si no hay referencia de pago se genera una referencia automatica `UPLOAD-*`.

### Novedades operativas

Campos requeridos:

- `document`
- `result`

Crea actividad de gestion desde archivo.

## Mapeo de columnas

El backend normaliza encabezados y reconoce sinonimos en espanol e ingles. Ejemplos:

| Campo destino | Sinonimos |
| --- | --- |
| `document` | documento, cedula, identificacion, nit |
| `name` | nombre, cliente, deudor, razon_social |
| `current_balance` | saldo_actual, saldo, capital |
| `days_past_due` | mora, dias_mora |
| `assigned_user_email` | gestor_email, email_gestor |
| `assigned_leader_email` | lider_email, coordinador_email |

Tambien se puede enviar `mapping` manual en JSON desde la UI.

## Seguridad multi-tenant

- Todo preview/confirm resuelve tenant con `require_tenant`.
- Los proyectos se validan contra el tenant.
- Los usuarios asignados se validan contra el tenant.
- Los clientes, obligaciones, pagos y demograficos se crean siempre con `tenant_id`.
- Platform admin puede operar con tenant indicado.
- Usuarios cliente no pueden cargar datos de otra empresa.

## Auditoria

Cada confirmacion registra evento `upload_batch.confirm` con:

- tenant
- usuario
- tipo de carga
- filas totales
- filas validas
- errores
- id del lote

No se audita `csv_text` ni contenido completo del archivo.

## Limites actuales

- Solo CSV en esta fase.
- No se almacena archivo fisico.
- Resultado/error se guarda resumido en `UploadBatch.summary_json`.
- Los endpoints de descarga devuelven CSV dinamico como texto en JSON para permitir descarga autenticada desde frontend.

## Siguiente mejora recomendada

- Parser XLSX controlado.
- Vista paginada de errores por lote.
- Reglas de validacion configurables por empresa/proyecto.
- Persistencia de archivos en storage por tenant.
- Jobs asincronos para cargas superiores a miles de filas.
