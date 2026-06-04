# Sprint 2 - Diagnostico Mi Excel Web

## Resumen

Mi Excel Web ya existia como modulo operativo dentro de Icodeup 360, con fuentes consultables, vistas guardadas y una hoja persistente en base de datos. El diagnostico confirma que la base tecnica era correcta, pero la experiencia visual todavia no comunicaba una hoja operativa tipo CRM/ERP ni permitia editar filas desde la interfaz.

## Estado Actual Detectado

- Backend: `v2/backend/app/api/routes/excel_web.py`
- Modelo persistente: `OperationalSheetRow`
- Esquemas: `OperationalSheetRowCreate`, `OperationalSheetRowPatch`, `OperationalSheetRowOut`
- Frontend: `v2/frontend/static/assets/app.js`
- Estilos: `v2/frontend/static/assets/styles.css`
- Data demo: `v2/backend/app/services/bootstrap_service.py`

## Funcionalidades Existentes

- Fuentes de datos por modulo: clientes, obligaciones, gestiones, promesas, pagos, acuerdos, juridico, ventas, documentos, cargas y alertas.
- Consulta paginada con maximo 20 registros visibles por pagina.
- Vistas guardadas por usuario o publicas por tenant.
- Hoja operativa persistente con registros manuales.
- Alcance por rol:
  - Gestor: datos propios/asignados.
  - Lider: equipo y proyectos asignados.
  - Admin empresa: tenant completo.
  - Superadmin Icodeup: alcance global autorizado.
- Export controlado por permiso `excel_web.export`.

## Brechas Identificadas

- La hoja persistente no tenia filtros superiores propios.
- La UI no mostraba matriz horizontal completa tipo hoja operativa.
- Las filas no se podian editar inline desde el frontend.
- El export de Mi Excel Web no descargaba un CSV real.
- El permiso de administracion de filas usaba una semantica heredada de vistas guardadas.
- La respuesta de filas no mostraba el nombre del usuario responsable.

## Riesgos

- Riesgo de fuga multi-tenant si los filtros de usuario/proyecto no pasan por scope backend.
- Riesgo de exportes excesivos si no se limita cantidad de filas.
- Riesgo visual si la tabla intenta encajar demasiadas columnas sin scroll horizontal controlado.
- Riesgo operativo si el gestor puede ver o editar filas que no pertenecen a su alcance.

## Recomendacion

Fortalecer el modulo sin crear arquitectura nueva:

- Mantener `OperationalSheetRow`.
- Agregar permiso semantico `excel_web.sheet.manage`.
- Mantener `excel_web.views.manage` como compatibilidad.
- Implementar filtros propios de hoja.
- Permitir edicion inline.
- Descargar CSV real con limite seguro.
- Documentar que no hay migracion requerida porque el modelo ya existia.

## Resultado Sprint 2

El sprint convierte Mi Excel Web en una hoja operativa empresarial con consulta, filtros, KPIs, resumen por estado, tabla horizontal, creacion, edicion, vistas guardadas y export seguro.
