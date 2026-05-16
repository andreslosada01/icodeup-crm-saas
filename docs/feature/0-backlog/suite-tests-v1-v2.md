# Feature: suite-tests-v1-v2

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar suite de tests para garantizar calidad en la migración: unit tests para backend V2, integration tests para APIs, y tests de regresión para V1

## Tipo
- [ ] Frontend
- [ ] Backend
- [x] Ambos

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como equipo de desarrollo, necesitamos tests para poder refactorizar y migrar sin romper funcionalidad existente.

---

## Criterios de Aceptación
- [ ] pytest configurado en backend
- [ ] Tests para auth endpoints
- [ ] Tests para CRM endpoints
- [ ] Cobertura > 70% en backend
- [ ] GitHub Actions CI pipeline con tests

---

## Tasks
- [ ] Configurar pytest + fixtures
- [ ] Escribir tests para auth service
- [ ] Escribir tests para customer service
- [ ] Escribir tests para promise service
- [ ] Configurar GitHub Actions
- [ ] Añadir test job al CI

---

## Notas Técnicas
Backend V2: pytest + pytest-asyncio
Frontend V2: Vitest + React Testing Library
CI: GitHub Actions con test, lint, build jobs