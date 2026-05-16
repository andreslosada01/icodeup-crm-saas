# Feature: v2-frontend-users-admin

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear página de administración de usuarios del tenant

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
Como administrador, quiero gestionar usuarios de mi empresa.

---

## Criterios de Aceptación
- [ ] Lista de usuarios: nombre, email, rol, estado
- [ ] Crear usuario (modal con name, email, role, password)
- [ ] Editar usuario
- [ ] Activar/desactivar usuario
- [ ] Asignar líder a agente

---

## Tasks
- [ ] Crear pages/UsersPage.tsx
- [ ] UserTable component
- [ ] UserForm modal (crear/editar)
- [ ] GET /api/admin/users
- [ ] POST /api/admin/users
- [ ] PUT /api/admin/users/{id}
- [ ] Estilar con Tailwind

---

## Notas Técnicas
Ver app.js para la UI de usuarios en V1.
Roles: superadmin, admin, coordinator, agent, quality