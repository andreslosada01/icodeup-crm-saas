# Feature: v2-docker-frontend-dockerfile

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear Dockerfile para build y serve del frontend React

## Tipo
- [ ] Frontend
- [ ] Backend
- [x] Infraestructura

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como DevOps, quiero un Dockerfile para el frontend que haga build y serve estático.

---

## Criterios de Aceptación
- [ ] Multi-stage build (build -> nginx)
- [ ] Node 20 para build
- [ ] Nginx para servir archivos estáticos
- [ ] Configuración nginx.conf básica
- [ ] Build exitoso y serve funcional

---

## Tasks
- [ ] Crear v2/frontend/Dockerfile
- [ ] Stage 1: npm install + npm run build
- [ ] Stage 2: nginx:alpine con build estático
- [ ] Crear v2/frontend/nginx.conf
- [ ] .dockerignore para node_modules
- [ ] Probar build y run

---

## Notas Técnicas
El frontend usa Vite, genera archivos estáticos en dist/.
Nginx debe servir /index.html para SPA routing.