# Auditoria Producto CRM SaaS V2

Producto objetivo: **Icodeup Collection & Legal CRM**  
Version auditada: `v2/`  
Fecha: 2026-05-28  
Rama de trabajo: `feature/product-hardening-collection-legal-crm`

## 1. Estado actual del producto

La V2 es una aplicacion funcional de CRM SaaS para cobranzas operativas. Cuenta con autenticacion, roles, empresas contratantes, proyectos/carteras, usuarios, clientes/deudores, cola de gestion, promesas, pagos, canales, tipificaciones, tablero ejecutivo, BI operativo y carga CSV.

El producto ya tiene una base real para operar localmente con PostgreSQL y frontend estatico servido por FastAPI. Aun requiere hardening para convertirse en SaaS comercial completo: planes, modulos activables, auditoria transversal, acuerdos de pago, documentos, juridico, ventas iniciales, controles de permisos mas granulares y pruebas de regresion.

## 2. Stack tecnico detectado

- Backend: FastAPI.
- ORM: SQLAlchemy 2 con `DeclarativeBase`.
- Schemas: Pydantic.
- Base de datos: PostgreSQL.
- Autenticacion: token Bearer con `python-jose`.
- Seguridad de clave: `bcrypt`.
- Frontend actual: HTML, CSS y JavaScript vanilla servido por FastAPI.
- Frontend objetivo declarado: React, TypeScript y Vite.
- Arranque local: scripts PowerShell en `v2/scripts`.
- Infra inicial: `v2/infra/docker-compose.yml`.

## 3. Estructura de carpetas relevante

```text
v2/
  backend/
    app/
      api/
        deps.py
        routes/
          administration.py
          auth.py
          crm.py
          health.py
          tenants.py
          typifications.py
      core/
        config.py
        roles.py
        security.py
      db/
        migrations.py
        session.py
      models/
        crm.py
        identity.py
        tenant.py
      repositories/
        administration_repository.py
        tenant_repository.py
        typification_repository.py
      schemas/
        administration.py
        auth.py
        crm.py
        tenant.py
        typification.py
      seeds/
        scale_demo.py
      services/
        auth_service.py
        bootstrap_service.py
  frontend/
    static/
      index.html
      assets/
        app.js
        styles.css
        icodeup-logo.png
  docs/
  infra/
  scripts/
```

## 4. Modulos backend existentes

- `auth`: login y emision de token.
- `health`: verificacion de aplicacion y PostgreSQL.
- `administration`: administracion plataforma de tenants, proyectos, usuarios y asignaciones.
- `tenants`: CRUD basico de tenants para platform admin.
- `typifications`: arboles de tipificacion por tenant.
- `crm`: modulo monolitico con opciones, dashboard, BI, clientes, importacion CSV, actividades, promesas, pagos y canales.

## 5. Modelos SQLAlchemy existentes y proposito

- `Tenant`: empresa contratante o tenant interno de IcodeUp.
- `Project`: proyecto/cartera dentro de una empresa.
- `User`: usuario autenticable, con tenant, rol, lider y estado.
- `UserProjectAssignment`: asignacion de usuarios a proyectos.
- `Customer`: cliente/deudor con datos financieros, demograficos y de gestion.
- `TypificationNode`: nodo de arbol de tipificacion.
- `ManagementActivity`: gestion realizada a un cliente.
- `PaymentPromise`: promesa de pago.
- `Payment`: pago registrado.
- `CommunicationChannel`: canal configurable por tenant/proyecto.
- `ImportBatch`: lote de importacion CSV.

## 6. Endpoints actuales por router

### Auth

- `POST /api/auth/login`

### Health

- `GET /api/health`

### Administration

- `GET /api/admin/overview`
- `GET /api/admin/roles`
- `GET /api/admin/tenants`
- `POST /api/admin/tenants`
- `PATCH /api/admin/tenants/{tenant_id}`
- `GET /api/admin/projects`
- `POST /api/admin/projects`
- `PATCH /api/admin/projects/{project_id}`
- `GET /api/admin/users`
- `POST /api/admin/users`
- `PATCH /api/admin/users/{user_id}`
- `PUT /api/admin/users/{user_id}/projects`

### Tenants

- `GET /api/tenants`
- `POST /api/tenants`

### Typifications

- `GET /api/typifications`
- `POST /api/typifications`
- `PATCH /api/typifications/{node_id}`
- `DELETE /api/typifications/{node_id}`

### CRM

- `GET /api/crm/options`
- `GET /api/crm/typifications`
- `GET /api/crm/dashboard`
- `GET /api/crm/bi`
- `GET /api/crm/customers`
- `POST /api/crm/customers`
- `POST /api/crm/customers/import`
- `GET /api/crm/customers/{customer_id}/activities`
- `POST /api/crm/customers/{customer_id}/activities`
- `GET /api/crm/promises`
- `POST /api/crm/promises`
- `PATCH /api/crm/promises/{promise_id}/complete`
- `GET /api/crm/payments`
- `POST /api/crm/payments`
- `GET /api/crm/channels`
- `POST /api/crm/channels`

