# Feature: v2-backend-interaction-repository

## Criticidad
- [ ] 🔴 Crítica
- [x] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar InteractionRepository: registrar timeline de interacciones con clientes

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
Como sistema, necesito guardar el historial de interacciones con cada cliente.

---

## Criterios de Aceptación
- [ ] InteractionRepository.get_by_customer()
- [ ] get_by_company() con pagination
- [ ] create(customer_id, type, note, agent, channel)
- [ ] Tests unitarios

---

## Tasks
- [ ] Crear repositories/interaction_repository.py
- [ ] get_by_customer(company_id, customer_id)
- [ ] get_all(company_id, pagination)
- [ ] create(data)
- [ ] Escribir tests

---

## Notas Técnicas
Ver server.py líneas 843-850 para insert_interaction().
Tipos de interacción: "Llamada", "WhatsApp", "Email", "Nota", "Promesa", "Pago"