# Sprint 4 - Diagnostico de cargas, repartos y demograficos

## Estado actual

El producto ya tenia una base de cargas en `v2/backend/app/api/routes/uploads.py` con endpoints para preview, confirmacion, lotes y demograficos. La implementacion previa permitia validar un CSV simple y crear clientes solo en un caso acotado de `reparto_cartera` con `project_id`.

## Hallazgos principales

- `UploadBatch` ya existe y permite registrar tenant, proyecto, usuario, tipo de carga, conteos, mapeo y resumen JSON.
- `CustomerDemographic` ya existe y permite almacenar telefonos, emails, direccion, ciudad, empleador, referencia y score.
- `Customer` y `CustomerObligation` ya soportan tenant, proyecto/cartera y asignacion a gestor/lider.
- `UserProjectAssignment` ya permite asociar usuarios a proyectos/carteras con rol operativo y estado activo.
- La UI ya tenia una seccion `uploads`, pero estaba limitada a un formulario de archivo y no guiaba el flujo de mapeo, validacion, confirmacion y descarga.
- Los permisos `uploads.view`, `uploads.manage`, `uploads.repartos.manage`, `uploads.demographics.manage` y `uploads.download` ya existian.

## Brechas detectadas

- No habia permisos explicitos para `uploads.preview` y `uploads.confirm`.
- El preview no sugeria mapeo automatico de columnas.
- El preview no separaba campos requeridos y opcionales por tipo de carga.
- La confirmacion no procesaba obligaciones, demograficos, telefonos/emails/direcciones, pagos ni novedades operativas.
- Los resultados y errores se exponian como metadata basica, no como CSV util para operacion.
- El formulario incluia tipos no funcionales para el sprint, generando riesgo de botones muertos.
- No habia plantilla CSV descargable por tipo de carga.

## Riesgos tecnicos

- El frontend sigue siendo monolitico, por lo que los cambios visuales deben ser compatibles con las clases y eventos existentes.
- No se debe guardar archivo fisico real en repositorio ni en storage local sin una fase documental/storage separada.
- XLSX no se implementa en esta fase para evitar dependencias y conversiones adicionales; queda documentado como mejora posterior.
- Los pagos sin referencia pueden duplicarse si el archivo cambia de nombre o fecha de fila; se mitiga generando referencia automatica estable por archivo/fila/documento/valor/fecha.

## Recomendaciones

- Mantener CSV como formato operativo inicial.
- Usar `UploadBatch.summary_json` como almacenamiento temporal de errores/resultados hasta definir storage persistente por tenant.
- Procesar tipos de carga prioritarios y retirar opciones no funcionales de UI.
- Reforzar permisos por accion para que gestores operativos no puedan cargar repartos generales.
- Mantener idempotencia en clientes, obligaciones y demograficos usando documento, numero de obligacion y combinaciones de contacto.

## Tipos priorizados

| Tipo | Estado | Permiso principal |
| --- | --- | --- |
| `clientes` | Implementado | `uploads.manage` |
| `obligaciones` | Implementado | `uploads.repartos.manage` |
| `reparto_cartera` | Implementado | `uploads.repartos.manage` |
| `demograficos` | Implementado | `uploads.demographics.manage` |
| `telefonos_emails_direcciones` | Implementado | `uploads.demographics.manage` |
| `pagos` | Implementado | `uploads.manage` |
| `novedades_operativas` | Implementado base | `uploads.manage` |

## Pendientes

- Carga XLSX con parser seguro.
- Storage fisico controlado por tenant.
- Vista historica avanzada de lotes con paginacion completa.
- Validaciones configurables por empresa.
- Reglas de deduplicacion configurables para pagos y demograficos.
