# Feature: alembic-migrations-v2

## Criticidad
- [ ] 🔴 Crítica
- [x] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Configurar y escribir migraciones Alembic para todos los modelos SQLAlchemy de V2

## Tipo
- [ ] Frontend
- [x] Backend
- [ ] Infraestructura

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como equipo de desarrollo, necesitamos migraciones versionadas para poder desplegar cambios de schema de forma controlada.

---

## Criterios de Aceptación
- [ ] Alembic inicializado y configurado
- [ ] Migración inicial con todos los modelos
- [ ] Scripts de seed para desarrollo
- [ ] Documentación de commands de migración

---

## Tasks
- [ ] Inicializar alembic: alembic init
- [ ] Configurar alembic.ini con connection string
- [ ] Crear env.py con SQLAlchemy engine
- [ ] Generar migración inicial: alembic revision --autogenerate
- [ ] Crear script de seed_data.py
- [ ] Documentar comandos: upgrade, downgrade, seed

---

## Notas Técnicas
Modelos existentes en v2/backend/app/models/
- identity.py: User, Company
- crm.py: Customer, Promise, Payment, Campaign, Interaction
- tenant.py: TenantRelated models

El server.py de V1 tiene el schema completo - usar como referencia para los modelos SQLAlchemy.