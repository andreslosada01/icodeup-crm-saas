# Sprint 1 - Cierre operativo gestor cobranzas

## Resumen de cambios

Se cerro el flujo operativo del gestor para trabajar por cliente completo o por obligacion especifica, manteniendo compatibilidad con `Customer.obligation` legacy.

## Backend

- `ManagementActivity` ahora acepta `obligation_id` opcional.
- `PaymentPromise` ahora acepta `obligation_id` opcional.
- `PaymentAgreement` ahora acepta `obligation_id` opcional.
- Los endpoints validan que la obligacion pertenezca al cliente y al tenant visible.
- Las respuestas devuelven `obligation_id` y `obligation_number`.
- El cierre de promesa genera actividad con la obligacion asociada.
- El bootstrap demo enlaza actividades, promesas y acuerdos existentes a obligaciones cuando aplica.

## Frontend

- Al seleccionar cliente se cargan tambien sus obligaciones.
- El detalle de cola muestra obligaciones del cliente.
- El drawer operativo muestra obligaciones en matriz horizontal.
- Los formularios de gestion y acuerdo permiten seleccionar obligacion.
- Las actividades y promesas muestran numero de obligacion cuando existe.
- El gestor puede registrar soporte documental metadata desde el drawer si tiene modulo documental activo.

## Permisos

El rol operativo `collections_agent` conserva alcance restringido, pero ahora puede:

- crear acuerdos de pago;
- crear documentos metadata;
- seguir sin exportar clientes, pagos, documentos o Excel Web.

## Migracion

Migracion no destructiva:

- `20260603_0004_sprint1_obligation_links.py`

Columnas nuevas nullable:

- `management_activities.obligation_id`
- `payment_promises.obligation_id`
- `payment_agreements.obligation_id`

## Pendientes

- Relacion directa `documents.obligation_id` queda recomendada para una fase posterior si el modulo documental requiere trazabilidad juridica/operativa por deuda.
- QA visual en navegador debe hacerse tras reiniciar el servicio para garantizar que el frontend y bootstrap nuevos esten cargados.
