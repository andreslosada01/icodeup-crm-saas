# Guia - Mi Excel Web

## Objetivo

Permitir consultas operativas seguras sin SQL libre y sin depender de Excel local.

## Fuentes

Clientes, gestiones, promesas, pagos, acuerdos, demograficos, grabaciones, juridico, ventas, documentos y cargas.

## Funciones

- filtros basicos
- columnas visibles
- paginacion
- vistas guardadas
- exportes auditados

## Permisos

- `excel_web.view`
- `excel_web.query`
- `excel_web.export`
- `excel_web.views.manage`

## Seguridad

Cada consulta filtra por tenant salvo superadmin. No se permite SQL libre ni fuga cross-tenant.
