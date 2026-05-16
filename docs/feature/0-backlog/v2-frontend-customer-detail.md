# Feature: v2-frontend-customer-detail

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear panel de detalle de cliente con timeline, acciones y formulario rápido

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
Como gestor, quiero ver el detalle de un cliente para gestionar su caso.

---

## Criterios de Aceptación
- [ ] Info del cliente: nombre, documento, contacto, segmento, saldo, DPD
- [ ] Timeline de interacciones
- [ ] Botones de acción: llamar, WhatsApp, email
- [ ] Formulario rápido para registrar interacción
- [ ] Sección de promesas y pagos del cliente
- [ ] Tags y notas

---

## Tasks
- [ ] Crear components/customers/CustomerDetailPanel.tsx
- [ ] Mostrar datos básicos del cliente
- [ ] Renderizar timeline de interacciones
- [ ] Implementar botones de acción (tel:, wa.me, mailto:)
- [ ] Crear QuickInteractionForm
- [ ] Mostrar promesas del cliente
- [ ] Mostrar pagos del cliente
- [ ] Estilar con Tailwind

---

## Notas Técnicas
Ver app.js para el panel de detalle en V1 (queue detail).
Los botones omnicanal usan tel:, wa.me, mailto: que son enlaces externos.