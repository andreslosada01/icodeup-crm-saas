# Feature: v2-backend-customer-endpoint

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear endpoint REST /api/crm/customers con GET, POST, PUT, DELETE

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
Como frontend, necesito endpoints REST para gestionar customers.

---

## Criterios de Aceptación
- [ ] GET /api/crm/customers - lista con pagination y filtros
- [ ] GET /api/crm/customers/{id} - detalle de customer
- [ ] POST /api/crm/customers - crear customer
- [ ] PUT /api/crm/customers/{id} - actualizar customer
- [ ] DELETE /api/crm/customers/{id} - eliminar customer
- [ ] Pydantic schemas para request/response
- [ ] Validación de datos de entrada
- [ ] Tests de integración

---

## Tasks
- [ ] Crear schemas/customer.py con CustomerCreate, CustomerUpdate, CustomerResponse
- [ ] Crear route en api/routes/crm.py
- [ ] GET / (list) con query params: page, limit, agent, status, segment
- [ ] GET /{id}
- [ ] POST / con validación
- [ ] PUT /{id}
- [ ] DELETE /{id}
- [ ] Integrar con CustomerService
- [ ] Escribir tests de integración

---

## Notas Técnicas
Verificar que el router use el prefijo /api/crm ya configurado.
Verificar que el endpoint de V1 server.py para entender los filtros disponibles.