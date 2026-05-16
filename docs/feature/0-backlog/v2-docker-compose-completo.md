# Feature: v2-docker-compose-completo

## Criticidad
- [ ] 🔴 Crítica
- [x] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Completar docker-compose.yml con todos los servicios: backend, frontend, postgres, redis, nginx

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
Como DevOps, quiero levantar todo el entorno con un solo docker-compose up.

---

## Criterios de Aceptación
- [ ] Servicio postgres (datos persistidos)
- [ ] Servicio redis (para cache/sessions)
- [ ] Servicio backend (build desde Dockerfile)
- [ ] Servicio frontend (build desde Dockerfile)
- [ ] Servicio nginx (reverse proxy en puerto 80)
- [ ] Networks y volumes configurados
- [ ] Health checks en servicios
- [ ] Puertos: 80 (nginx), 5432 (postgres), 6379 (redis)

---

## Tasks
- [ ] Actualizar v2/infra/docker-compose.yml
- [ ] Agregar servicio backend con depends_on postgres, redis
- [ ] Agregar servicio frontend
- [ ] Agregar servicio nginx
- [ ] Configurar networks: backend_network, frontend_network
- [ ] Configurar volumes para persistencia
- [ ] Probar docker-compose up -d
- [ ] Verificar que todo levanta y funciona

---

## Notas Técnicas
El orden de startup: postgres -> redis -> backend -> frontend -> nginx.
El backend necesita DATABASE_URL y REDIS_URL del entorno.
Nginx proxy: /api/* -> backend:8020, /* -> frontend:3000