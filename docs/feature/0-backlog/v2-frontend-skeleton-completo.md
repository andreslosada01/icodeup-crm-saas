# IcodeUp CRM - Backlog de Mejoras

> Análisis completo del proyecto V1 (monolítico funcional) y V2 (modular incompleto).
> Generado: 2026-05-16

---

## Resumen Ejecutivo

El proyecto tiene **DOS versiones paralelas**:

- **V1**: Monolito JavaScript + Python/SQLite. FUNCIONAL en producción local.
- **V2**: Estructura modular React/FastAPI/PostgreSQL. INCOMPLETA, solo esqueleto.

### Dilema Actual

La V1 es insostenible (4000 líneas en un archivo JS) pero funciona.
La V2 tiene buena arquitectura pero está vacía.
**No está claro cómo migrar de V1 a V2 sin romper lo que funciona.**

---

## Criticidad Definiciones

| Símbolo | Nivel | Descripción |
|---------|-------|-------------|
| 🔴 | Crítica | Bloqueante, debe tomarse primero |
| 🟡 | Alta | Importante, siguiente en priorizar |
| 🟢 | Media | Normal, hacer después |
| 🔵 | Baja | Nice-to-have, si hay tiempo |

---

## 🔴 CRÍTICA

### 1. [v2-frontend-skeleton-completo](docs/feature/0-backlog/v2-frontend-skeleton-completo.md)
**Descripción:** Crear la estructura base del frontend V2: routing, layout, API client, estado global, componentes base

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

**User Story:**
Como equipo de desarrollo, necesitamos un esqueleto frontend funcional en V2 para poder empezar a migrar componentes de V1 sin perder funcionalidad.

**Criterios de Aceptación:**
- [ ] Routing configurado con React Router
- [ ] Layout principal con navegación
- [ ] API client funcionando con auth JWT
- [ ] Estado global con Zustand
- [ ] Página de login funcional
- [ ] Dashboard básico

**Tasks:**
- [ ] Configurar React Router con lazy loading
- [ ] Crear API client (fetch wrapper)
- [ ] Implementar Zustand store para auth
- [ ] Crear LoginPage
- [ ] Crear DashboardPage skeleton
- [ ] Configurar Tailwind CSS

---

### 2. [v2-backend-crm-core-migration](docs/feature/0-backlog/v2-backend-crm-core-migration.md)
**Descripción:** Migrar lógica CRM core (customers, promises, payments, campaigns, interactions) del server.py de V1 al backend FastAPI de V2

**Tipo:** Backend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

**User Story:**
Como equipo de desarrollo, necesitamos que el backend V2 tenga toda la lógica CRM operativa para que el frontend pueda conectarse a endpoints reales.

**Criterios de Aceptación:**
- [ ] Endpoints /api/crm/customers completos (CRUD + filtros)
- [ ] Endpoints /api/crm/promises completos
- [ ] Endpoints /api/crm/payments completos
- [ ] Endpoints /api/crm/campaigns completos
- [ ] Endpoints /api/crm/interactions completos
- [ ] Tests unitarios para cada servicio

**Tasks:**
- [ ] Implementar CustomerService + CustomerRepository
- [ ] Implementar PromiseService + PromiseRepository
- [ ] Implementar PaymentService + PaymentRepository
- [ ] Implementar CampaignService + CampaignRepository
- [ ] Implementar InteractionService + InteractionRepository
- [ ] Escribir tests para cada servicio

---

### 3. [migracion-v1-a-v2-plan-concreto](docs/feature/0-backlog/migracion-v1-a-v2-plan-concreto.md)
**Descripción:** Crear plan detallado de migración módulo por módulo de V1 a V2, con dependencias, riesgos y estrategia de conivencia

**Tipo:** Proceso
**Estado:** Backlog
**Fecha creación:** 2026-05-16

**User Story:**
Como equipo de desarrollo, necesitamos un mapa de migración claro que defina qué se mueve primero, qué depende de qué, y cómo mantenemos V1 operativa hasta que V2 esté lista.

