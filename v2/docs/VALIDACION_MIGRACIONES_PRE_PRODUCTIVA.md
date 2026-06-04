# Validacion de migraciones pre-productiva

## Migraciones Alembic existentes

| Revision | Proposito | Estado |
| --- | --- | --- |
| 20260528_0001 | Baseline inicial V2 product hardening | Vigente |
| 20260603_0002 | Operacion CRM/cobranzas fase 8B | Vigente |
| 20260603_0003 | Filas operativas Excel Web | Vigente |
| 20260603_0004 | Enlaces de obligaciones Sprint 1 | Vigente |
| 20260604_0005 | Equipos, carteras y asignaciones Sprint 3 | Head esperado |

## Validaciones requeridas

- Ejecutar `alembic upgrade head` desde `v2/backend`.
- Ejecutar `alembic current` y confirmar `20260604_0005 (head)`.
- Ejecutar `python -m compileall app`.
- Confirmar que `app.models` importa modelos de core, seguridad, CRM, cobranza, juridico, documentos, ventas, auditoria, Excel Web, equipos, uploads, alertas e integraciones.
- Mantener `apply_compatibility_migrations` como capa temporal hasta completar pruebas desde base limpia.

## Riesgos detectados

- Si una tabla fue creada por compatibility migrations y no por Alembic, una instalacion limpia podria fallar. En esta revision no se agregaron tablas nuevas.
- No deben renombrarse columnas ni eliminarse campos legacy hasta crear migraciones de transicion.
- Produccion debe aplicar Alembic antes de iniciar la app.

## Recomendaciones

1. Crear una base limpia de test y ejecutar `alembic upgrade head`.
2. Iniciar la app con `ENABLE_DEMO_DATA=false` y confirmar arranque sin seeds demo.
3. Ejecutar healthcheck y pruebas de login.
4. Crear backup antes de cada nueva migracion.
5. Para nuevas fases, generar una revision Alembic por cambio de modelo y documentar impacto.

## Resultado Sprint 5

No se agregaron migraciones destructivas. Los cambios de Sprint 5 fueron de estabilizacion, pruebas, docs, scripts y limites de consulta.
