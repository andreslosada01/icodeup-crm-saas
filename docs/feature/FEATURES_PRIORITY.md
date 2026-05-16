# IcodeUp CRM - Feature Priority

> Se actualiza automáticamente en cada operación de backlog.

---

## 📊 Resumen

| Criticidad | Backlog | WIP | Done |
|------------|---------|-----|------|
| 🔴 Crítica | 12 | - | - |
| 🟡 Alta | 6 | - | - |
| 🟢 Media | 17 | - | - |
| 🔵 Baja | 4 | - | - |

---

## 🔴 CRÍTICA (Tomar primero)

### 📋 Backlog

#### 1. [v2-frontend-configurar-vite-tailwind](0-backlog/v2-frontend-configurar-vite-tailwind.md)
- **Descripción:** Configurar Vite con React, TypeScript strict mode y Tailwind CSS v4 en el frontend V2
- **Fecha creación:** 2026-05-16

#### 2. [v2-frontend-react-router](0-backlog/v2-frontend-react-router.md)
- **Descripción:** Configurar React Router v6 con lazy loading y route base para el CRM
- **Fecha creación:** 2026-05-16

#### 3. [v2-frontend-api-client](0-backlog/v2-frontend-api-client.md)
- **Descripción:** Crear API client con interceptor de auth, manejo de errores y tipos TypeScript
- **Fecha creación:** 2026-05-16

#### 4. [v2-frontend-zustand-store](0-backlog/v2-frontend-zustand-store.md)
- **Descripción:** Implementar Zustand store para estado global: auth, ui y datos del CRM
- **Fecha creación:** 2026-05-16

#### 5. [v2-frontend-layout-base](0-backlog/v2-frontend-layout-base.md)
- **Descripción:** Crear layout base del CRM: sidebar de navegación, header con usuario, área de contenido
- **Fecha creación:** 2026-05-16

#### 6. [v2-frontend-login-page](0-backlog/v2-frontend-login-page.md)
- **Descripción:** Crear página de login funcional que se conecte al backend V2
- **Fecha creación:** 2026-05-16

#### 7. [v2-backend-configurar-pytest](0-backlog/v2-backend-configurar-pytest.md)
- **Descripción:** Configurar pytest con fixtures, async support y coverage en el backend V2
- **Fecha creación:** 2026-05-16

#### 8. [v2-backend-auth-service-completo](0-backlog/v2-backend-auth-service-completo.md)
- **Descripción:** Implementar auth service completo: register, login, logout, refresh token, password hash
- **Fecha creación:** 2026-05-16

#### 9. [v2-backend-customer-repository](0-backlog/v2-backend-customer-repository.md)
- **Descripción:** Implementar CustomerRepository con operaciones CRUD y filtros
- **Fecha creación:** 2026-05-16

#### 10. [v2-backend-customer-service](0-backlog/v2-backend-customer-service.md)
- **Descripción:** Implementar CustomerService con lógica de negocio: scoring, risk calculation, status transitions
- **Fecha creación:** 2026-05-16

#### 11. [v2-backend-promise-repository](0-backlog/v2-backend-promise-repository.md)
- **Descripción:** Implementar PromiseRepository: CRUD de promesas de pago
- **Fecha creación:** 2026-05-16

#### 12. [v2-backend-payment-repository](0-backlog/v2-backend-payment-repository.md)
- **Descripción:** Implementar PaymentRepository: CRUD de pagos registrados
- **Fecha creación:** 2026-05-16

---

## 🟡 ALTA

### 📋 Backlog

#### 1. [v2-backend-customer-endpoint](0-backlog/v2-backend-customer-endpoint.md)
- **Descripción:** Crear endpoint REST /api/crm/customers con GET, POST, PUT, DELETE
- **Fecha creación:** 2026-05-16

#### 2. [v2-backend-promise-endpoint](0-backlog/v2-backend-promise-endpoint.md)
- **Descripción:** Crear endpoint REST /api/crm/promises con GET y POST
- **Fecha creación:** 2026-05-16

#### 3. [v2-backend-payment-endpoint](0-backlog/v2-backend-payment-endpoint.md)
- **Descripción:** Crear endpoint REST /api/crm/payments con GET y POST
- **Fecha creación:** 2026-05-16

#### 4. [v2-backend-interaction-repository](0-backlog/v2-backend-interaction-repository.md)
- **Descripción:** Implementar InteractionRepository: registrar timeline de interacciones con clientes
- **Fecha creación:** 2026-05-16

#### 5. [v2-backend-interaction-endpoint](0-backlog/v2-backend-interaction-endpoint.md)
- **Descripción:** Crear endpoint REST /api/crm/interactions para el timeline
- **Fecha creación:** 2026-05-16

#### 6. [v2-frontend-dashboard-page](0-backlog/v2-frontend-dashboard-page.md)
- **Descripción:** Crear página de dashboard con métricas principales de cobranza
- **Fecha creación:** 2026-05-16

---

## 🟢 MEDIA

### 📋 Backlog