**Criterios de Aceptación:**
- [ ] Documento de migración con fases claras
- [ ] Cada módulo de V1 mapeado a componente V2
- [ ] Definidas las dependencias entre módulos
- [ ] Estrategia de rollback definida
- [ ] Criterios de "V2 listo para producción"

**Tasks:**
- [ ] Inventariar todos los módulos de app.js (4000 líneas)
- [ ] Mapear cada módulo a la estructura V2
- [ ] Definir fases de migración
- [ ] Crear criterios de aceptación por fase
- [ ] Documentar estrategia de conivencia (V1 + V2 en paralelo)

---

### 4. [suite-tests-v1-v2](docs/feature/0-backlog/suite-tests-v1-v2.md)
**Descripción:** Implementar suite de tests para garantizar calidad en la migración: unit tests para backend V2, integration tests para APIs, y tests de regresión para V1

**Tipo:** Ambos
**Estado:** Backlog
**Fecha creación:** 2026-05-16

**User Story:**
Como equipo de desarrollo, necesitamos tests para poder refactorizar y migrar sin romper funcionalidad existente.

**Criterios de Aceptación:**
- [ ] pytest configurado en backend
- [ ] Tests para auth endpoints
- [ ] Tests para CRM endpoints
- [ ]覆盖率 > 70% en backend
- [ ] GitHub Actions CI pipeline con tests

**Tasks:**
- [ ] Configurar pytest + fixtures
- [ ] Escribir tests para auth service
- [ ] Escribir tests para customer service
- [ ] Escribir tests para promise service
- [ ] Configurar GitHub Actions
- [ ] Añadir test job al CI

---

## 🟡 ALTA

### 5. [v2-frontend-auth-flow](docs/feature/0-backlog/v2-frontend-auth-flow.md)
**Descripción:** Implementar flow completo de autenticación: login, logout, refresh token, manejo de sesiones, protected routes

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

**User Story:**
Como usuario, quiero hacer login y que el sistema recuerde mi sesión de forma segura.

**Criterios de Aceptación:**
- [ ] Login funcional con email/password
- [ ] JWT almacenado en httpOnly cookie o localStorage seguro
- [ ] Logout limpia sesión
- [ ] Token refresh automático
- [ ] Protected routes redirigen a login
- [ ] Roles verificados en frontend y backend

---

### 6. [docker-compose-produccion](docs/feature/0-backlog/docker-compose-produccion.md)
**Descripción:** Completar docker-compose con todos los servicios: backend, frontend (build), postgres, redis, nginx/caddy para producción local

**Tipo:** Infraestructura
**Estado:** Backlog
**Fecha creación:** 2026-05-16

**User Story:**
Como DevOps, quiero un docker-compose completo que levante todo el entorno de producción local para probar antes de deployar.

**Criterios de Aceptación:**
- [ ] Servicio backend con Dockerfile
- [ ] Servicio frontend con build Docker
- [ ] Nginx como reverse proxy
- [ ] Volumes para persistencia
- [ ] Redes definidas
- [ ] Health checks en todos los servicios

---

### 7. [alembic-migrations-v2](docs/feature/0-backlog/alembic-migrations-v2.md)
**Descripción:** Configurar y escribir migraciones Alembic para todos los modelos SQLAlchemy de V2

**Tipo:** Backend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

**User Story:**
Como equipo de desarrollo, necesitamos migraciones versionadas para poder desplegar cambios de schema de forma controlada.

**Criterios de Aceptación:**
- [ ] Alembic inicializado y configurado
- [ ] Migración inicial con todos los modelos
- [ ] Scripts de seed para desarrollo
- [ ] Documentación de commands de migración

---

### 8. [v2-frontend-dashboard-crm](docs/feature/0-backlog/v2-frontend-dashboard-crm.md)
**Descripción:** Migrar el dashboard de V1 (métricas, gráficos, indicadores) al frontend V2 con diseño moderno

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

