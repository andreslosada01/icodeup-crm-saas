# Sprint 6 - Diagnostico deploy test

## 1. Estado actual de scripts

| Archivo | Estado | Observacion |
| --- | --- | --- |
| `v2/scripts/deploy_test.sh.example` | Actualizado | Despliega desde rama configurable, crea venv, instala requirements, migra, compila, reinicia systemd y valida health. |
| `v2/scripts/deploy_prod.sh.example` | Existente | Sirve como referencia productiva; no se uso para test. |
| `v2/scripts/backup_postgres.sh.example` | Actualizado | Usa `pg_dump`, timestamp, gzip y variables PostgreSQL de entorno. |
| `v2/scripts/restore_backup_to_test.sh.example` | Actualizado | Exige confirmacion explicita y evita nombres de DB con prod/production. |
| `v2/scripts/server_test_setup_ubuntu.sh.example` | Nuevo | Prepara Ubuntu Server con dependencias, usuario y carpetas base. |
| `v2/deploy/systemd/icodeup360-test.service.example` | Nuevo | Servicio test con `uvicorn`, porque el proyecto no declara `gunicorn`. |
| `v2/deploy/nginx/icodeup360-test.nginx.example` | Nuevo | Proxy HTTP a `127.0.0.1:8020`, listo para Certbot. |

## 2. Variables requeridas

Variables reales leidas por `app.core.config.Settings`:

| Variable | Uso | Requerida |
| --- | --- | --- |
| `APP_NAME` | Nombre de aplicacion FastAPI/health | No |
| `APP_ENV` | Entorno mostrado en health | Recomendado |
| `APP_HOST` | Host configurativo | No |
| `APP_PORT` | Puerto mostrado en health | Recomendado |
| `FRONTEND_DIR` | Ruta frontend static | Requerida en servidor si no se usa default del repo |
| `SECRET_KEY` | JWT/sesiones | Si |
| `SESSION_COOKIE_NAME` | Nombre cookie | No |
| `SESSION_HOURS` | Duracion sesion | No |
| `DATABASE_URL` | Conexion PostgreSQL | Si |
| `TENANT_MODE` | Estrategia multi-tenant | No |
| `PLATFORM_TENANT_SLUG` | Tenant plataforma | No |
| `ENABLE_DEMO_SEEDS` | Seeds demo | Solo test/demo |
| `ENABLE_DEMO_DATA` | Data demo | Solo test/demo |
| `PLATFORM_ADMIN_EMAIL` | Superadmin inicial | Recomendado en test |
| `PLATFORM_ADMIN_PASSWORD` | Password inicial | Recomendado en test, debe rotarse |

Variables reservadas documentadas en `.env.example` pero no leidas actualmente:

- `DEBUG`
- `ALLOWED_ORIGINS`
- `LOG_LEVEL`
- `UPLOAD_STORAGE_MODE`
- `UPLOAD_STORAGE_PATH`
- `MAX_PAGE_SIZE`

Estas quedan como politica de despliegue/futuro hardening, no como comportamiento activo actual.

## 3. Dependencias backend

El proyecto usa `v2/backend/pyproject.toml`. Para facilitar servidores test tradicionales se creo `v2/backend/requirements.txt` con las mismas dependencias operativas y de prueba:

- FastAPI
- Uvicorn
- Pydantic Settings
- SQLAlchemy
- Alembic
- Psycopg
- Bcrypt
- python-jose
- Pytest
- HTTPX

No se agrego `gunicorn` porque no estaba declarado en dependencias actuales. El servicio systemd usa `uvicorn`.

## 4. Dependencias frontend

El frontend es HTML/CSS/JavaScript estatico servido por FastAPI desde `v2/frontend/static`.

No requiere build step ni Node en servidor. `node --check` se usa solo como validacion local/CI.

## 5. Requerimientos PostgreSQL

- PostgreSQL 15+ recomendado.
- Base test sugerida: `icodeup_crm_test`.
- Usuario sugerido: `icodeup_test_user`.
- Conexion por `DATABASE_URL` con driver `postgresql+psycopg`.
- Backups con `pg_dump` y restore con `pg_restore`.

## 6. Requerimientos Nginx

- Nginx como reverse proxy.
- Proxy a `http://127.0.0.1:8020`.
- `client_max_body_size 50M` para cargas CSV.
- Timeouts de 120 segundos para cargas y operaciones largas.
- HTTPS via Certbot despues de configurar DNS.

## 7. Requerimientos systemd

- Servicio `icodeup360-test`.
- Usuario Linux no root: `icodeup`.
- `WorkingDirectory=/opt/icodeup360-test/app/v2/backend`.
- `EnvironmentFile=/etc/icodeup360-test/.env`.
- Ejecutable: `/opt/icodeup360-test/app/.venv/bin/uvicorn`.

## 8. Riesgos de despliegue

- No copiar `.env.example` sin reemplazar `SECRET_KEY` y password DB.
- No activar usuarios reales con password demo.
- No ejecutar restore sobre una base productiva.
- La app todavia aplica `apply_compatibility_migrations` al iniciar; mantener backups antes de deploy.
- `ALLOWED_ORIGINS` y `DEBUG` estan documentadas pero no aplican controles activos actualmente.
- Storage documental real requiere politica adicional; hoy el modulo documental opera principalmente metadata.

## 9. Checklist para servidor test

- Servidor Ubuntu actualizado.
- Usuario `icodeup` creado.
- Directorios `/opt`, `/etc`, `/var/log`, `/var/lib/uploads`, `/var/backups` creados.
- PostgreSQL disponible.
- Repo clonado.
- `.env` real creado en `/etc/icodeup360-test/.env`.
- Venv creado.
- Requirements instalados.
- Alembic en head.
- systemd activo.
- Nginx proxy activo.
- Health OK.
- Login demo OK.
- QA por rol completado.
- Backup y restore probados.

## 10. Validaciones locales ejecutadas

| Validacion | Resultado |
| --- | --- |
| `python -m compileall .\v2\backend\app .\v2\backend\tests` | OK |
| `node --check .\v2\frontend\static\assets\app.js` | OK |
| `alembic upgrade head` | OK |
| `alembic current` | `20260604_0005 (head)` |
| `pytest` modo seguro | OK, 75 skipped esperados |
| `GET http://127.0.0.1:8020/api/health` | OK, PostgreSQL conectado |
| `git ls-files` contra `.env`, logs, DB, dumps y runtime | OK, sin archivos sensibles versionados |
| `bash -n` scripts `.example` | No ejecutado localmente; `bash` no disponible en esta maquina Windows |

## 11. Resultado del diagnostico

La rama `feature/deploy-test-server` queda preparada para crear un servidor Ubuntu test con instalacion parametrizable. La app no fue modificada a nivel funcional; los cambios son de configuracion ejemplo, scripts operativos y documentacion de despliegue/QA.
