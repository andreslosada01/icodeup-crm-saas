# Resultados QA Local Piloto Icodeup Advisors

Fecha: 2026-06-11
Rama: `feature/deploy-test-server`
Commit probado: `0d973dd chore: add local Icodeup Advisors pilot seed`
Base usada: `icodeup_crm_local`
URL local: `http://127.0.0.1:8020`

## 1. Activacion temporal del seed

Se activo temporalmente en `v2/.env` local:

```env
ENABLE_DEMO_DATA=true
ENABLE_DEMO_SEEDS=true
ENABLE_PILOT_ICODEUP_SEED=true
```

La activacion fue solo local y no versionada. Despues de validar, `ENABLE_PILOT_ICODEUP_SEED` se dejo nuevamente en `false` en `v2/.env` local para evitar tiempos de arranque innecesarios.

`v2/backend/.env.local.windows.example` permanece con:

```env
ENABLE_PILOT_ICODEUP_SEED=false
```

## 2. Health

`GET http://127.0.0.1:8020/api/health`

Resultado:

```json
{"ok":true,"app":"Icodeup 360","environment":"local","port":8020,"database":{"ok":true,"detail":"PostgreSQL conectado."}}
```

## 3. Inventario encontrado

Tenant validado: `Icodeup Advisors`

| Entidad | Conteo |
|---|---:|
| Usuarios | 11 |
| Proyectos | 3 |
| Clientes | 300 |
| Obligaciones | 500 |
| Gestiones base seed | 300 |
| Gestiones despues de QA API | 301 |
| Promesas | 50 |
| Pagos | 30 |
| Acuerdos | 20 |
| Demograficos | 100 |
| Lotes de carga metadata | 3 |

La gestion adicional corresponde a la validacion real de creacion de gestion con usuario gestor.

## 4. Relaciones validadas

| Validacion | Resultado |
|---|---|
| Clientes distribuidos entre gestores | OK, 5 gestores distintos |
| Obligaciones con gestor asignado | OK, 0 sin gestor |
| Obligaciones con lider asignado | OK, 0 sin lider |
| Lider con equipo/carteras | OK, 3 asignaciones de proyecto |
| Seed idempotente | OK, segunda ejecucion no duplico conteos base |

## 5. Usuarios probados

Todos con contrasena demo local `Demo360!2026`:

| Usuario | Resultado |
|---|---|
| `admin.icodeup@demo.icodeup.local` | Login OK |
| `lider.cobranzas.icodeup@demo.icodeup.local` | Login OK |
| `gestor1.icodeup@demo.icodeup.local` | Login OK |

## 6. API por rol

### Admin tenant

| Endpoint | Resultado |
|---|---|
| `/api/dashboard/me` | 200 |
| `/api/governance/users` | 200 |
| `/api/governance/roles` | 200 |
| `/api/governance/modules` | 200 |
| `/api/governance/audit-logs` | 200 |
| `/api/teams/projects` | 200 |
| `/api/crm/customers` | 200 |
| `/api/crm/obligations` | 200 |
| `/api/uploads/batches` | 200 |
| `/api/excel-web/query` | 200 |

Observacion: `/api/admin/users` respondio 403 para admin tenant porque esa ruta legacy esta restringida a plataforma. La administracion SaaS visual de usuarios para tenant se valida correctamente por `/api/governance/users`.

### Lider de cobranzas

| Endpoint | Resultado |
|---|---|
| `/api/teams/dashboard` | 200 |
| `/api/crm/customers` | 200 |
| `/api/crm/obligations` | 200 |
| `/api/crm/promises` | 200 |
| `/api/excel-web/query` | 200 |

### Gestor

| Endpoint | Resultado |
|---|---|
| `/api/crm/customers` | 200 |
| `/api/crm/obligations` | 200 |
| `/api/crm/promises` | 200 |
| `/api/crm/agreements` | 200 |
| `/api/excel-web/query` | 200 |
| Crear gestion en cliente asignado | OK, gestion creada |
| `/api/admin/users` | 403 esperado |

## 7. Pruebas ejecutadas

| Prueba | Resultado |
|---|---|
| `python -m compileall .\v2\backend\app .\v2\backend\tests` | OK |
| `node --check .\v2\frontend\static\assets\app.js` | OK |
| `alembic upgrade head` | OK |
| `alembic current` | `20260604_0005 (head)` |
| `pytest` modo seguro | OK, 85 skipped esperado |
| `pytest .\tests\test_pilot_icodeup_advisors_seed.py` con integracion activa | OK, 5 passed |

## 8. Errores encontrados

No se encontraron errores bloqueantes.

Observaciones:

- La primera prueba manual de PowerShell tuvo un conflicto de nombre con `H`, alias de historial de PowerShell. Se repitio usando `AuthHeaders` y no requirio cambios de codigo.
- `/api/admin/users` responde 403 para admin tenant por diseno legacy; se valido la ruta funcional correcta `/api/governance/users`.

## 9. Seguridad de archivos

No se versiono:

- `v2/.env`
- `v2/scripts/run_local_windows.ps1`
- dumps
- backups
- logs
- runtime
- archivos reales
- secretos

## 10. Decision

Resultado: **listo para QA visual del usuario con observaciones menores no bloqueantes**.

Siguiente paso recomendado:

1. Abrir `http://127.0.0.1:8020`.
2. Ingresar con `admin.icodeup@demo.icodeup.local`.
3. Validar visualmente dashboard, menu, usuarios, roles, carteras, clientes, Excel Web, cargas y reportes.
4. Repetir con `lider.cobranzas.icodeup@demo.icodeup.local` y `gestor1.icodeup@demo.icodeup.local`.
