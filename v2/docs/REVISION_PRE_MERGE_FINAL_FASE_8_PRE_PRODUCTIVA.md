# Revision pre-merge final fase 8 pre-productiva

## 1. Resumen ejecutivo

La rama `feature/phase-8-legal-sales-functional` queda revisada para integracion controlada hacia `main`. La rama contiene el cierre funcional de Fase 8, los sprints operativos posteriores y el Sprint 5 de estabilizacion pre-productiva. La validacion confirma que el producto compila, el frontend no tiene errores de sintaxis, Alembic esta en head, la app local responde healthcheck con PostgreSQL conectado y la suite integrada demo pasa completa.

Durante esta revision se encontro una regresion menor critica en el flujo de gestor: al limitar promesas a 20, una promesa recien creada desde una gestion podia quedar fuera del listado si el orden era por fecha de vencimiento. Se corrigio el orden del listado de promesas a `created_at desc` para garantizar visibilidad inmediata de acciones recientes sin cambiar rutas ni contratos.

Decision: listo para merge a `main` con observaciones no bloqueantes.

## 2. Rama origen

`feature/phase-8-legal-sales-functional`

## 3. Rama destino

`main`

## 4. Commits incluidos

Estado contra remoto despues de `git fetch origin`:

- Behind/Ahead contra `origin/main`: `0 / 14`
- `main` no tiene commits pendientes que falten en la rama.

Commits pendientes de integrar:

| Commit | Mensaje |
| --- | --- |
| 8322278 | chore: stabilize pre-production readiness sprint |
| f2a8260 | feat: add upload and portfolio import flow |
| 9e20cc5 | feat: add teams portfolios and assignments sprint |
| 2daa6cf | feat: make excel web grid editable |
| 7bdba29 | feat: improve operational excel web |
| 4ecf551 | feat: close collector operational workflow |
| 24f40f5 | feat: make excel web an operational worksheet |
| 8ef85a2 | fix: scope excel web by operational role |
| 5e5fd27 | fix: finalize collection CRM demo operations |
| cb6b721 | fix: restore management activity save and compact sidebar |
| e3f6da0 | feat: make phase 8c operations functional |
| 1911d62 | docs: add phase 8b pre-merge review |
| 48aefa2 | feat: strengthen collection CRM operations phase 8b |
| bd96ecd | feat: add phase 8 configuration alerts legal sales UX |

Nota: este documento y la correccion menor de ordenamiento de promesas se consolidan como commit final de cierre pre-merge.

## 5. Validaciones ejecutadas

| Validacion | Resultado |
| --- | --- |
| `git status --short` inicial | Limpio antes de la revision |
| `git fetch origin` | OK |
| `git rev-list --left-right --count origin/main...HEAD` | `0 14` |
| `python -m compileall .\v2\backend\app .\v2\backend\tests` | OK |
| `node --check .\v2\frontend\static\assets\app.js` | OK |
| `alembic upgrade head` | OK |
| `alembic current` | `20260604_0005 (head)` |
| `pytest` modo seguro | OK, 75 skipped esperados |
| `pytest` integracion demo | OK, 75 passed |
| `GET http://127.0.0.1:8020/api/health` | OK |
| Revision de secretos versionados | OK, sin `.env`, logs, dumps, DB o runtime versionados |

## 6. Estado de migraciones

Alembic esta en `20260604_0005 (head)`.

Migraciones incluidas en la rama:

- `20260528_0001_initial_schema_v2_product_hardening`
- `20260603_0002_phase8b_collection_crm_operations`
- `20260603_0003_operational_sheet_rows`
- `20260603_0004_sprint1_obligation_links`
- `20260604_0005_sprint3_team_project_assignments`

No se hicieron migraciones destructivas en esta revision. La capa `apply_compatibility_migrations` se mantiene como compatibilidad temporal.

## 7. Estado de pruebas

Modo seguro:

