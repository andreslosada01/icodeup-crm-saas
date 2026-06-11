# Validacion Ambiente Local PostgreSQL Icodeup

Fecha: 2026-06-11  
Rama: `feature/deploy-test-server`  
Base local objetivo: `icodeup_crm_local`  
Usuario PostgreSQL objetivo: `icodeup_local_user`  
App local: `http://127.0.0.1:8020/`

## 1. Objetivo

Validar que Icodeup 360 puede funcionar localmente en Windows contra PostgreSQL instalado en la maquina, usando base local temporal para QA funcional y piloto interno.

Este ambiente no es produccion y no debe exponerse publicamente.

## 2. Arquitectura validada

- Modelo SaaS: shared database / shared schema.
- Aislamiento: `tenant_id`, permisos, modulos y roles.
- No se implementa database-per-tenant.
- No se implementa PostgreSQL RLS en esta fase.

## 3. Configuracion esperada

Archivo activo:

```text
v2/.env
```

Ejemplo seguro:

```text
v2/backend/.env.local.windows.example
```

Valores esperados:

```env
APP_ENV=local
DATABASE_URL=postgresql+psycopg://icodeup_local_user:<password>@127.0.0.1:5432/icodeup_crm_local
TENANT_MODE=shared_schema
ENABLE_DEMO_DATA=true
ENABLE_DEMO_SEEDS=true
ENABLE_PILOT_ICODEUP_SEED=true
```

## 4. Comandos de validacion

```powershell
cd .\v2\backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m compileall app tests
.\.venv\Scripts\python.exe -m pytest
```

Health:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8020/api/health
```

## 5. Estado de migraciones

Estado esperado:

```text
20260604_0005 (head)
```

## 6. Usuarios demo disponibles

Demo Andina:

- `superadmin@demo.icodeup.local`
- `admin.andina@demo.icodeup.local`
- `coord.cobranzas.andina@demo.icodeup.local`
- `gestor1.andina@demo.icodeup.local`
- `gestor2.andina@demo.icodeup.local`
- `calidad.andina@demo.icodeup.local`
- `abogado.andina@demo.icodeup.local`
- `comercial.andina@demo.icodeup.local`

Piloto Icodeup Advisors, solo si `ENABLE_PILOT_ICODEUP_SEED=true`:

- `admin.icodeup@demo.icodeup.local`
- `lider.cobranzas.icodeup@demo.icodeup.local`
- `gestor1.icodeup@demo.icodeup.local`
- `gestor2.icodeup@demo.icodeup.local`
- `gestor3.icodeup@demo.icodeup.local`
- `gestor4.icodeup@demo.icodeup.local`
- `gestor5.icodeup@demo.icodeup.local`
- `calidad.icodeup@demo.icodeup.local`
- `auditor.icodeup@demo.icodeup.local`
- `abogado.icodeup@demo.icodeup.local`
- `comercial.icodeup@demo.icodeup.local`

## 7. Riesgos encontrados

| Riesgo | Estado | Mitigacion |
|---|---|---|
| `.env` real con secretos | No versionar | `.gitignore` mantiene `v2/.env` ignorado |
| Seed piloto activado por accidente | Controlado | Requiere `ENABLE_PILOT_ICODEUP_SEED=true` |
| Datos reales en local | No permitido | Usar solo datos sinteticos `@demo.icodeup.local` |
| Backups locales versionados | No permitido | `*.dump`, logs y runtime no se suben |
| Pruebas de integracion sin credenciales | Esperado | `pytest` modo seguro omite integracion |

## 8. Resultado validado el 2026-06-11

Comandos ejecutados en rama `feature/deploy-test-server`:

| Validacion | Resultado |
|---|---|
| `python -m compileall .\v2\backend\app .\v2\backend\tests` | OK |
| `node --check .\v2\frontend\static\assets\app.js` | OK usando Node embebido de Codex |
| `alembic current` | `20260604_0005 (head)` |
| `pytest` modo seguro | OK, 85 pruebas omitidas por no activar integracion |
| Seed piloto con `ENABLE_PILOT_ICODEUP_SEED=true` | OK |
| Segunda ejecucion del seed piloto | OK, sin duplicacion de conteos |
| `GET /api/health` | OK, PostgreSQL conectado |
| `pytest tests\test_pilot_icodeup_advisors_seed.py` con credenciales demo locales | OK, 5 passed |

Inventario confirmado para tenant `icodeup-advisors`:

| Entidad | Conteo |
|---|---:|
| Usuarios | 11 |
| Proyectos | 3 |
| Clientes | 300 |
| Obligaciones | 500 |
| Gestiones | 300 |
| Promesas | 50 |
| Pagos | 30 |
| Acuerdos | 20 |
| Demograficos | 100 |
| Lotes de carga | 3 |

No se editaron ni versionaron secretos. La ejecucion del seed se hizo con variable de entorno temporal en el proceso.

## 9. Decision

Ambiente local PostgreSQL: **listo para QA funcional con observaciones**.

Observaciones:

- El seed piloto queda apagado por defecto.
- Para validar el piloto completo se debe activar `ENABLE_PILOT_ICODEUP_SEED=true`, reiniciar la app y ejecutar los tests de integracion con credenciales demo locales.
- Este ambiente no reemplaza servidor test ni produccion.
