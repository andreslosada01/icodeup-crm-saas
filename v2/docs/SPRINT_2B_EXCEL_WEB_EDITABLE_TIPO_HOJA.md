# Sprint 2B - Excel Web Editable Tipo Hoja

## 1. Resumen Ejecutivo

Mi Excel Web ahora permite operar una hoja editable tipo spreadsheet dentro de Icodeup 360. El usuario puede escribir directamente en celdas, crear una fila desde la grilla, modificar varias filas, ver cambios pendientes y guardar todo en base de datos.

## 2. Problema Anterior

El Sprint 2 habia dejado una hoja funcional, pero la experiencia seguia pareciendo una tabla con formulario y boton de edicion por fila. Para operacion diaria de cobranzas se necesitaba una experiencia mas cercana a Excel Web o Google Sheets empresarial.

## 3. Nueva Grilla Editable

La seccion `Mi hoja de seguimiento` ahora muestra:

- una fila superior `Nueva fila`,
- celdas editables permanentes,
- select para estado,
- select para cartera/proyecto cuando hay proyectos disponibles,
- celdas modificadas resaltadas,
- indicador de fila `Sin guardar`,
- barra de acciones para guardar o cancelar cambios.

## 4. Como Crear Fila

1. Escribir en la fila `Nueva fila`.
2. Diligenciar al menos:
   - cliente o documento,
   - gestion o compromiso,
   - estado.
3. Presionar `Guardar cambios`.
4. El sistema ejecuta `POST /api/excel-web/sheet-rows`.
5. La fila queda persistida y la grilla se refresca.

## 5. Como Editar Celdas

1. Hacer clic en una celda editable.
2. Escribir directamente.
3. La celda queda resaltada.
4. La fila queda marcada como `Sin guardar`.
5. Presionar `Guardar cambios`.
6. El sistema ejecuta `PATCH /api/excel-web/sheet-rows/{row_id}` por cada fila modificada.

## 6. Como Guardar Cambios

El guardado es por lote seguro:

- se valida la fila nueva,
- se validan filas modificadas,
- se crea la fila nueva si aplica,
- se actualizan las filas existentes una a una,
- se muestra un resumen de filas creadas y actualizadas.

No se implementa autosave por celda en este sprint para evitar operaciones involuntarias y reducir riesgo operativo.

## 7. Permisos

Permisos involucrados:

- `excel_web.view`
- `excel_web.query`
- `excel_web.sheet.manage`
- `excel_web.views.manage`
- `excel_web.export`

`excel_web.sheet.manage` controla la creacion y edicion de filas. `excel_web.views.manage` queda como compatibilidad legacy.

## 8. Alcance por Rol

- Gestor: ve y edita sus propias filas.
- Lider: ve filas de su equipo/proyectos segun scope.
- Admin empresa: ve filas de su tenant.
- SuperAdmin Icodeup: ve segun alcance global autorizado.

El backend conserva el filtro por tenant y rol. Si un gestor intenta editar una fila fuera de alcance, recibe acceso bloqueado o no encontrado seguro.

## 9. Paginacion

La hoja mantiene maximo 20 registros persistidos por pagina. La fila `Nueva fila` se muestra adicionalmente para captura rapida. Si existen cambios sin guardar, la navegacion de pagina y filtros se bloquean con mensaje:

`Tienes cambios sin guardar. Guarda o cancela antes de cambiar de pagina.`

## 10. Limitaciones Actuales

- No hay formulas.
- No hay copiado/pegado masivo tipo Excel.
- No hay edicion por lote desde portapapeles.
- No hay autocompletado avanzado de clientes u obligaciones.
- No hay autosave por celda.

## 11. Diferencias Frente a Microsoft Excel

La meta es una hoja operativa del CRM, no un reemplazo completo de Excel. La grilla esta integrada con permisos, tenant, auditoria, usuarios, cartera y persistencia en PostgreSQL.

## 12. Proximos Pasos

- Copiar/pegar rangos desde Excel.
- Autocomplete de cliente y obligacion.
- Validaciones por columna configurables.
- Historial de cambios por celda.
- Guardado masivo optimizado en backend.