**User Story:**
Como gestor, quiero ver mi dashboard con métricas clave de cobranza de forma clara y visual.

**Criterios de Aceptación:**
- [ ] Métricas principales (cartera, recuperación, promesas)
- [ ] Gráfico de embudo de cobranza
- [ ] Tabla de agentes con productividad
- [ ] Lista de promesas del día
- [ ] Filtros por segmento

---

### 9. [v2-frontend-customer-management](docs/feature/0-backlog/v2-frontend-customer-management.md)
**Descripción:** Migrar gestión de clientes: lista, filtros, detalle, formulario, timeline

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 10. [v2-frontend-queue-management](docs/feature/0-backlog/v2-frontend-queue-management.md)
**Descripción:** Migrar cola de gestión con filtros, paginación, y detalle de expediente

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

## 🟢 MEDIA

### 11. [linting-formatting-standards](docs/feature/0-backlog/linting-formatting-standards.md)
**Descripción:** Configurar ESLint, Prettier, Ruff, y Git hooks con Husky para ambos proyectos (V1 y V2)

**Tipo:** Proceso
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 12. [v2-frontend-typification-admin](docs/feature/0-backlog/v2-frontend-typification-admin.md)
**Descripción:** Migrar administración de tipificaciones (árbol de tipificaciones por empresa)

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 13. [v2-frontend-campaigns](docs/feature/0-backlog/v2-frontend-campaigns.md)
**Descripción:** Migrar gestión de campañas de cobranza

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 14. [v2-frontend-settings](docs/feature/0-backlog/v2-frontend-settings.md)
**Descripción:** Migrar configuración: parámetros de cartera, canales de comunicación, variables de scoring

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 15. [v2-backend-tenants-admin](docs/feature/0-backlog/v2-backend-tenants-admin.md)
**Descripción:** Implementar panel de administración de tenants (empresas) para platform_admin

**Tipo:** Backend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 16. [v2-frontend-tenants-admin](docs/feature/0-backlog/v2-frontend-tenants-admin.md)
**Descripción:** Implementar UI del panel de administración de tenants

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 17. [csv-import-v2](docs/feature/0-backlog/csv-import-v2.md)
**Descripción:** Implementar importación masiva de cartera por CSV/Excel en V2

**Tipo:** Ambos
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

## 🔵 BAJA

### 18. [v1-refactor-comments](docs/feature/0-backlog/v1-refactor-comments.md)
**Descripción:** Limpiar app.js: eliminar comentarios redundantes, organizar funciones, documentar con JSDoc

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 19. [error-boundaries-v2](docs/feature/0-backlog/error-boundaries-v2.md)
**Descripción:** Implementar ErrorBoundaries en React V2 para manejo graceful de errores

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 20. [logging-centralizado](docs/feature/0-backlog/logging-centralizado.md)
**Descripción:** Implementar logging estructurado con trazabilidad (request IDs) en backend

**Tipo:** Backend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 21. [v2-frontend-reports](docs/feature/0-backlog/v2-frontend-reports.md)
**Descripción:** Migrar reportería y BI del CRM

**Tipo:** Frontend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 22. [v2-audit-log](docs/feature/0-backlog/v2-audit-log.md)
**Descripción:** Implementar auditoría inmutable de cambios sensibles

**Tipo:** Backend
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 23. [v2-omnichannel-integrations](docs/feature/0-backlog/v2-omnichannel-integrations.md)
**Descripción:** Implementar integraciones reales: WhatsApp API, email SMTP, telefonia WebRTC

**Tipo:** Ambos
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

### 24. [deploy-ci-cd](docs/feature/0-backlog/deploy-ci-cd.md)
**Descripción:** Implementar CI/CD con GitHub Actions: build, test, deploy a staging/producción

**Tipo:** Infraestructura
**Estado:** Backlog
**Fecha creación:** 2026-05-16

---

## Inventario V1 (app.js ~4000 líneas)

