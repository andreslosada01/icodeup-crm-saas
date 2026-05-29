# Revision Fase 5 Demo Comercial

## 1. Resumen de cambios

La Fase 5 agrego una capa de data demo comercial, idempotente y controlada por configuracion, para que Icodeup 360 pueda presentarse con una historia end-to-end creible sin usar datos reales.

## 2. Datos demo creados

- 3 tenants demo: Andina Servicios Financieros, Legal Recovery Group Demo y Cooperativa Horizonte Demo.
- 4 proyectos para Andina.
- 60 clientes/deudores ficticios para Andina.
- 90 gestiones.
- 32 promesas.
- 15 pagos.
- 10 acuerdos con cuotas.
- 10 casos juridicos con actuaciones, audiencias y vencimientos.
- 38 metadatos documentales.
- 6 leads y 6 oportunidades.
- Suscripciones demo por plan.
- Modulos activados por tenant.

## 3. Usuarios demo creados

- `superadmin@demo.icodeup.local`
- `admin.andina@demo.icodeup.local`
- `coord.cobranzas.andina@demo.icodeup.local`
- `gestor1.andina@demo.icodeup.local`
- `gestor2.andina@demo.icodeup.local`
- `calidad.andina@demo.icodeup.local`
- `abogado.andina@demo.icodeup.local`
- `comercial.andina@demo.icodeup.local`

Contrasena demo: `Demo360!2026`.

## 4. Tenants demo creados

- `andina-servicios-financieros`
- `legal-recovery-group-demo`
- `cooperativa-horizonte-demo`

## 5. Flujos validados

- Gobierno SaaS.
- Admin Empresa.
- Gestor operativo.
- Juridico.
- Documentos.
- Ventas.
- Ejecutivo BI.

## 6. Dashboards revisados

La data demo alimenta clientes, cartera, promesas, pagos, acuerdos, juridico, documentos, ventas y BI. Las vistas que todavia son placeholders conservan copy comercial y no bloquean el recorrido.

## 7. Riesgos pendientes

- La demo depende de activar `ENABLE_DEMO_DATA` o `ENABLE_DEMO_SEEDS`.
- Los documentos son metadatos ficticios, no archivos reales.
- Juridico, documentos y ventas siguen siendo base/MVP visual-operativo.
- Para produccion se debe garantizar que las banderas demo esten desactivadas.

## 8. Validaciones ejecutadas

- `python -m compileall .\v2\backend\app`: OK.
- `node --check .\v2\frontend\static\assets\app.js`: OK.
- `alembic current`: OK, revision `20260528_0001 (head)`.
- `pytest`: OK en modo seguro; 23 pruebas omitidas por requerir `ICODEUP_RUN_INTEGRATION_TESTS=1` y base segura.
- `GET /api/health`: OK en `http://127.0.0.1:8020/api/health`.
- Smoke HTTP local:
  - `superadmin@demo.icodeup.local`: login, menu, dashboard, clientes, promesas, pagos, acuerdos, documentos, ventas OK.
  - `admin.andina@demo.icodeup.local`: login, menu, dashboard, clientes, promesas, pagos, acuerdos, documentos, ventas, juridico y BI OK.
  - `gestor1.andina@demo.icodeup.local`: login, menu, dashboard, clientes, promesas, pagos, acuerdos, documentos, ventas OK.
  - `abogado.andina@demo.icodeup.local`: juridico OK.
  - `comercial.andina@demo.icodeup.local`: ventas OK.

## 9. Evidencia de no usar datos reales

- Usuarios con dominio `@demo.icodeup.local`.
- Clientes con correos `@demo.local`.
- Documentos numericos secuenciales tipo `900100001`.
- Telefonos ficticios tipo `3000000001`.
- Storage paths ficticios bajo `tenants/demo/...`.
- Notas visibles indicando que la informacion es ficticia.

## 10. Recomendacion

La demo queda lista para revision comercial interna. Antes de una presentacion con cliente se recomienda activar explicitamente `ENABLE_DEMO_DATA=true` en el ambiente demo, confirmar que no exista data real mezclada y preparar un recorrido guiado con los usuarios demo definidos.
