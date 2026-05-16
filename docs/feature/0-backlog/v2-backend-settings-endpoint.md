# Feature: v2-backend-settings-endpoint

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear endpoint GET/PUT /api/crm/settings

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
Como frontend, necesito leer y actualizar la configuración de la empresa.

---

## Criterios de Aceptación
- [ ] GET /api/crm/settings
- [ ] PUT /api/crm/settings
- [ ] Pydantic schemas
- [ ] Tests

---

## Tasks
- [ ] Crear schemas/settings.py
- [ ] GET /api/crm/settings
- [ ] PUT /api/crm/settings
- [ ] Integrar con SettingsRepository
- [ ] Escribir tests

---

## Notas Técnicas
Solo admins y superadmins pueden modificar settings.