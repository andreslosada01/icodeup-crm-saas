# Feature: v2-frontend-zustand-store

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar Zustand store para estado global: auth, ui y datos del CRM

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
Como desarrollador, quiero estado global con Zustand para manejar auth, UI y datos del CRM sin prop drilling.

---

## Criterios de Aceptación
- [ ] Auth store: user, token, login(), logout(), isAuthenticated
- [ ] CRM store: customers, promises, payments, selectedCustomer
- [ ] UI store: loading, error, activeView
- [ ] Tipos TypeScript para cada store
- [ ] Persistencia en localStorage para auth

---

## Tasks
- [ ] Instalar zustand
- [ ] Crear stores/auth.ts con estado de usuario
- [ ] Crear stores/crm.ts con datos del CRM
- [ ] Crear stores/ui.ts con estado de interfaz
- [ ] Implementar persistencia en localStorage
- [ ] Crear hook useAuth(), useCRM(), useUI()
- [ ] Tipar correctamente todo

---

## Notas Técnicas
NO usar Context API para estado global - solo Zustand.
Ver defaultState en app.js líneas 25-330 para la estructura de datos.