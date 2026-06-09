# Hotfix Funcional UX Real Fase 8C

## 1. Problemas reales detectados

La Fase 8B tenia una base tecnica amplia, pero varias pantallas se sentian como demostracion estatica. El gestor necesitaba registrar gestiones con confirmacion visible y el administrador necesitaba parametrizar sin tocar codigo.

## 2. Causa raiz

El backend ya exponia muchos endpoints, pero el frontend no los conectaba con formularios, estados de carga, toasts, errores visibles y acciones reales.

## 3. Correccion de guardar gestion

Se agrego un drawer operativo para el boton `Gestionar`. El formulario ahora:

- usa `POST /api/crm/customers/{id}/activities`,
- muestra loading,
- informa exito con toast,
- muestra error controlado,
- refresca cola, BI e historial,
- mantiene el cliente abierto para seguir operando.

## 4. Nueva UX de gestion

El drawer incluye:

- resumen del cliente,
- saldo, mora, riesgo, estado y gestor,
- acciones rapidas,
- formulario de gestion,
- actividad reciente,
- promesas, pagos, demograficos y grabaciones cuando el permiso aplica.

## 5. Correccion de menu y permisos

Se retiro Grabaciones del menu `operational_user` y del mapa de permisos base de `agent`. El bootstrap ahora tambien elimina permisos sobrantes de roles de sistema para mantener idempotencia.

## 6. Centro de Configuracion funcional

Se agregaron formularios conectados para:

- catalogos,
- reglas de negocio,
- reglas de alertas,
- workflows,
- etapas de workflows.

## 7. Integraciones funcional

Se agregaron formularios y acciones para:

- proveedores,
- canales,
- prueba de canal,
- plantillas,
- webhooks,
- prueba de webhook,
- logs de eventos.

Los secretos se mantienen enmascarados.

## 8. Cargas y Repartos funcional

Se agrego flujo:

- seleccionar CSV,
- tipo de carga,
- proyecto,
- mapeo JSON opcional,
- preview,
- confirmacion,
- consulta de resultado y errores.

## 9. Mi Excel Web funcional

Se agrego:

- seleccion de fuente,
- busqueda texto,
- columnas visibles,
- paginacion,
- ejecutar consulta,
- guardar vista,
- exportar con permiso.

## 10. Grabaciones restringido por permiso

Grabaciones solo carga si el menu autoriza la seccion. La pantalla autorizada permite:

- filtrar,
- ver detalle,
- solicitar playback,
- solicitar descarga,
- registrar acceso auditado por backend.

## 11. Botones muertos corregidos

Se agregaron `showToast`, `setButtonLoading` y `runAction`. Los botones principales ahora muestran resultado o error controlado.

## 12. Validaciones realizadas

Validaciones previstas:

- `node --check` frontend.
- `compileall` backend.
- `alembic current`.
- `pytest`.
- health local.
- smoke API de gestion, configuracion, integraciones, cargas, Excel Web y menu.

## 13. Riesgos pendientes

- QA visual manual en navegador por rol.
- Integraciones reales requieren proveedores productivos y secretos cifrados.
- Cargas XLSX queda pendiente; esta fase usa CSV seguro.
- Frontend sigue monolitico HTML/CSS/JS.
- Algunas ediciones avanzadas pueden requerir pantallas dedicadas futuras.
