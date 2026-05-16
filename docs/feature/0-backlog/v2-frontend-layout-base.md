# Feature: v2-frontend-layout-base

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear layout base del CRM: sidebar de navegación, header con usuario, área de contenido

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
Como usuario, quiero ver la estructura base del CRM con navegación para poder orientarme.

---

## Criterios de Aceptación
- [ ] Layout con sidebar izquierdo
- [ ] Header con logo, título y usuario
- [ ] Área de contenido principal
- [ ] Navegación funcional (links a las rutas)
- [ ] Responsive (sidebar colapsable en mobile)
- [ ] Indicador de carga en content area

---

## Tasks
- [ ] Crear components/layout/Layout.tsx
- [ ] Crear components/layout/Sidebar.tsx con nav items
- [ ] Crear components/layout/Header.tsx con user info
- [ ] Crear components/layout/Content.tsx
- [ ] Integrar con React Router
- [ ] Estilar con Tailwind
- [ ] Implementar collapse en mobile

---

## Notas Técnicas
Usar componentes funcionales con TypeScript.
Ver indices de navegación en app.js líneas 582-730 para los items de menú.
Segmentos: dashboard, queue, customers, promises, payments, campaigns, settings, users, tenants (platform)