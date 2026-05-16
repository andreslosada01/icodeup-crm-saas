# Feature: v2-backend-promise-repository

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar PromiseRepository: CRUD de promesas de pago

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
Como sistema, necesito gestionar promesas de pago de clientes.

---

## Criterios de Aceptación
- [ ] PromiseRepository.get_by_id()
- [ ] get_by_customer(customer_id)
- [ ] get_by_company(company_id) con filtros
- [ ] create(customer_id, amount, date, channel)
- [ ] update_status(promise_id, new_status)
- [ ] Tests unitarios

---

## Tasks
- [ ] Crear repositories/promise_repository.py
- [ ] Implementar PromiseRepository
- [ ] get_by_id(company_id, promise_id)
- [ ] get_by_customer(company_id, customer_id)
- [ ] get_all(company_id, filters)
- [ ] create(data)
- [ ] update_status(id, status)
- [ ] Escribir tests

---

## Notas Técnicas
Ver server.py líneas 853-860 para insert_promise().
Estados: Vigente, Cumplida, Vencida, Cancelada
Estructura de promise: id, customerId, amount, date, channel, status, createdAt