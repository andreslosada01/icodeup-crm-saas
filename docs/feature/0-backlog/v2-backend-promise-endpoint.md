# Feature: v2-backend-promise-endpoint

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear endpoint REST /api/crm/promises con GET y POST

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
Como frontend, necesito endpoints para gestionar promesas de pago.

---

## Criterios de Aceptación
- [ ] GET /api/crm/promises - lista con filtros
- [ ] GET /api/crm/promises/{id} - detalle
- [ ] POST /api/crm/promises - crear promesa
- [ ] PATCH /api/crm/promises/{id}/complete - marcar cumplida
- [ ] Pydantic schemas
- [ ] Tests de integración

---

## Tasks
- [ ] Crear schemas/promise.py
- [ ] GET /api/crm/promises con filtros: customer_id, status, from_date, to_date
- [ ] GET /api/crm/promises/{id}
- [ ] POST /api/crm/promises
- [ ] PATCH /{id}/complete
- [ ] Integrar con PromiseRepository
- [ ] Escribir tests

---

## Notas Técnicas
Al crear una promesa, también actualizar el status del customer a "Promesa".
Ver app.js líneas 731-748 para la lógica de crear promesa en frontend.