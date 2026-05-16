# Feature: v2-docker-backend-dockerfile

## Criticidad
- [ ] 🔴 Crítica
- [x] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear Dockerfile multi-stage para el backend FastAPI

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
Como DevOps, quiero un Dockerfile para poder containerizar el backend.

---

## Criterios de Aceptación
- [ ] Dockerfile multi-stage (build -> runtime)
- [ ] Usar python:3.12-slim
- [ ] Instalar dependencias desde pyproject.toml
- [ ] Exponer puerto 8020
- [ ] CMD correcto para uvicorn
- [ ] .dockerignore configurado
- [ ] Build exitoso

---

## Tasks
- [ ] Crear v2/backend/Dockerfile
- [ ] Stage 1: build con pyproject.toml
- [ ] Stage 2: runtime slim
- [ ] Crear .dockerignore
- [ ] Probar build local: docker build -t icodeup-backend .
- [ ] Probar run: docker run -p 8020:8020 icodeup-backend

---

## Notas Técnicas
El backend usa uvicorn como servidor.
La imagen final debe tener las dependencias de producción, no de desarrollo.
Configurar para leer DATABASE_URL del entorno.