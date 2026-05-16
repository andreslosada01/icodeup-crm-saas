# Feature: v2-backend-portfolio-repository

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar PortfolioRepository: gestionar carteras y asignación de usuarios

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
Como sistema, necesito gestionar carteras y sus miembros.

---

## Criterios de Aceptación
- [ ] PortfolioRepository.get_all(company_id)
- [ ] get_by_id(portfolio_id)
- [ ] create(name, code, leader_id)
- [ ] add_user(portfolio_id, user_id, role)
- [ ] remove_user(portfolio_id, user_id)
- [ ] Tests

---

## Tasks
- [ ] Crear repositories/portfolio_repository.py
- [ ] CRUD de carteras
- [ ] Gestión de miembros (portfolio_users)
- [ ] Escribir tests

---

## Notas Técnicas
Ver server.py líneas 207-225 para la tabla portfolio y portfolio_users.