#### 1. [v2-frontend-customer-list](0-backlog/v2-frontend-customer-list.md)
- **Descripción:** Crear lista de clientes con filtros, paginación y acciones rápidas
- **Fecha creación:** 2026-05-16

#### 2. [v2-frontend-customer-detail](0-backlog/v2-frontend-customer-detail.md)
- **Descripción:** Crear panel de detalle de cliente con timeline, acciones y formulario rápido
- **Fecha creación:** 2026-05-16

#### 3. [v2-frontend-queue-page](0-backlog/v2-frontend-queue-page.md)
- **Descripción:** Crear página de cola de gestión con filtros y vista de expediente
- **Fecha creación:** 2026-05-16

#### 4. [v2-frontend-promise-form](0-backlog/v2-frontend-promise-form.md)
- **Descripción:** Crear formulario para registrar promesa de pago
- **Fecha creación:** 2026-05-16

#### 5. [v2-frontend-payment-form](0-backlog/v2-frontend-payment-form.md)
- **Descripción:** Crear formulario para registrar pago realizado
- **Fecha creación:** 2026-05-16

#### 6. [v2-backend-campaign-repository](0-backlog/v2-backend-campaign-repository.md)
- **Descripción:** Implementar CampaignRepository: CRUD de campañas de cobranza
- **Fecha creación:** 2026-05-16

#### 7. [v2-backend-campaign-endpoint](0-backlog/v2-backend-campaign-endpoint.md)
- **Descripción:** Crear endpoint REST /api/crm/campaigns
- **Fecha creación:** 2026-05-16

#### 8. [v2-frontend-campaign-list](0-backlog/v2-frontend-campaign-list.md)
- **Descripción:** Crear lista de campañas con métricas de envío
- **Fecha creación:** 2026-05-16

#### 9. [v2-backend-settings-repository](0-backlog/v2-backend-settings-repository.md)
- **Descripción:** Implementar SettingsRepository: parámetros de cartera por empresa
- **Fecha creación:** 2026-05-16

#### 10. [v2-backend-settings-endpoint](0-backlog/v2-backend-settings-endpoint.md)
- **Descripción:** Crear endpoint GET/PUT /api/crm/settings
- **Fecha creación:** 2026-05-16

#### 11. [v2-frontend-settings-page](0-backlog/v2-frontend-settings-page.md)
- **Descripción:** Crear página de configuración de parámetros de cartera
- **Fecha creación:** 2026-05-16

#### 12. [v2-backend-portfolio-repository](0-backlog/v2-backend-portfolio-repository.md)
- **Descripción:** Implementar PortfolioRepository: gestionar carteras y asignación de usuarios
- **Fecha creación:** 2026-05-16

#### 13. [v2-backend-portfolio-endpoint](0-backlog/v2-backend-portfolio-endpoint.md)
- **Descripción:** Crear endpoint REST /api/crm/portfolios
- **Fecha creación:** 2026-05-16

#### 14. [v2-frontend-portfolio-admin](0-backlog/v2-frontend-portfolio-admin.md)
- **Descripción:** Crear página de administración de carteras y asignación de usuarios
- **Fecha creación:** 2026-05-16

#### 15. [v2-frontend-users-admin](0-backlog/v2-frontend-users-admin.md)
- **Descripción:** Crear página de administración de usuarios del tenant
- **Fecha creación:** 2026-05-16

#### 16. [v2-docker-backend-dockerfile](0-backlog/v2-docker-backend-dockerfile.md)
- **Descripción:** Crear Dockerfile multi-stage para el backend FastAPI
- **Fecha creación:** 2026-05-16

#### 17. [v2-docker-frontend-dockerfile](0-backlog/v2-docker-frontend-dockerfile.md)
- **Descripción:** Crear Dockerfile para build y serve del frontend React
- **Fecha creación:** 2026-05-16

---

## 🔵 BAJA

### 📋 Backlog

#### 1. [v2-docker-compose-completo](0-backlog/v2-docker-compose-completo.md)
- **Descripción:** Completar docker-compose.yml con todos los servicios: backend, frontend, postgres, redis, nginx
- **Fecha creación:** 2026-05-16

#### 2. [migracion-v1-a-v2-plan-concreto](0-backlog/migracion-v1-a-v2-plan-concreto.md)
- **Descripción:** Crear plan detallado de migración módulo por módulo de V1 a V2, con dependencias, riesgos y estrategia de conivencia
- **Fecha creación:** 2026-05-16

#### 3. [suite-tests-v1-v2](0-backlog/suite-tests-v1-v2.md)
- **Descripción:** Implementar suite de tests para garantizar calidad en la migración: unit tests para backend V2, integration tests para APIs, y tests de regresión para V1
- **Fecha creación:** 2026-05-16

#### 4. [v2-backend-tenants-admin](0-backlog/v2-backend-tenants-admin.md)
- **Descripción:** Implementar panel de administración de tenants (empresas) para platform_admin
- **Fecha creación:** 2026-05-16

---

*Última actualización: 2026-05-16*