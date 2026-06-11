# Validacion PostgreSQL Local Windows

## 1. Crear base local

Usar pgAdmin o `psql` con:

```powershell
psql -U postgres -h 127.0.0.1 -p 5432 -f .\v2\deploy\postgres\create_local_windows_database.sql.example
```

Antes de ejecutar, cambiar la contrasena placeholder `change-me` por una contrasena local segura.

## 2. Configurar `.env`

La aplicacion lee `v2/.env`.

```powershell
Copy-Item .\v2\backend\.env.local.windows.example .\v2\.env
notepad .\v2\.env
```

Validar:

- `DATABASE_URL=postgresql+psycopg://icodeup_local_user:<password>@127.0.0.1:5432/icodeup_crm_local`
- `TENANT_MODE=shared_schema`
- `ENABLE_DEMO_DATA=true`
- `ENABLE_DEMO_SEEDS=true`
- `APP_PORT=8020`

## 3. Ejecutar migraciones

```powershell
cd .\v2\backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

Resultado esperado:

- migraciones aplicadas sin errores
- `alembic current` en `head`

## 4. Validar sintaxis y pruebas

```powershell
cd ..\..
.\v2\backend\.venv\Scripts\python.exe -m compileall .\v2\backend\app .\v2\backend\tests
.\v2\backend\.venv\Scripts\python.exe -m pytest
```

El modo seguro de `pytest` puede omitir pruebas de integracion si no se definen credenciales `ICODEUP_TEST_*`.

## 5. Levantar app

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\scripts\run_local_windows.ps1.example
```

URL:

- `http://127.0.0.1:8020/`

Health:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8020/api/health
```

## 6. Validar login demo

Validar al menos:

- SuperAdmin Icodeup
- Admin Empresa
- Lider Cobranzas
- Gestor
- Abogado
- Comercial

Usar solo credenciales locales/demo configuradas en `v2/.env`.

## 7. Validar modulos principales

- Gobierno SaaS
- Mi Empresa
- Roles y permisos
- Clientes
- Obligaciones
- Cola de gestion
- Promesas
- Pagos
- Acuerdos
- Cargas y repartos
- Excel Web
- Juridico
- Documentos
- Ventas
- BI

## 8. Validar que no se versiona informacion local

Antes de cualquier commit:

```powershell
git status --short
git status --ignored --short
```

No deben aparecer como archivos a subir:

- `v2/.env`
- dumps `.dump`
- backups
- logs
- `v2/postgres-data`
- `v2/runtime`
- archivos reales de clientes
