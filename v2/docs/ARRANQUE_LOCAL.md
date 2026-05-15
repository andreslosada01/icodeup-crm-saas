# Arranque Local V2

## Puertos

- V1 funcional: `http://127.0.0.1:8010/`
- V2 arquitectura nueva: `http://127.0.0.1:8020/`

## Backend V2

Desde la raiz del proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\scripts\start-v2.ps1
```

## PostgreSQL

Para desarrollo local dejamos PostgreSQL portable dentro de V2:

```text
v2/runtime/pgsql
```

Los datos locales quedan en:

```text
v2/postgres-data
```

Estos directorios estan excluidos en `.gitignore` porque no son codigo fuente.

El script de arranque valida PostgreSQL, crea la base si falta y luego inicia el backend:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\scripts\start-v2.ps1
```

Si solo quieres iniciar la base:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\scripts\start-postgres.ps1
```

Si quieres detener la base:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\scripts\stop-postgres.ps1
```

La V2 lee la conexion desde el archivo local:

```text
v2/.env
```

Variable:

```text
DATABASE_URL=postgresql+psycopg://icodeup:icodeup@localhost:5432/icodeup_crm
```

Si PostgreSQL usa otro usuario, contrasena, host o puerto, cambia esa variable.

## Estado actual

PostgreSQL esta configurado localmente en `127.0.0.1:5432` con la base `icodeup_crm`.

El endpoint:

```text
http://127.0.0.1:8020/api/health
```

debe mostrar `PostgreSQL conectado`.

## Siguiente paso

Continuar la migracion funcional de modulos de V1 a V2: empresas, proyectos, usuarios, clientes, tipificaciones, gestiones, auditoria y reporteria.
