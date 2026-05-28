# IcodeUp CRM SaaS

Repositorio oficial de IcodeUp CRM V2, una plataforma SaaS corporativa para cobranzas, recuperacion de cartera, gestion operativa, analitica BI y administracion multiempresa.

La version activa del producto vive en `v2/`. El repositorio fue depurado para mantener una sola base de codigo y evitar confusiones de arranque, arquitectura y despliegue.

## Arranque Local

Ejecuta desde la raiz del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\scripts\start-v2.ps1
```

Luego abre:

```text
http://127.0.0.1:8020/
```

Credenciales locales de plataforma:

```text
platform@icodeup.com
ChangeMeV2Local!
```

## Stack

- Backend: FastAPI, SQLAlchemy y PostgreSQL.
- Frontend operativo: HTML, CSS y JavaScript servido por FastAPI.
- Frontend objetivo: React, TypeScript y Vite.
- Autenticacion: tokens JWT y roles por tenant.
- Base de datos local: PostgreSQL portable para desarrollo.
- Arquitectura SaaS: IcodeUp plataforma, empresas cliente, proyectos, usuarios, clientes y datos aislados por tenant.

## Modulos Actuales

- Login corporativo.
- Tablero ejecutivo y BI predictivo.
- Cola de gestion.
- Clientes y carga de repartos.
- Promesas de pago.
- Pagos.
- Canales de comunicacion.
- Empresas cliente.
- Proyectos/carteras.
- Usuarios, lideres, supervisores y agentes.
- Tipificaciones parametrizables.
- Data demo masiva para pruebas operativas.

## Rutas Relevantes

- Backend: `v2/backend/app/`
- Frontend estatico: `v2/frontend/static/`
- Scripts locales: `v2/scripts/`
- Documentacion tecnica: `v2/docs/`
- Sembrador demo: `v2/backend/app/seeds/scale_demo.py`

## Seguridad Local

No se versionan `.env`, entornos virtuales, runtime portable de PostgreSQL, base de datos local ni logs. Usa `v2/.env.example` como referencia para crear configuraciones por ambiente.
