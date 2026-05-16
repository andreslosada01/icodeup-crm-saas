# Feature: v2-frontend-auth-flow

## Criticidad
- [ ] 🔴 Crítica
- [x] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar flow completo de autenticación: login, logout, refresh token, manejo de sesiones, protected routes

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
Como usuario, quiero hacer login y que el sistema recuerde mi sesión de forma segura.

---

## Criterios de Aceptación
- [ ] Login funcional con email/password
- [ ] JWT almacenado en httpOnly cookie o localStorage seguro
- [ ] Logout limpia sesión
- [ ] Token refresh automático
- [ ] Protected routes redirigen a login
- [ ] Roles verificados en frontend y backend

---

## Tasks
- [ ] Crear AuthContext/Zustand store para auth
- [ ] Implementar API client con interceptor de tokens
- [ ] Crear LoginPage con validación
- [ ] Implementar refresh token logic
- [ ] Crear HOC/hook para protected routes
- [ ] Implementar logout global

---

## Notas Técnicas
El backend ya tiene /api/auth/login. Verificar que devuelva JWT.
V1 usa sesiones con cookies - V2 debe usar JWT.
Ver v2/backend/app/api/routes/auth.py para endpoints existentes.