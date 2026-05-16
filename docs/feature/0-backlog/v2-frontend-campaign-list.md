# Feature: v2-frontend-campaign-list

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear lista de campañas con métricas de envío

## Tipo
- [x] Frontend
- [ ] Backend
- [ ] Ambos

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como administrador, quiero ver las campañas creadas y sus resultados.

---

## Criterios de Aceptación
- [ ] Lista de campañas con columnas: nombre, segmento, canal, enviados, contactados, promesas, pagos
- [ ] Indicador de rendimiento (%)
- [ ] Crear nueva campaña (abre modal)
- [ ] Ver detalle de campaña

---

## Tasks
- [ ] Crear pages/CampaignListPage.tsx
- [ ] Crear CampaignTable component
- [ ] Crear CampaignForm (nueva campaña)
- [ ] GET /api/crm/campaigns
- [ ] POST /api/crm/campaigns
- [ ] Estilar con Tailwind

---

## Notas Técnicas
Ver app.js líneas 781-799 para UI de campañas en V1.
La campaña se asocia a un segmento para contar cuántos clientes recibe.