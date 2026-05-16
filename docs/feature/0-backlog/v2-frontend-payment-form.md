# Feature: v2-frontend-payment-form

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear formulario para registrar pago realizado

## Tipo
- [x] Frontend
- [ ] Backend
- [ ] Ambos

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como gestor, quiero registrar un pago realizado por un cliente.

---

## Criterios de Aceptación
- [ ] Selector de cliente (buscable)
- [ ] Campo de monto (COP)
- [ ] Campo de fecha
- [ ] Selector de método (PSE, Transferencia, Efectivo)
- [ ] Campo de referencia (opcional)
- [ ] Validación: monto > 0, cliente seleccionado
- [ ] POST a /api/crm/payments

---

## Tasks
- [ ] Crear components/payments/PaymentForm.tsx
- [ ] Selector de cliente con search
- [ ] Campo monto con formato COP
- [ ] Date picker
- [ ] Selector método (PSE, Transferencia, Efectivo, otro)
- [ ] Campo referencia
- [ ] Validación y POST
- [ ] Estilar con Tailwind

---

## Notas Técnicas
Ver app.js líneas 750-778 para el formulario de pago en V1.
Al registrar pago, también se marcan promesas como cumplidas.