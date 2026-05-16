# Feature: v2-backend-payment-repository

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar PaymentRepository: CRUD de pagos registrados

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
Como sistema, necesito gestionar pagos realizados por clientes.

---

## Criterios de Aceptación
- [ ] PaymentRepository.get_by_id()
- [ ] get_by_customer(customer_id)
- [ ] get_by_company(company_id) con pagination
- [ ] create(customer_id, amount, date, method, reference)
- [ ] Tests unitarios

---

## Tasks
- [ ] Crear repositories/payment_repository.py
- [ ] Implementar PaymentRepository
- [ ] get_by_id(company_id, payment_id)
- [ ] get_by_customer(company_id, customer_id)
- [ ] get_all(company_id, pagination)
- [ ] create(data)
- [ ] Escribir tests

---

## Notas Técnicas
Ver server.py líneas 863-870 para insert_payment().
Al crear un pago, también hay que marcar promesas cumplidas si el monto las cubre.
Ver app.js líneas 768-773 para esta lógica.