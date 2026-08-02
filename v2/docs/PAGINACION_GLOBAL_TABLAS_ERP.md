# Paginacion Global de Tablas ERP

## 1. Regla maxima

Toda tabla renderizada por el helper frontend `table()` muestra maximo 10 registros por pagina.

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
- muestra maximo 10 filas;
- agrega controles Anterior/Siguiente cuando aplica;
- conserva empty states existentes.

Opciones principales:

- `key`: clave estable de paginacion;
- `pageSize`: tamano de pagina, con maximo efectivo de 10;
- `forcePager`: fuerza mostrar paginador.

## 4. Navegacion

Cada tabla renderiza:

- boton Anterior;
- boton Siguiente;
- indicador `Pagina X de Y`;
- total de registros.

El estado de pagina se guarda en `state.ui.tablePages`.

## 5. Proteccion backend en listados visibles

Ademas del frontend, los endpoints de listados visibles se limitaron a 10 registros por consulta cuando exponen `limit` o `page_size`. Esto evita que una llamada manual pida 20, 50 o 100 registros por pagina en modulos como Mi Excel Web, cargas, equipos, auditoria, telefonia, grabaciones, promesas, pagos, acuerdos y obligaciones.

## 6. Riesgos pendientes

- Algunos agregados ejecutivos pueden consultar ventanas internas mayores para calcular metricas, pero no deben renderizar tablas visibles sin pasar por paginacion.
- Tablas con paginacion propia de backend, como cola/clientes, conservan su paginacion existente y ademas quedan protegidas por el render comun.
- Si dos tablas comparten exactamente los mismos headers y empty message, podrian compartir estado de pagina. Las tablas criticas de Excel Web usan claves explicitas.
