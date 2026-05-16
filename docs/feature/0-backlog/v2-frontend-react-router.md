# Feature: v2-frontend-react-router

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Configurar React Router v6 con lazy loading y route base para el CRM

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
Como desarrollador, quiero routing funcional para poder navegar entre las distintas vistas del CRM.

---

## Criterios de Aceptación
- [ ] React Router v6 instalado
- [ ] Routes básicas: /, /login, /dashboard, /customers, /queue
- [ ] Lazy loading configurado para cada route
- [ ] 404 handling configurado
- [ ] Links funcionan correctamente

---

## Tasks
- [ ] Instalar react-router-dom
- [ ] Crear estructura de routes
- [ ] Implementar lazy loading con Suspense
- [ ] Crear page components placeholder
- [ ] Configurar 404 route
- [ ] Probar navegación

---

## Notas Técnicas
Usar React.lazy() y Suspense para code splitting.
Definir las rutas según los módulos de V1: dashboard, queue, customers, promises, payments, campaigns, settings, users, tenants