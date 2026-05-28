# Arquitectura V2

## Principios

- La V2 no debe concentrar toda la logica en un solo archivo.
- Las rutas HTTP no deben acceder directamente a SQL sin pasar por servicios/repositorios.
- Las variables sensibles no deben estar quemadas en codigo.
- La parametrizacion del producto debe hacerse desde la aplicacion por IcodeUp plataforma.
- Cada empresa cliente debe estar aislada por tenant.

## Capas

```mermaid
flowchart TD
    UI["Frontend React TypeScript"] --> API["Backend FastAPI"]
    API --> AUTH["Auth y permisos"]
    API --> TENANT["Tenants: empresas, proyectos, usuarios"]
    API --> CRM["CRM: clientes, gestiones, promesas, pagos"]
    API --> PARAM["Parametrizacion: tipificaciones, canales, reglas"]
    API --> REPO["Repositorios SQLAlchemy"]
    REPO --> DB["PostgreSQL"]
    API --> WORKERS["Workers: importaciones, reportes, omnicanalidad"]
    API --> CONFIG["Config .env"]
```

## Backend

- `api/routes`: endpoints HTTP.
- `services`: casos de uso y reglas de negocio.
- `repositories`: acceso a datos.
- `models`: modelos SQLAlchemy.
- `schemas`: contratos Pydantic.
- `core`: configuracion, seguridad y logging.
- `tenancy`: resolucion y aislamiento de empresas.
- `workers`: tareas asincronas.

## Frontend

- `features`: modulos por dominio.
- `components`: UI reutilizable.
- `services`: clientes HTTP.
- `app`: layout, rutas y estado global.
- `styles`: sistema visual.

## Evolucion Pendiente

1. Alembic como migrador formal de esquema.
2. Auditoria inmutable de acciones criticas.
3. Pruebas automatizadas de permisos multiempresa.
4. Integraciones reales de WhatsApp, email y telefonia WebRTC.
5. Workers para importaciones, reportes programados y campanas.
6. Observabilidad, backups y CI/CD para ambientes test, staging y produccion.
