# Sprint 2 - Mi Excel Web Operativo Tipo App Pagos

## Objetivo

Fortalecer Mi Excel Web para que funcione como una hoja operativa dentro de Icodeup 360, similar a una experiencia tipo App Pagos, pero integrada al SaaS, con permisos, tenant, auditoria y persistencia real.

## Componentes Implementados

### Filtros Superiores

- Buscar por cliente, documento, obligacion, nota o estado.
- Filtro por proyecto/cartera.
- Filtro por estado.
- Filtro por usuario cuando el rol lo permite.
- Rango de fechas.

### KPIs y Resumen

- Registros de consulta.
- Valor visible de pagina.
- Seguimientos guardados.
- Gestionados.
- Tarjetas por estado:
  - Pendiente
  - Seguimiento
  - Gestionado
  - Pagos
  - Cerrado

### Tabla Operativa

Columnas principales:

- ID
- Usuario
- Fecha
- Cartera
- Cliente
- Documento
- Obligacion
- Gestion
- Compromiso
- Valor
- Estado
- Proxima accion
- Acciones

### Operacion de Filas

- Agregar fila.
- Editar fila inline.
- Guardar cambios en base de datos.
- Cancelar edicion.
- Paginacion maxima de 20 filas.

### Export CSV

El endpoint `POST /api/excel-web/export` descarga CSV real y aplica:

- permiso `excel_web.export`,
- fuente autorizada,
- filtros seguros,
- alcance por tenant/rol,
- limite maximo de 5000 filas por export,
- auditoria de export.

## Permisos

Permisos relevantes:

- `excel_web.view`: ver modulo.
- `excel_web.query`: consultar fuentes y hoja.
- `excel_web.sheet.manage`: crear y editar filas de hoja operativa.
- `excel_web.views.manage`: administrar vistas guardadas y compatibilidad legacy.
- `excel_web.export`: exportar CSV.

## Alcance por Rol

- Gestor: consulta y administra filas dentro de su operacion asignada.
- Lider: consulta y opera informacion de su equipo/proyectos.
- Admin empresa: consulta tenant completo y exporta si tiene permiso.
- Superadmin: consulta global autorizada.

## Data Demo

El bootstrap ya crea filas demo de hoja operativa para Andina Servicios Financieros. El sprint conserva la idempotencia y no crea nuevas migraciones destructivas.

## Validaciones Recomendadas

1. Login gestor demo.
2. Abrir Mi Excel Web.
3. Filtrar hoja por estado `Seguimiento`.
4. Agregar fila manual.
5. Editar fila y guardar.
6. Validar paginacion maximo 20.
7. Login admin empresa.
8. Exportar CSV.
9. Confirmar que gestor no exporta.
10. Confirmar que no hay datos de otros tenants.

## Riesgos Pendientes

- La UI sigue siendo frontend HTML/CSS/JS monolitico.
- La tabla usa scroll horizontal controlado por cantidad de columnas.
- En una fase futura conviene agregar seleccion masiva, edicion por celda y guardado por lote.

## Decision

Sprint 2 queda listo para QA funcional y revision pre-merge dentro de la rama activa.
