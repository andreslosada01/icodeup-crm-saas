# Revision Pre-Merge Fase 6

## 1. Resumen ejecutivo

La Fase 6 fue revisada sobre la rama `feature/phase-6-roles-legal-sales-hardening`. El objetivo de hardening de roles especializados para juridico y ventas se cumple sin romper compatibilidad legacy.

La rama queda lista para abrir PR hacia `main` con observaciones menores no bloqueantes. No se hizo merge.

## 2. Estado de rama

- Rama activa: `feature/phase-6-roles-legal-sales-hardening`.
- Rama destino: `main`.
- Ultimo commit revisado: `10a6c8b feat: harden specialized legal and sales roles`.
- Estado local antes de crear este documento: limpio.
- Comparacion `main...feature/phase-6-roles-legal-sales-hardening`: `0 1`.
- Comparacion `origin/main...feature/phase-6-roles-legal-sales-hardening`: `0 1`.
- La rama remota existe en `origin` con SHA `10a6c8b`.

## 3. Validaciones ejecutadas

| Validacion | Resultado |
|---|---|
| `git status --short --branch` | OK, rama correcta y limpia antes del documento |
| `git fetch origin` | OK |
| `git log --oneline -8` | OK |
| `git rev-list --left-right --count main...feature/phase-6-roles-legal-sales-hardening` | OK, `0 1` |
| `python -m compileall .\v2\backend\app` usando venv | OK |
| `node --check .\v2\frontend\static\assets\app.js` | OK |
| `alembic current` | OK, `20260528_0001 (head)` |
| `pytest` modo seguro | OK, 28 pruebas saltadas por configuracion de integracion |
| `GET http://127.0.0.1:8020/api/health` | OK |
| Smoke test con `TestClient` | OK |
| Modulo sales/legal desactivado y restaurado | OK |

## 4. Resultado de pruebas

`pytest` se ejecuto en modo seguro. Las pruebas quedaron saltadas porque no se habilito `ICODEUP_RUN_INTEGRATION_TESTS=1`, comportamiento esperado para no tocar una base productiva o no controlada.

Adicionalmente se ejecuto smoke test con `TestClient` contra el codigo actual de la rama, validando login, menu, dashboard y endpoints para:

- SuperAdmin Icodeup.
- Admin Empresa Andina.
- Gestor de cobranzas.
- Abogado.
- Asesor comercial.

## 5. Validacion de roles especializados

Se confirmo en base/servicio que existen roles por tenant para Andina:

- `lawyer`
- `legal_director`
- `sales_advisor`
- `sales_leader`
- `collections_agent`
- `collections_leader`
- `tenant_auditor`

El bootstrap se ejecuto dos veces en proceso de validacion y no duplico roles tenant. Los permisos esperados existen para `lawyer`, `sales_advisor` y `collections_agent`.

## 6. Validacion UserProfile.role_id vs User.role

Se confirmo que:

- `UserProfile.role_id` tiene prioridad cuando el perfil tiene rol activo.
- `User.role` queda como fallback legacy.
- `platform_admin` conserva acceso total.
- `tenant_admin` conserva administracion tenant.
- `agent` sin perfil comercial ya no gana acceso a ventas por fallback.
- Abogado y comercial demo ya no usan `coordinator` como rol legacy.

## 7. Validacion abogado

Usuario: `abogado.andina@demo.icodeup.local`.

Resultado:

- Login OK.
- `profile_role = lawyer`.
- Menu contiene Inicio, Clientes, Juridico y Documentos.
- No ve Gobierno SaaS.
- No ve Ventas.
- No ve cobranzas completa.
- `/api/legal/cases` OK.
- `/api/legal/deadlines` OK.
- `/api/documents` OK.
- `/api/sales/leads` devuelve 403.
- `/api/crm/customers/export` devuelve 403.
- `/api/crm/payments/export` devuelve 403.
- Dashboard: `Panel juridico operativo`.

## 8. Validacion comercial

Usuario: `comercial.andina@demo.icodeup.local`.

Resultado:

- Login OK.
- `profile_role = sales_advisor`.
- Menu contiene Inicio, Clientes y Ventas.
- No ve Gobierno SaaS.
- No ve Juridico.
- No ve Documentos.
- `/api/sales/leads` OK.
- `/api/sales/opportunities` OK.
- `/api/legal/cases` devuelve 403.
- `/api/documents` devuelve 403.
- `/api/crm/customers/export` devuelve 403.
- `/api/crm/payments/export` devuelve 403.
- Dashboard: `Panel comercial operativo`.

## 9. Validacion gestor

Usuario: `gestor1.andina@demo.icodeup.local`.

