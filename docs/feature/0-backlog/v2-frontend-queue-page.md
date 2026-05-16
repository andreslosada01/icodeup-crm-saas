# Feature: v2-frontend-queue-page

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear página de cola de gestión con filtros y vista de expediente

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
Como gestor, quiero mi cola de trabajo ordenada por prioridad para saber qué cliente atender.

---

## Criterios de Aceptación
- [ ] Lista de clientes asignados al agente actual
- [ ] Ordenada por priority descendente
- [ ] Filtros: estado, riesgo, DPD
- [ ] Click abre panel de detalle
- [ ] Indicador de promesas pendientes
- [ ] Badge de clientes sin contacto reciente

---

## Tasks
- [ ] Crear pages/QueuePage.tsx
- [ ] Implementar cola con filtros de V1
- [ ] Crear QueueFilters component
- [ ] Crear QueueItem component
- [ ] Integrar con customer detail panel
- [ ] Estilar con Tailwind
- [ ] Probar con datos reales

---

## Notas Técnicas
Ver app.js líneas ~1200-1500 para la cola de gestión V1.
La cola se ordena por priority y muestra promesas del día.