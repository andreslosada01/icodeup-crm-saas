# Feature: v2-backend-configurar-pytest

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Configurar pytest con fixtures, async support y coverage en el backend V2

## Tipo
- [ ] Frontend
- [x] Backend
- [ ] Ambos

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como desarrollador, quiero una suite de tests configurada para poder escribir tests y validar el código.

---

## Criterios de Aceptación
- [ ] pytest instalado y configurado en pyproject.toml
- [ ] pytest-asyncio para tests async
- [ ] Fixtures para db session, client, auth
- [ ] Estructura de tests/ organizada
- [ ] conftest.py con fixtures base
- [ ] Primer test passing (ej: test_health_endpoint)

---

## Tasks
- [ ] Agregar pytest, pytest-asyncio, pytest-cov a pyproject.toml
- [ ] Crear tests/__init__.py
- [ ] Crear tests/conftest.py con fixtures
- [ ] Crear fixtures: db_session, client, auth_headers
- [ ] Crear tests/test_health.py con test básico
- [ ] Verificar que pytest corre y pasa
- [ ] Configurar coverage en pyproject.toml

---

## Notas Técnicas
El backend usa SQLAlchemy con SessionLocal.
Los tests deben poder correr sin necesidad de PostgreSQL real - usar una DB en memoria o mock.