# Feature: v2-backend-settings-repository

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Implementar SettingsRepository: parámetros de cartera por empresa

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
Como sistema, necesito guardar los parámetros de configuración por empresa.

---

## Criterios de Aceptación
- [ ] SettingsRepository.get(company_id)
- [ ] update(company_id, settings)
- [ ] Settings: monthly_goal, promise_alert_days, critical_dpd
- [ ] Tests

---

## Tasks
- [ ] Crear repositories/settings_repository.py
- [ ] get(company_id)
- [ ] update(company_id, data)
- [ ] Validación de rangos
- [ ] Escribir tests

---

## Notas Técnicas
Ver server.py líneas 171-176 para la tabla settings.
Parámetros: monthly_goal (COP), promise_alert_days (int), critical_dpd (días)