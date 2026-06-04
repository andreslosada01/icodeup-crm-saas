# Sprint 2B - Diagnostico Excel Web Editable

## 1. Funcionamiento Actual

Mi Excel Web esta implementado como un modulo operativo dentro del frontend monolitico HTML/CSS/JavaScript y expone una hoja persistente mediante `OperationalSheetRow`.

El backend ya ofrece:

- `GET /api/excel-web/sheet-rows`
- `POST /api/excel-web/sheet-rows`
- `PATCH /api/excel-web/sheet-rows/{row_id}`
- `POST /api/excel-web/export`
- `GET/POST/PATCH /api/excel-web/views`

La consulta respeta tenant, rol, permisos y paginacion maxima de 20 filas por pagina.

## 2. Creacion de Filas

La creacion se hace con un formulario sobre la tabla. El formulario llama `POST /api/excel-web/sheet-rows` y guarda una fila asociada al usuario autenticado.

## 3. Edicion de Filas

La edicion actual es por fila: el usuario presiona `Editar`, la fila cambia a controles, y luego guarda con `PATCH /api/excel-web/sheet-rows/{row_id}`.

## 4. Parecido Actual a Hoja de Calculo

El modulo ya tiene tabla horizontal, filtros, KPIs, paginacion y export CSV. Aun asi, no se comporta como hoja de calculo porque las celdas no son editables directamente todo el tiempo y la creacion todavia depende de un formulario separado.

## 5. Brechas para Escritura Directa en Celdas

- Falta una fila nueva dentro de la grilla.
- Falta marcar celdas modificadas.
- Falta estado global de cambios sin guardar.
- Falta guardado por lote de filas modificadas.
- Falta cancelar cambios locales sin recargar toda la aplicacion.
- Falta navegacion basica con Enter, Tab y Escape.
- Falta bloqueo al cambiar de pagina cuando hay cambios pendientes.

## 6. Riesgos Tecnicos

- Enviar cambios incompletos o invalidos al backend.
- Perder ediciones locales al filtrar o paginar.
- Romper export, vistas o consulta operativa.
- Generar fuga de datos si se evita el scope backend. Este sprint conserva los endpoints existentes para mantener seguridad.
- Sobrecargar el frontend monolitico si se intenta replicar Excel completo.

## 7. Plan de Implementacion

1. Mantener backend y modelo actuales.
2. Reemplazar la edicion por boton `Editar` con celdas editables permanentes.
3. Agregar una fila `Nueva fila` dentro de la grilla.
4. Registrar cambios locales en `state.ops.excelSheetChanges`.
5. Guardar filas modificadas por PATCH una a una.
6. Crear nueva fila por POST si cumple datos minimos.
7. Agregar validaciones basicas en frontend.
8. Bloquear paginacion/filtros cuando existan cambios sin guardar.
9. Mantener maximo de 20 filas por pagina.
10. Agregar tests de permisos y alcance para PATCH.
