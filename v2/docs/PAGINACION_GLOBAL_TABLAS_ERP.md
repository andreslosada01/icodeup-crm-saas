# Paginacion Global de Tablas ERP

## 1. Regla maxima

Toda tabla renderizada por el helper frontend `table()` muestra maximo 20 registros por pagina.

La regla busca evitar listados largos, mejorar lectura operativa y mantener una experiencia empresarial compacta.

## 2. Tablas impactadas

La regla aplica a tablas/matrices que usan `table()` en:

- tablero y BI;
- cola de gestion;
- clientes;
- promesas;
- pagos;
- acuerdos;
- canales;
- empresas;
- proyectos;
- usuarios;
- roles/permisos;
- auditoria;
- terceros;
- tareas;
- configuracion;
- alertas;
- juridico;
- ventas;
- tipificaciones;
- grabaciones;
- cargas;
- demograficos;
- integraciones;
- Mi Excel Web;
- vistas guardadas;
- hoja de seguimiento.

## 3. Helper usado

Se modifico:

```javascript
table(headers, rows, emptyMessage, options = {})
```

Comportamiento:

- convierte filas HTML en una lista interna;
- calcula pagina actual por clave estable;
- muestra maximo 20 filas;
- agrega controles Anterior/Siguiente cuando aplica;
- conserva empty states existentes.

Opciones principales:

- `key`: clave estable de paginacion;
- `pageSize`: tamano de pagina, con maximo efectivo de 20;
- `forcePager`: fuerza mostrar paginador.

## 4. Navegacion

Cada tabla renderiza:

- boton Anterior;
- boton Siguiente;
- indicador `Pagina X de Y`;
- total de registros.

El estado de pagina se guarda en `state.ui.tablePages`.

## 5. Proteccion backend en Mi Excel Web

Ademas del frontend, `ExcelWebQuery.page_size` se limito a 20. Esto evita que una llamada manual pida 50 o 100 registros por pagina en el modulo Excel Web.

## 6. Riesgos pendientes

- Algunos endpoints backend todavia aceptan `page_size` mayor en otros modulos; visualmente se limita por frontend, pero el hardening backend global debe revisarse en una fase futura.
- Tablas con paginacion propia de backend, como cola/clientes, conservan su paginacion existente y ademas quedan protegidas por el render comun.
- Si dos tablas comparten exactamente los mismos headers y empty message, podrian compartir estado de pagina. Las tablas criticas de Excel Web usan claves explicitas.
