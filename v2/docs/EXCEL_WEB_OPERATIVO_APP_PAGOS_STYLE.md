# Mi Excel Web Operativo - Estilo App Pagos JJ

## 1. Problema anterior

Mi Excel Web funcionaba como una consulta tecnica con fuentes, columnas y vistas guardadas, pero no se leia como una hoja operativa para gestores, lideres o administradores. El usuario debia entender nombres de campos tecnicos y no habia una zona persistente para seguimiento diario.

## 2. Nuevo diseno operativo

La vista ahora se organiza como herramienta de trabajo:

- encabezado con alcance por rol;
- filtros superiores claros;
- KPIs de consulta y seguimiento;
- resumen visual por estado;
- tabla operativa paginada;
- formulario para agregar filas de seguimiento;
- tabla "Mi hoja de seguimiento" persistente;
- fuentes y vistas guardadas como apoyo, no como centro tecnico.

## 3. Fuentes disponibles por rol

- Gestor: clientes, obligaciones, gestiones, promesas, pagos, acuerdos, alertas y documentos propios.
- Lider: clientes, obligaciones, gestiones, promesas, pagos, acuerdos y alertas del equipo.
- Admin empresa: fuentes del tenant.
- SuperAdmin: fuentes de plataforma segun filtros y permisos.
- Abogado/comercial: fuentes permitidas por permisos especializados.

## 4. Filtros

La consulta operativa incluye:

- fuente de informacion;
- busqueda por cliente, documento, obligacion, nota o estado;
- proyecto/cartera;
- estado;
- riesgo;
- usuario/gestor para lideres y administradores;
- mora minima y maxima;
- fecha desde y hasta.

## 5. KPIs y resumen visual

La pantalla muestra:

- registros de consulta;
- valor de la pagina visible;
- seguimientos guardados;
- filas gestionadas;
- resumen en barras por estado.

## 6. Hoja de seguimiento

Se agrego la tabla `operational_sheet_rows` para persistir filas operativas. Campos principales:

- fecha compromiso;
- cartera/proyecto;
- cliente;
- documento;
- obligacion;
- gestion/nota;
- compromiso;
- valor;
- estado;
- proxima accion.

La fila queda guardada en PostgreSQL y se filtra por tenant y alcance de usuario.

## 7. Guardado en base de datos

Endpoints agregados:

- `GET /api/excel-web/sheet-rows`
- `POST /api/excel-web/sheet-rows`
- `PATCH /api/excel-web/sheet-rows/{row_id}`

Permisos:

- consultar: `excel_web.query`;
- crear/editar: `excel_web.views.manage`.

## 8. Paginacion

Mi Excel Web queda limitado a maximo 20 registros visibles por pagina. El backend tambien limita `ExcelWebQuery.page_size` a 20 para evitar bypass desde URL o llamadas manuales.

## 9. Alcance por rol

El alcance reutiliza la logica existente:

- gestor ve filas propias y clientes asignados;
- lider ve equipo y proyectos asignados;
- admin empresa ve tenant;
- platform admin ve plataforma;
- no hay fuga cross-tenant.

## 10. Pruebas ejecutadas

Validaciones esperadas para cierre:

- `python -m compileall .\app`
- `node --check .\v2\frontend\static\assets\app.js`
- `alembic current`
- `pytest`
- smoke real con gestor, lider y admin.

## 11. Riesgos pendientes

- La hoja permite crear y listar filas; la edicion inline visual queda pendiente para una iteracion posterior.
- Exportacion fisica CSV de Mi Excel Web sigue registrada/auditada, pero no descarga archivo fisico todavia.
- Las filas no se relacionan obligatoriamente con `customer_id` u `obligation_id` cuando el usuario ingresa datos manuales; se permite para flexibilidad operativa.
