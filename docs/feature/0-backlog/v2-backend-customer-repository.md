# Feature: v2-backend-customer-repository

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar CustomerRepository con operaciones CRUD y filtros

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
Como desarrollador, necesito un repositorio de customers para poder acceder a los datos de clientes.

---

## Criterios de Aceptación
- [ ] CustomerRepository con get_by_id()
- [ ] get_all() con pagination
- [ ] create() con validación
- [ ] update() con patch parcial
- [ ] delete() (soft delete o hard)
- [ ] filtros: by_agent, by_status, by_segment, by_dpd
- [ ] Tests unitarios

---

## Tasks
- [ ] Crear repositories/customer_repository.py
- [ ] Implementar CustomerRepository class
- [ ] get_by_id(company_id, customer_id)
- [ ] get_all(company_id, filters, pagination)
- [ ] create(company_id, data)
- [ ] update(company_id, customer_id, data)
- [ ] delete(company_id, customer_id)
- [ ] Métodos de filtro privados
- [ ] Escribir tests

---

## Notas Técnicas
El modelo Customer está en v2/backend/app/models/crm.py
Ver server.py de V1 líneas 804-841 para insert_customer().
Ver build_state() líneas 924-973 para estructura del customer.