- 75 tests recolectados.
- 75 skipped esperados por no habilitar variables de integracion.
- Resultado: OK.

Modo integracion demo:

- Variables usadas:
  - `ICODEUP_RUN_INTEGRATION_TESTS=1`
  - passwords demo controlados para platform, tenant, leader, lawyer y sales.
- Resultado final: 75 passed.

La primera corrida integrada detecto el caso de promesa recien creada no visible por ordenamiento. Se corrigio y la suite completa paso despues de reiniciar el servicio local.

## 8. Estado funcional por rol

| Rol | Estado | Cobertura |
| --- | --- | --- |
| SuperAdmin Icodeup | OK | Login, menu gobierno, governance, salud, auditoria, restricciones de operacion ordinaria. |
| Admin Empresa | OK | Mi empresa, usuarios, roles, equipos, cargas, configuracion, auditoria tenant, datos por tenant. |
| Lider Cobranzas | OK | Dashboard equipo, proyectos, agentes, clientes, obligaciones, promesas, pagos, acuerdos. |
| Gestor | OK | Cola, clientes asignados, obligaciones, gestiones, promesas visibles, pagos/acuerdos segun permiso, export bloqueado. |
| Supervisor Calidad | OK base | Lectura/control segun permisos existentes; se recomienda QA visual manual adicional. |
| Abogado | OK | Legal/documentos/clientes lectura, sin governance, sin ventas, sin exportes indebidos. |
| Comercial | OK | Sales/leads/oportunidades/clientes lectura, sin governance, sin juridico, sin documentos. |

## 9. Riesgos pendientes

- QA visual manual final por rol despues de reiniciar el servicio en servidor test.
- Produccion debe iniciar con `ENABLE_DEMO_DATA=false` y `ENABLE_DEMO_SEEDS=false`.
- Se debe rotar cualquier password demo antes de clientes reales.
- Storage documental aun es metadata/base; archivos reales requieren politica externa de storage, antivirus y retencion.
- Integraciones WhatsApp, email y telefonia siguen siendo base/configuracion demo hasta conectar proveedores reales.
- Frontend sigue siendo HTML/CSS/JS monolitico; aceptable para primera salida controlada, pero conviene modularizar luego.

## 10. Observaciones no bloqueantes

- Existen archivos locales no versionados como `.env`, logs y runtime de navegador. No aparecen en `git ls-files` ni en cambios staged.
- La app local fue reiniciada para validar contra el codigo actualizado.
- El endpoint de promesas mantiene limite 20, pero ahora ordena por creacion descendente para priorizar actividad reciente.
- La demo y las pruebas usan datos ficticios; no se detecto versionado de archivos reales.

## 11. Recomendacion final para merge

Recomendacion: listo para PR/merge controlado hacia `main`.

Condiciones recomendadas antes de hacer push/merge:

1. Confirmar `git status` limpio despues del commit de este documento.
2. Revisar diff final del PR.
3. Hacer merge no fast-forward o PR aprobado, segun flujo GitHub elegido.
4. No desplegar directo a produccion; primero servidor test.

## 12. Recomendacion para despliegue en servidor test

1. Crear servidor test con PostgreSQL limpio.
2. Configurar variables de entorno sin secretos versionados.
3. Ejecutar `alembic upgrade head`.
4. Levantar servicio con systemd o script controlado.
5. Validar `/api/health`.
6. Ejecutar smoke test por rol:
   - `superadmin@demo.icodeup.local`
   - `admin.andina@demo.icodeup.local`
   - `coord.cobranzas.andina@demo.icodeup.local`
   - `gestor1.andina@demo.icodeup.local`
   - `abogado.andina@demo.icodeup.local`
   - `comercial.andina@demo.icodeup.local`
7. Validar cargas/repartos con CSV ficticio.
8. Probar backup y restore hacia una base test secundaria.
9. Solo despues de ese ciclo preparar release productivo.
