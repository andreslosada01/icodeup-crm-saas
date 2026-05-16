# Feature: v2-backend-interaction-endpoint

## Criticidad
- [ ] 🔴 Crítica
- [x] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear endpoint REST /api/crm/interactions para el timeline

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
Como frontend, necesito guardar y leer las interacciones con clientes.

---

## Criterios de Aceptación
- [ ] GET /api/crm/interactions?customer_id=xxx
- [ ] POST /api/crm/interactions
- [ ] Pydantic schemas
- [ ] Tests de integración

---

## Tasks
- [ ] Crear schemas/interaction.py
- [ ] GET / con filtro customer_id
- [ ] POST / para crear interacción
- [ ] Integrar con InteractionRepository
- [ ] Escribir tests

---

## Notas Técnicas
Cada interacción registra: tipo, nota, agente, canal, fecha.
El timeline del customer se construye leyendo las interacciones.