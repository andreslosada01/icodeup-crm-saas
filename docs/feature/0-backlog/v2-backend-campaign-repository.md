# Feature: v2-backend-campaign-repository

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar CampaignRepository: CRUD de campañas de cobranza

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
Como sistema, necesito gestionar campañas de cobranza.

---

## Criterios de Aceptación
- [ ] CampaignRepository.get_all()
- [ ] get_by_id()
- [ ] create(segment, channel, template)
- [ ] update_stats(campaign_id, sent, contacted, promises, payments)
- [ ] Tests

---

## Tasks
- [ ] Crear repositories/campaign_repository.py
- [ ] Implementar CampaignRepository
- [ ] CRUD básico
- [ ] update_stats()
- [ ] Escribir tests

---

## Notas Técnicas
Ver server.py líneas 873-892 para insert_campaign().
Ver app.js líneas 781-799 para lógica de crear campaña en V1.