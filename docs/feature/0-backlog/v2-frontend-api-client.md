# Feature: v2-frontend-api-client

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear API client con interceptor de auth, manejo de errores y tipos TypeScript

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
Como desarrollador, quiero un API client tipado que maneje auth y errores para conectar con el backend de forma consistente.

---

## Criterios de Aceptación
- [ ] API client funcional con fetch
- [ ] Tipos TypeScript para requests y responses
- [ ] Interceptor para agregar JWT en headers
- [ ] Manejo de errores centralizado
- [ ] Métodos: get, post, put, delete
- [ ] Tipos para: Customer, User, Promise, Payment, Campaign

---

## Tasks
- [ ] Crear api/client.ts con funciones get/post/put/delete
- [ ] Crear api/types.ts con interfaces tipadas
- [ ] Implementar interceptor de JWT
- [ ] Implementar manejo de errores
- [ ] Crear endpoints para /api/auth/login, /api/crm/*
- [ ] Exportar API client y tipos

---

## Notas Técnicas
El backend FastAPI usa /api/auth y /api/crm como prefix.
Ver server.py de V1 para los endpoints y estructuras de datos.