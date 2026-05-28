# IcodeUp CRM V2

Version actual del CRM SaaS corporativo de cobranzas de IcodeUp.

## Objetivo

- Operar como plataforma multiempresa administrada por IcodeUp.
- Aislar datos, usuarios, proyectos y clientes por empresa contratante.
- Centralizar parametrizacion desde usuarios plataforma de IcodeUp.
- Preparar el camino para test, staging y produccion con PostgreSQL, auditoria, integraciones y despliegue seguro.

## Stack

- Backend: FastAPI, SQLAlchemy y Pydantic.
- Base de datos: PostgreSQL.
- Frontend operativo: archivos estaticos servidos por FastAPI.
- Frontend objetivo: React, TypeScript y Vite.
- Configuracion: `.env` por ambiente.
- Seguridad: roles, permisos y autenticacion por token.

## Estado

La V2 ya cuenta con autenticacion, roles, empresas, proyectos, usuarios, clientes, repartos, cola de gestion, gestiones, promesas, pagos, canales, tipificaciones y reporteria BI.

PostgreSQL local esta configurado para desarrollo en `127.0.0.1:5432` y la app corre en:

```text
http://127.0.0.1:8020/
```

## Arranque

Desde la raiz del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\scripts\start-v2.ps1
```

## Data Demo

Para generar data masiva de prueba:

```powershell
cd .\v2\backend
.\.venv\Scripts\python.exe -m app.seeds.scale_demo --customers-per-project 125
```

La data demo crea empresas, proyectos, usuarios, agentes, supervisores, clientes, gestiones, promesas y pagos para validar tablero, cola y BI.
