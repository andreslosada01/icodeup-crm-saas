# Feature: v2-frontend-promise-form

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear formulario para registrar promesa de pago

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
Como gestor, quiero registrar una promesa de pago de un cliente.

---

## Criterios de Aceptación
- [ ] Selector de cliente (buscable)
- [ ] Campo de monto (COP, formateado)
- [ ] Campo de fecha (date picker)
- [ ] Selector de canal (WhatsApp, Teléfono, Email)
- [ ] Validación: monto > 0, fecha futura o hoy
- [ ] Al crear: mostrar toast de éxito
- [ ] Al crear: cerrar modal y refresh lista

---

## Tasks
- [ ] Crear components/promises/PromiseForm.tsx
- [ ] Implementar selector de cliente con search
- [ ] Implementar campo de monto con formato COP
- [ ] Implementar date picker
- [ ] Implementar selector de canal
- [ ] Validación del formulario
- [ ] POST a /api/crm/promises
- [ ] Estilar con Tailwind

---

## Notas Técnicas
Ver app.js líneas 731-748 para el formulario de promesa en V1.
Al crear una promesa, el status del customer cambia a "Promesa".