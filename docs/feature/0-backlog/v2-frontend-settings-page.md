# Feature: v2-frontend-settings-page

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear página de configuración de parámetros de cartera

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
Como administrador, quiero configurar los parámetros de mi cartera.

---

## Criterios de Aceptación
- [ ] Formulario con: Meta mensual (COP), Días alerta promesa, DPD crítico
- [ ] GET /api/crm/settings al cargar
- [ ] PUT /api/crm/settings al guardar
- [ ] Validación de valores
- [ ] Toast de éxito/error

---

## Tasks
- [ ] Crear pages/SettingsPage.tsx
- [ ] Implementar formulario con 3 campos
- [ ] GET settings al mount
- [ ] PUT al submit
- [ ] Validación (meta > 0, días > 0)
- [ ] Estilar con Tailwind

---

## Notas Técnicas
Ver app.js líneas 1020-1026 para el formulario de settings en V1.