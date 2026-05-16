# Feature: v2-frontend-login-page

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear página de login funcional que se conecte al backend V2

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
Como usuario, quiero hacer login con email y password para acceder al CRM.

---

## Criterios de Aceptación
- [ ] Formulario con email y password
- [ ] Validación de inputs (email requerido, password min 6 chars)
- [ ] Llamada a /api/auth/login
- [ ] Al éxito: guardar token, redireccionar a dashboard
- [ ] Al error: mostrar mensaje de error
- [ ] Estado de loading durante el request
- [ ] Recordar empresa (company selector si aplica)

---

## Tasks
- [ ] Crear pages/LoginPage.tsx
- [ ] Implementar form con react-hook-form o useState
- [ ] Conectar con auth store y API client
- [ ] Manejar errores 401, 500, network error
- [ ] Agregar estado de loading
- [ ] Estilar con Tailwind (diseño limpio, profesional)
- [ ] Probar login funcional

---

## Notas Técnicas
El backend ya tiene /api/auth/login implementado.
Revisar auth service de V2: v2/backend/app/services/auth_service.py
V1 usa selector de empresa en login - ver si es necesario en V2.