# IcodeUp CRM - Estructura actual

## Distribucion del proyecto

El proyecto esta en una fase funcional local, todavia ligera:

- `index.html`: estructura de pantallas del CRM.
- `styles.css`: estilos visuales y responsive.
- `app.js`: logica de interfaz, filtros, gestion de clientes, carga CSV, roles visibles y sincronizacion con API.
- `server.py`: backend HTTP, login, sesiones, permisos, SQLite y endpoints API.
- `data/platform.sqlite3`: base local de plataforma IcodeUp.
- `data/tenants/*.sqlite3`: bases locales independientes por empresa cliente.
- `data/icodeup_crm.sqlite3`: base anterior conservada como fuente de migracion local.
- `assets/`: logo e imagenes.
- `run-crm.ps1`: script para levantar el servidor local.
- `README.md`: instrucciones de uso.
- `PLAN_PRODUCCION.md`: ruta funcional y tecnica hacia produccion.

## Lenguajes y tecnologias

- Frontend: HTML, CSS y JavaScript puro.
- Backend: Python con librerias estandar.
- Base de datos local: SQLite.
- Persistencia productiva recomendada: PostgreSQL.
- Despliegue recomendado futuro: Docker, HTTPS, dominio, backups y monitoreo.

## Modelo SaaS multiempresa

El CRM debe operar con una URL comun, por ejemplo `https://crm.icodeup.com`. El usuario no escoge empresa en el login: el sistema identifica su entorno desde una capa de plataforma y carga solo la informacion de su empresa.

Para produccion, la arquitectura recomendada es:

- Base de plataforma: empresas contratantes, usuarios de acceso, suscripciones, estado de tenant, dominios, auditoria global y mapa de conexion.
- Base independiente por empresa cliente: clientes, proyectos, repartos, usuarios operativos, gestiones, promesas, pagos, tipificaciones, canales, reportes y auditoria operativa.
- Codigo aplicativo compartido: los cambios funcionales se despliegan una sola vez y aplican a todas las empresas, sin mezclar datos.
- Panel IcodeUp plataforma: crea empresas, crea proyectos base, activa/inactiva tenants y revisa salud del servicio.
- Centro de control IcodeUp: inventario y administracion de usuarios y proyectos de todos los tenants.

En la version local actual ya se usa una separacion fisica compatible con SaaS:

- `platform.sqlite3` mantiene IcodeUp, empresas contratantes, usuarios de login, sesiones y auditoria global.
- `data/tenants/<slug>.sqlite3` mantiene la operacion de cada empresa: proyectos, clientes, repartos, usuarios, gestiones, promesas, pagos, canales y reportes.

Las tablas conservan `company_id` como defensa adicional y para facilitar la migracion futura a PostgreSQL por base o por esquema.

## Modulos de negocio

Aunque aun no esta separado en carpetas, el sistema ya esta tomando esta forma modular:

- Autenticacion y sesiones.
- Empresas multi-tenant.
- Usuarios, roles, lideres y gestores.
- Carteras/repartos.
- Clientes y obligaciones.
- Cola de gestion.
- Tipificaciones.
- Promesas y pagos.
- Omnicanalidad.
- Reportes.
- Configuracion y variables.
- Administracion SaaS de empresas contratantes y proyectos.

## Proxima modularizacion recomendada

Cuando demos el salto a una base mas grande, conviene mover a:

```text
backend/
  app/
    auth/
    companies/
    users/
    portfolios/
    customers/
    interactions/
    payments/
    channels/
    reports/
  migrations/
frontend/
  src/
    views/
    components/
    services/
database/
  schema/
  seeds/
platform/
  tenants/
  provisioning/
```

Por ahora se mantiene simple para iterar rapido y validar el flujo operativo.
