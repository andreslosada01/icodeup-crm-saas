# Feature: v2-backend-customer-service

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar CustomerService con lógica de negocio: scoring, risk calculation, status transitions

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
Como sistema, necesito un servicio que maneje la lógica de negocio de customers: scoring, riesgos y transiciones de estado.

---

## Criterios de Aceptación
- [ ] CustomerService.calculate_priority(dpd, balance, risk, status)
- [ ] CustomerService.calculate_risk(dpd, balance) -> Bajo/Medio/Alto
- [ ] CustomerService.update_status(customer_id, new_status)
- [ ] Transiciones válidas de estado
- [ ] Logs de auditoría para cambios
- [ ] Tests para cada método

---

## Tasks
- [ ] Crear services/customer_service.py
- [ ] Implementar calculate_risk() según DPD y balance
- [ ] Implementar calculate_priority() con fórmula de V1
- [ ] Implementar status_transitions permitidas
- [ ] Implementar update_status() con validación
- [ ] Agregar logging de cambios
- [ ] Escribir tests para cada método

---

## Notas Técnicas
Ver app.js líneas 1200+ para funciones como riskFromDpd(), scoreCustomer().
Fórmula de riesgo V1:
- dpd > 90 o balance > 50M -> Alto
- dpd > 60 o balance > 20M -> Medio  
- Sino -> Bajo

Fórmula priority: combinación de DPD, balance y contactability.