## 7. Funcionalidades reales disponibles hoy

- Login por token.
- Bootstrap de plataforma.
- Administracion de empresas, proyectos y usuarios desde IcodeUp plataforma.
- Roles principales: platform admin, tenant admin, coordinator, quality supervisor y agent.
- Asignacion de usuarios a proyectos.
- Clientes con saldo, mora, riesgo, prioridad, contacto y proxima accion.
- Importacion CSV de clientes con upsert por tenant/proyecto/documento.
- Cola paginada de clientes.
- Actividades de gestion con tipificacion.
- Creacion y cumplimiento de promesas.
- Registro de pagos y ajuste de saldo.
- Canales configurables para WhatsApp, email y telefonia.
- Tipificaciones administrables.
- Dashboard ejecutivo.
- BI operativo con KPIs, alertas, semaforos, prediccion y oportunidades.
- Data demo masiva para validacion.

## 8. Funcionalidades incompletas o mencionadas pero no implementadas

- Planes SaaS y suscripciones por tenant.
- Activacion/desactivacion de modulos por tenant.
- Acuerdos de pago con cuotas.
- Modulo juridico.
- Gestion documental.
- Ventas / CRM 360.
- Auditoria transversal.
- Versionado formal de migraciones.
- Integraciones reales de WhatsApp Business API, SMTP/Graph/Gmail y telefonia WebRTC.
- Softphone embebido.
- Control avanzado de permisos por accion.
- Storage documental por tenant.
- Pruebas automatizadas.
- Observabilidad productiva.
- Recuperacion de clave, MFA y politicas de contrasena.

## 9. Riesgos tecnicos

- `crm.py` concentra demasiadas responsabilidades y dificulta evolucionar el producto.
- `Base.metadata.create_all` sirve para desarrollo, pero no reemplaza migraciones controladas en produccion.
- Frontend vanilla crece en complejidad y puede volverse dificil de mantener.
- Reglas de negocio y serializacion viven mezcladas en routers.
- No hay capa de servicios para operaciones criticas como pagos, importaciones y auditoria.
- No existe test suite que proteja regresiones.

## 10. Riesgos de seguridad

- No se detecta MFA, politicas de expiracion de sesiones ni recuperacion segura de cuenta.
- La auditoria de acciones criticas no esta implementada.
- El control de permisos existe, pero debe ampliarse por modulo y por accion.
- Integraciones futuras con canales deben evitar almacenar secretos sin cifrado.
- No debe subirse `.env`, bases locales, logs, runtime PostgreSQL ni documentos reales.
- El modelo documental requiere validacion fuerte de tenant y storage aislado.

## 11. Riesgos de escalabilidad

- Consultas de dashboard y BI cargan colecciones en memoria; con carteras grandes requeriran agregaciones SQL y materializacion.
- No hay paginacion en todos los listados operativos.
- Importacion CSV se ejecuta sin jobs asincronos.
- No hay colas de tareas para integraciones, notificaciones o scoring.
- No hay cache ni indices especializados para reporteria masiva.

## 12. Riesgos de arquitectura

- El CRM esta centrado en un router monolitico.
- Las reglas de acceso estan duplicables si no se extraen a utilidades compartidas.
- No hay frontera clara entre core SaaS, cobranzas, juridico, documentos, ventas e integraciones.
- El frontend actual depende de rutas existentes; cualquier cambio de URL romperia la operacion.
- Falta un contrato formal de modulos activables por tenant.

## 13. Evaluacion del modelo SaaS multiempresa

La base multiempresa existe: tenants, proyectos por tenant, usuarios por tenant y clientes por tenant/proyecto. El platform admin de IcodeUp puede ver y administrar globalmente. Los usuarios tenant se limitan a su empresa en las rutas principales.

Para SaaS comercial falta modelar planes, suscripciones, modulos, limites y estado contractual. Tambien falta una politica explicita para tenants sin plan: por compatibilidad debe ser permisiva inicialmente.

## 14. Evaluacion del aislamiento por tenant

El aislamiento esta presente en clientes, proyectos, canales y tipificaciones. Los agentes solo ven clientes asignados. El mayor riesgo esta en nuevas funcionalidades: cualquier modulo nuevo debe validar `tenant_id` en todas las relaciones y nunca confiar solo en IDs enviados por frontend.

Recomendacion: centralizar funciones de acceso, validar entidades relacionadas y agregar pruebas de acceso cruzado.

## 15. Evaluacion del modelo de roles y permisos

Roles actuales:

- `platform_admin`: IcodeUp, acceso global.
- `tenant_admin`: administra su empresa.
- `coordinator`: gestiona operacion de su empresa/equipo.
- `quality_supervisor`: lectura y control de calidad.
- `agent`: gestion de clientes asignados.

