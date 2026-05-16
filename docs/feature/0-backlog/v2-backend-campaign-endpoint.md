# Feature: v2-backend-campaign-endpoint

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear endpoint REST /api/crm/campaigns

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
Como frontend, necesito gestionar campañas de cobranza.

---

## Criterios de Aceptación
- [ ] GET /api/crm/campaigns
- [ ] GET /api/crm/campaigns/{id}
- [ ] POST /api/crm/campaigns
- [ ] Pydantic schemas
- [ ] Tests

---

## Tasks
- [ ] Crear schemas/campaign.py
- [ ] CRUD endpoints
- [ ] Integrar con CampaignRepository
- [ ] Escribir tests

---

## Notas Técnicas
Al crear campaña, se cuentan los clientes del segmento para setear "sent".