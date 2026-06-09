# Sprint 1 - Diagnostico operativo gestor

## Resumen ejecutivo

La base SaaS de Icodeup 360 ya permitia al gestor autenticarse, ver su cola, abrir clientes asignados, registrar gestiones, consultar promesas, pagos, documentos y Mi Excel Web segun permisos. El punto debil principal era la trazabilidad operativa por obligacion: el cliente podia tener varias obligaciones detalladas, pero las gestiones, promesas y acuerdos se registraban solo a nivel cliente.

## Estado actual revisado

- Backend CRM modular en `app/api/routes/crm/`.
- Modelo `CustomerObligation` existente y cargado por demo.
- Endpoint `GET /api/crm/customers/{customer_id}/obligations` existente.
- Drawer operativo del frontend con gestion, actividad reciente, promesas, pagos, demograficos y grabaciones cuando aplica.
- Mi Excel Web ya filtra por rol operativo y expone obligaciones.

## Brechas encontradas

- `ManagementActivity`, `PaymentPromise` y `PaymentAgreement` no tenian `obligation_id`.
- Las respuestas de actividad/promesa/acuerdo no mostraban numero de obligacion.
- El drawer no cargaba obligaciones del cliente.
- El formulario de gestion no permitia seleccionar obligacion.
- El agente gestor podia ver acuerdos y documentos, pero el rol `collections_agent` no tenia permisos de creacion para cerrar acuerdo o soporte operativo.
- Documentos no tiene relacion directa con obligacion; por ahora se puede asociar a cliente/acuerdo y referenciar la obligacion en notas.

## Riesgos

- Riesgo bajo: columnas nullable y sin cambios destructivos.
- Riesgo medio: los permisos nuevos dependen de que el bootstrap actualice `RolePermission` al reiniciar el servicio.
- Riesgo bajo: soporte documental por obligacion queda como metadata en notas hasta ampliar el modelo documental.

## Recomendacion

Cerrar el flujo operativo con cambios aditivos: enlazar gestiones, promesas y acuerdos a obligaciones; cargar obligaciones en el drawer; permitir al gestor crear acuerdos y soportes metadata sin exportes ni administracion.
