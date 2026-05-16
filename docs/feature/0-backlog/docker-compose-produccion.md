# Feature: docker-compose-produccion

## Criticidad
- [ ] 🔴 Crítica
- [x] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Completar docker-compose con todos los servicios: backend, frontend (build), postgres, redis, nginx/caddy para producción local

## Tipo
- [ ] Frontend
- [ ] Backend
- [ ] Infraestructura
- [x] Todos

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como DevOps, quiero un docker-compose completo que levante todo el entorno de producción local para probar antes de deployar.

---

## Criterios de Aceptación
- [ ] Servicio backend con Dockerfile
- [ ] Servicio frontend con build Docker
- [ ] Nginx como reverse proxy
- [ ] Volumes para persistencia
- [ ] Redes definidas
- [ ] Health checks en todos los servicios

---

## Tasks
- [ ] Crear Dockerfile para backend (multi-stage build)
- [ ] Crear Dockerfile para frontend (node build)
- [ ] Configurar nginx.conf con reverse proxy
- [ ] Actualizar docker-compose con todos los servicios
- [ ] Configurar networks y volumes
- [ ] Añadir health checks
- [ ] Probar levantamiento completo

---

## Notas Técnicas
docker-compose.yml actual solo tiene postgres y redis.
Falta: backend, frontend build, nginx.
Ver v2/infra/docker-compose.yml - estado actual.