| Módulo | Líneas aprox. | Estado migración V2 |
|--------|---------------|---------------------|
| Constantes y configuración | 1-100 | No migrado |
| Estado default (datos demo) | 25-330 | No migrado |
| Inicialización y elementos DOM | 331-415 | No migrado |
| Login y autenticación | 416-580 | No migrado |
| Navegación y vistas | 581-730 | No migrado |
| Formularios (promesas, pagos, campaigns) | 731-1130 | No migrado |
| Población de opciones estáticas | 1131-1210 | No migrado |
| Renderizado de vistas | 1211-2500+ | No migrado |
| Lógica de negocio (promesas, pagos) | 2500-3000+ | No migrado |
| Funciones utilitarias | 3000-3500+ | No migrado |
| Event listeners | 3500-4000+ | No migrado |

**Total estimado: 4000+ líneas en un solo archivo**

---

## Arquitectura V2 - Estado de Avance

### Backend (FastAPI)
```
v2/backend/
├── app/
│   ├── api/routes/
│   │   ├── administration.py  ⚠️ Implementado pero básico
│   │   ├── auth.py           ⚠️ Implementado pero básico
│   │   ├── crm.py            ⚠️ Implementado pero básico
│   │   ├── health.py         ✅ Básico
│   │   ├── tenants.py        ⚠️ Implementado pero básico
│   │   └── typifications.py  ⚠️ Implementado pero básico
│   ├── core/
│   │   ├── config.py         ✅ Configuración .env
│   │   ├── roles.py          ⚠️ Roles definidos
│   │   └── security.py       ⚠️ JWT básico
│   ├── db/
│   │   ├── migrations.py     ⚠️ No hay Alembic
│   │   └── session.py        ⚠️ Session maker
│   ├── models/
│   │   ├── crm.py            ⚠️ Modelos definidos
│   │   ├── identity.py       ⚠️ User/Company
│   │   └── tenant.py         ⚠️ Tenant models
│   ├── repositories/         ⚠️ Solo esqueletos
│   ├── schemas/              ⚠️ Pydantic models
│   └── services/             ⚠️ Solo bootstrapping
└── pyproject.toml            ✅ Dependencias
```

### Frontend (React + Vite)
```
v2/frontend/
├── index.html                ✅ entry point
├── package.json              ⚠️ Solo dependencias básicas
├── src/
│   └── app/
│       ├── main.tsx          ⚠️ SOLO dice "Arquitectura modular iniciada"
│       └── styles.css        ⚠️ Vacío
└── static/
    └── assets/               ⚠️ Carpeta vacía (esperando build)
```

**Estado: Frontend V2 NO EXISTE más allá del entry point**

---

## Recomendación de Priorización

### Fase 1: Hacer V2 Funcional (mes 1-2)
1. v2-frontend-skeleton-completo
2. v2-backend-crm-core-migration
3. alembic-migrations-v2
4. suite-tests-v1-v2
5. migracion-v1-a-v2-plan-concreto

### Fase 2: Migrar Features V1 → V2 (mes 3-4)
6. v2-frontend-auth-flow
7. v2-frontend-dashboard-crm
8. v2-frontend-customer-management
9. v2-frontend-queue-management
10. v2-backend-tenants-admin

### Fase 3: Completar V2 (mes 5-6)
11. v2-frontend-typification-admin
12. v2-frontend-campaigns
13. v2-frontend-settings
14. docker-compose-produccion
15. csv-import-v2

### Fase 4: Calidad y Produccion (mes 7+)
16. linting-formatting-standards
17. deploy-ci-cd
18. v2-frontend-tenants-admin
19. v2-frontend-reports
20. v2-audit-log

---

## Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Líneas V1 (app.js) | ~4000 |
| Archivos en V2 backend | ~30 |
| Archivos en V2 frontend | 3 |
| Cobertura de tests | 0% |
| Documentos de arquitectura | 5+ |
| Features en backlog | 24 |

---

*Última actualización: 2026-05-16*