El modelo es suficiente para V2, pero debe evolucionar hacia permisos por modulo y accion para juridico, documentos, BI avanzado, integraciones y ventas.

## 16. Evaluacion del frontend actual

El frontend actual es funcional y moderno para una V2 operativa. Tiene login, navegacion, tablero, cola, clientes, promesas, pagos, reportes BI, canales, empresas, proyectos, usuarios y tipificaciones.

El riesgo principal es mantenibilidad: `app.js` concentra estado, renderizado, llamadas API y eventos. A corto plazo se puede mantener con placeholders y cambios pequenos. A mediano plazo conviene migrar a React/Vite con componentes, router, estado y pruebas.

## 17. Brechas para convertirlo en Collection & Legal CRM

- Acuerdos de pago con cuotas.
- Expedientes juridicos.
- Actuaciones, audiencias y vencimientos.
- Documentos vinculados a cliente, pago, acuerdo o caso.
- Auditoria corporativa.
- Permisos por modulo.
- Reporteria por etapa juridica, riesgo legal y recuperacion esperada.
- Dashboard de vencimientos y alertas legales.

## 18. Brechas para modulo juridico

- No existen casos juridicos.
- No hay abogado asignado ni rol legal especializado.
- No hay radicados, juzgados, etapas, audiencias ni vencimientos.
- No existe relacion documental juridica.
- No hay matriz de riesgo legal.

## 19. Brechas para modulo documental

- No existe tabla documental.
- No existe storage fisico ni metadatos.
- No hay validacion de tipos documentales.
- No hay relacion con cliente, pago, acuerdo o caso juridico.
- No hay trazabilidad de cambios documentales.

## 20. Brechas para modulo ventas

- No existen leads ni oportunidades.
- No hay pipeline comercial.
- No hay asignacion comercial ni fuentes.
- No hay proyeccion de cierre.
- No hay separacion entre CRM de cobranza y CRM 360 futuro.

## 21. Backlog priorizado por fases

1. Refactor seguro de `crm.py` en subrouters sin cambiar URLs.
2. Modelar planes SaaS, suscripciones y modulos por tenant.
3. Crear acuerdos de pago con cuotas.
4. Crear juridico minimo: casos, actuaciones, audiencias y vencimientos.
5. Crear documentos como metadatos y preparar storage.
6. Crear ventas minimo: leads y oportunidades.
7. Agregar auditoria transversal.
8. Agregar placeholders frontend sin romper experiencia actual.
9. Crear documentacion de roadmap y checklist de regresion.
10. Preparar suite automatizada inicial y migraciones formales.

## Tabla de recomendaciones

| Prioridad | Mejora | Archivos impactados | Riesgo de cambio | Beneficio esperado | Recomendacion |
| --- | --- | --- | --- | --- | --- |
| Alta | Refactorizar `crm.py` en subrouters | `v2/backend/app/api/routes/crm/*` | Medio | Mantenibilidad y escalabilidad | Hacer sin cambiar rutas ni schemas |
| Alta | Centralizar acceso CRM | `access.py` | Medio | Menos riesgo de acceso cruzado | Reusar en modulos nuevos |
| Alta | Agregar auditoria | `models/audit.py`, `services/audit_service.py`, routers | Medio | Trazabilidad corporativa | Registrar eventos criticos primero |
| Alta | Agregar acuerdos de pago | `models/crm.py`, `schemas/crm.py`, `routes/crm/agreements.py` | Medio | Core real de cobranzas | Mantener promesas y pagos existentes |
| Alta | Agregar juridico minimo | `models/legal.py`, `schemas/legal.py`, `routes/legal.py` | Medio | Evolucion a Collection & Legal CRM | Validar tenant en cada relacion |
| Media | Agregar documentos metadata | `models/documents.py`, `schemas/documents.py`, `routes/documents.py` | Medio | Preparar expedientes | No subir binarios en esta fase |
| Media | Agregar planes SaaS | `models/subscription.py`, `routes/subscriptions.py` | Bajo | Producto vendible por plan | Comportamiento permisivo inicial |
| Media | Agregar ventas minimo | `models/sales.py`, `schemas/sales.py`, `routes/sales.py` | Bajo | Camino a CRM 360 | Dejar separado del core de cobranzas |
| Media | Placeholders frontend | `index.html`, `app.js`, `styles.css` | Bajo | Navegacion comercial visible | No redisenar todo ahora |
| Alta | Checklist de regresion | `docs/CHECKLIST_PRUEBAS_REGRESION_V2.md` | Bajo | Control de calidad | Usarlo antes de cada release |
| Media | Migraciones formales | `alembic` futuro | Medio | Produccion segura | No hacer destructivo en V2.1 |
| Media | Tests automatizados | `tests/` futuro | Medio | Menos regresiones | Empezar por auth, permisos y CRM |
