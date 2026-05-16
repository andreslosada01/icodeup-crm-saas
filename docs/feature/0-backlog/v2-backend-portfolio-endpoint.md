# Feature: v2-backend-portfolio-endpoint

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear endpoint REST /api/crm/portfolios

## Tipo
- [ ] Frontend
- [x] Backend
- [ ] Ambos

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como frontend, necesito gestionar carteras.

---

## Criterios de Aceptación
- [ ] GET /api/crm/portfolios
- [ ] GET /api/crm/portfolios/{id}
- [ ] POST /api/crm/portfolios
- [ ] POST /api/crm/portfolios/{id}/users
- [ ] DELETE /api/crm/portfolios/{id}/users/{user_id}
- [ ] Pydantic schemas
- [ ] Tests

---

## Tasks
- [ ] Crear schemas/portfolio.py
- [ ] CRUD endpoints
- [ ] Gestión de usuarios del portfolio
- [ ] Integrar con PortfolioRepository
- [ ] Escribir tests

---

## Notas Técnicas
Las carteras agrupan clientes y tienen usuarios asignados (líderes y agentes).