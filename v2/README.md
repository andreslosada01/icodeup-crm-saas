# IcodeUp CRM V2

Version corporativa del CRM SaaS de cobranzas.

Esta carpeta nace para rehacer la aplicacion con arquitectura modular, configuracion por ambiente y separacion clara entre frontend, backend, dominio, datos e infraestructura.

## Objetivo

- Mantener la V1 como prototipo funcional.
- Construir V2 con arquitectura lista para pruebas, staging y produccion.
- Evitar variables quemadas en codigo.
- Centralizar la parametrizacion en usuarios IcodeUp plataforma.
- Preparar el camino para PostgreSQL, auditoria, integraciones omnicanalidad y despliegue seguro.

## Stack Propuesto

- Frontend: React + TypeScript + Vite.
- Backend: FastAPI + SQLAlchemy + Alembic.
- Base de datos: PostgreSQL.
- Cache/colas: Redis + worker para importaciones, reportes e integraciones.
- Autenticacion: JWT/sesiones seguras, roles y permisos por tenant.
- Configuracion: `.env` por ambiente.

## Estado

Base inicial creada. PostgreSQL local esta configurado para desarrollo en `127.0.0.1:5432` y la V2 corre en `http://127.0.0.1:8020/`.

Arranque recomendado desde la raiz del proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\scripts\start-v2.ps1
```

La implementacion funcional se migrara por modulos desde V1.