Resultado:

- Login OK.
- `profile_role = collections_agent`.
- Menu contiene Inicio, Cola, Clientes, Promesas, Pagos y Acuerdos.
- No ve Gobierno SaaS.
- No ve Juridico.
- No ve Ventas.
- `/api/crm/customers` OK.
- `/api/legal/cases` devuelve 403.
- `/api/sales/leads` devuelve 403.
- `/api/crm/customers/export` devuelve 403.

## 10. Validacion admin empresa

Usuario: `admin.andina@demo.icodeup.local`.

Resultado:

- Login OK.
- Ve menu de administracion tenant.
- Ve Mi Empresa, usuarios, roles/permisos, modulos contratados y settings.
- `/api/governance/roles` OK.
- `/api/governance/settings` OK.
- `/api/legal/cases` OK.
- `/api/sales/leads` OK.
- No ve Gobierno SaaS global en menu.

## 11. Validacion superadmin

Usuario: `superadmin@demo.icodeup.local`.

Resultado:

- Login OK.
- Ve Gobierno SaaS.
- Ve tenants, planes, suscripciones, modulos, auditoria y salud.
- `/api/governance/subscriptions` OK.
- `/api/governance/modules` OK.
- Mantiene acceso platform.

## 12. Validacion endpoints sensibles

Endpoints revisados:

- `/api/menu/me`
- `/api/dashboard/me`
- `/api/legal/cases`
- `/api/legal/deadlines`
- `/api/sales/leads`
- `/api/sales/opportunities`
- `/api/documents`
- `/api/crm/customers`
- `/api/crm/payments/export`
- `/api/crm/customers/export`
- `/api/governance/roles`
- `/api/governance/modules`

Resultado:

- 200 cuando corresponde.
- 403 cuando corresponde.
- Exportes bloqueados para Abogado, Comercial y Gestor.
- Gobierno bloqueado para perfiles operativos.
- Sales y Legal bloquean por modulo desactivado y se restauran correctamente.

## 13. Validacion multi-tenant

Se reviso que los endpoints sensibles mantienen validacion por tenant y permisos. La prueba de modulos se hizo contra el tenant Andina y se restauro el estado original.

No se detecto fuga cross-tenant en los flujos validados. Se recomienda ejecutar pruebas de integracion completas con `ICODEUP_RUN_INTEGRATION_TESTS=1` antes del merge final si existe una base de prueba aislada.

## 14. Validacion frontend

Validaciones realizadas:

- `node --check` OK.
- `app.js` contiene etiquetas `Abogado` y `Asesor comercial`.
- `roleLabel()` prioriza `profile_role`.
- El dashboard usa titulos especializados para juridico y ventas.
- El menu se valida por API para no mostrar secciones indebidas.

Observacion: no se pudo ejecutar QA visual con Browser porque el skill local de Browser no estaba disponible en la ruta indicada por el entorno. Adicionalmente, el servicio local en `8020` seguia asociado a un proceso Python antiguo y Windows habia negado detenerlo en la fase anterior. La validacion funcional se realizo con `TestClient` contra el codigo actual de la rama.

## 15. Riesgos criticos

No se encontraron riesgos criticos bloqueantes.

## 16. Riesgos medios

- Validacion visual completa pendiente tras reiniciar servicio local con la venv del proyecto.
- `User.role` sigue como fallback legacy y debe seguirse reduciendo gradualmente.
- Pruebas pytest de integracion quedan preparadas, pero no ejecutadas por configuracion segura.

## 17. Riesgos bajos

- La UI de administracion puede mejorar para explicar rol legacy vs rol especializado.
- El frontend sigue siendo monolitico HTML/CSS/JS; no es bloqueante para esta fase.

## 18. Correcciones aplicadas

Durante esta revision pre-merge no se aplicaron correcciones funcionales adicionales. Se creo este documento de revision.

## 19. Decision final

Listo con observaciones.

La rama esta lista para abrir PR hacia `main`. La observacion no bloqueante es ejecutar QA visual/manual despues de reiniciar el servicio local con el codigo actual.

## 20. Recomendacion para merge a main

Abrir PR desde `feature/phase-6-roles-legal-sales-hardening` hacia `main`, revisar este documento, ejecutar smoke visual local tras reinicio del servicio y proceder con merge si no aparecen hallazgos visuales.

## 21. Recomendacion para siguiente fase

La siguiente fase recomendada es preparar el paquete comercial/operativo:

- QA visual con navegador por perfil.
- Guia de pre-merge automatizada.
- Pulido UI de roles especializados en administracion.
- Preparacion de PR Fase 6.
