# Feature: v2-backend-crm-core-migration

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Migrar lógica CRM core (customers, promises, payments, campaigns, interactions) del server.py de V1 al backend FastAPI de V2

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
Como equipo de desarrollo, necesitamos que el backend V2 tenga toda la lógica CRM operativa para que el frontend pueda conectarse a endpoints reales.

---

## Criterios de Aceptación
- [ ] Endpoints /api/crm/customers completos (CRUD + filtros)
- [ ] Endpoints /api/crm/promises completos
- [ ] Endpoints /api/crm/payments completos
- [ ] Endpoints /api/crm/campaigns completos
- [ ] Endpoints /api/crm/interactions completos
- [ ] Tests unitarios para cada servicio

---

## Tasks
- [ ] Implementar CustomerService + CustomerRepository
- [ ] Implementar PromiseService + PromiseRepository
- [ ] Implementar PaymentService + PaymentRepository
- [ ] Implementar CampaignService + CampaignRepository
- [ ] Implementar InteractionService + InteractionRepository
- [ ] Escribir tests para cada servicio

---

## Notas Técnicas
Ver server.py líneas 800-1200 para lógica de inserción de customers, promises, payments, campaigns.
Ver server.py líneas 917-1114 para build_state() que construye el estado completo del CRM.