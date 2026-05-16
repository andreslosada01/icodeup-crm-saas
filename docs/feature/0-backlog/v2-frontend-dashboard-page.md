# Feature: v2-frontend-dashboard-page

## Criticidad
- [ ] 🔴 Crítica
- [x] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear página de dashboard con métricas principales de cobranza

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
Como gestor, quiero ver métricas clave de cobranza en mi dashboard.

---

## Criterios de Aceptación
- [ ] Tarjetas de métricas: Total cartera, Recuperación del mes, Promesas vigentes, Clientes en mora
- [ ] Gráfico de embudo de cobranza (opcional, puede ser placeholder)
- [ ] Lista de promesas para hoy
- [ ] Filtro por segmento
- [ ] Diseño responsive
- [ ] Loading states

---

## Tasks
- [ ] Crear pages/DashboardPage.tsx
- [ ] Crear components/dashboard/MetricCard.tsx
- [ ] Implementar fetching de /api/crm/state
- [ ] Mostrar métricas en cards
- [ ] Implementar lista de promesas del día
- [ ] Implementar filtro por segmento
- [ ] Estilar con Tailwind
- [ ] Probar con datos reales del backend

---

## Notas Técnicas
La data viene del endpoint /api/crm/state que devuelve todo el estado.
Ver app.js líneas ~1211-1500 para el renderizado del dashboard en V1.
Por ahora dashboard puede usar datos mock si el backend no está listo.