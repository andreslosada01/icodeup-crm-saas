# Feature: v2-backend-payment-endpoint

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear endpoint REST /api/crm/payments con GET y POST

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
Como frontend, necesito endpoints para gestionar pagos.

---

## Criterios de Aceptación
- [ ] GET /api/crm/payments - lista con pagination
- [ ] GET /api/crm/payments/{id} - detalle
- [ ] POST /api/crm/payments - registrar pago
- [ ] Al registrar pago: actualizar balance del customer
- [ ] Al registrar pago: marcar promesas cumplidas si corresponde
- [ ] Pydantic schemas
- [ ] Tests de integración

---

## Tasks
- [ ] Crear schemas/payment.py
- [ ] GET /api/crm/payments con pagination y filtros
- [ ] GET /api/crm/payments/{id}
- [ ] POST /api/crm/payments - crear pago
- [ ] Lógica de actualizar customer balance
- [ ] Lógica de marcar promesas cumplidas
- [ ] Escribir tests

---

## Notas Técnicas
Ver app.js líneas 750-778 para lógica completa de registrar pago.
El pago debe:
1. Crear el registro en payments
2. Actualizar balance del customer
3. Si balance = 0, cambiar status a "Contactado"
4. Marcar promesas como cumplidas si el monto las cubre