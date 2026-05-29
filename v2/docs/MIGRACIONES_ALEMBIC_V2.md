# Migraciones Alembic V2

## Por que se agrega Alembic

Icodeup 360 necesita migraciones versionadas para pasar de desarrollo local a test y produccion sin depender solo de `Base.metadata.create_all` ni de SQL manual compatible.

Alembic queda como mecanismo formal para versionar cambios de esquema.

## Estructura

```text
v2/backend/
  alembic.ini
  alembic/
    env.py
    script.py.mako
    versions/
      20260528_0001_initial_schema_v2_product_hardening.py
```

## Configuracion

`alembic/env.py` usa:

- `app.core.config.settings.database_url`
- `app.db.session.Base.metadata`
- imports de `app.models` para cargar toda la metadata SQLAlchemy

## Migracion inicial

La revision inicial es:

`20260528_0001_initial_schema_v2_product_hardening`

Es una baseline no destructiva. Crea tablas faltantes con `checkfirst=True` y no elimina datos, tablas ni columnas.

## Relacion con apply_compatibility_migrations

`v2/backend/app/db/migrations.py` se mantiene temporalmente.

Durante esta etapa:

- `Base.metadata.create_all` sigue permitiendo desarrollo local rapido.
- `apply_compatibility_migrations` conserva compatibilidad con bases creadas antes del hardening.
- Alembic queda preparado para test/produccion y futuras migraciones versionadas.

No se debe retirar `apply_compatibility_migrations` hasta que una base de test confirme que Alembic cubre todos los cambios historicos.

## Comandos

Desde `v2/backend`:

```powershell
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "descripcion_del_cambio"
```

## Recomendacion local

1. Levantar PostgreSQL local.
2. Validar `v2/.env`.
3. Ejecutar `alembic current`.
4. Ejecutar `alembic upgrade head`.
5. Arrancar la app y validar `/api/health`.

## Recomendacion servidor

1. Backup antes de migrar.
2. Ejecutar migraciones en ambiente de test.
3. Ejecutar pruebas automatizadas multi-tenant.
4. Validar login, menu dinamico, exportes y modulos.
5. Aplicar en produccion con ventana controlada.

## Advertencias antes de produccion

- No ejecutar autogenerate directo sobre produccion sin revisar el diff.
- No aceptar operaciones `drop_table`, `drop_column` o renombres sin plan de rollback.
- Convertir las migraciones compatibles historicas en revisiones Alembic explicitas antes de retirar `apply_compatibility_migrations`.
