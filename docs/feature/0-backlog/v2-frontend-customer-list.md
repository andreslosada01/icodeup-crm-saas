# Feature: v2-frontend-customer-list

## Criticidad
- [ ] 🔴 Crítica
- [ ] 🟡 Alta
- [x] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear lista de clientes con filtros, paginación y acciones rápidas

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
Como gestor, quiero ver mi lista de clientes con filtros para encontrar casos rápidamente.

---

## Criterios de Aceptación
- [ ] Tabla con columnas: Nombre, Documento, Saldo, DPD, Estado, Agente
- [ ] Filtros: búsqueda por nombre/documento, estado, agente, segmento
- [ ] Paginación (10, 25, 50 por página)
- [ ] Click en fila abre detalle del cliente
- [ ] Indicador visual de riesgo (color por nivel)
- [ ] Loading y empty states

---

## Tasks
- [ ] Crear pages/CustomerListPage.tsx
- [ ] Crear components/customers/CustomerTable.tsx
- [ ] Crear components/customers/CustomerFilters.tsx
- [ ] Implementar fetching con filtros
- [ ] Implementar paginación
- [ ] Crear CustomerDetailPanel (sidebar o modal)
- [ ] Estilar con Tailwind
- [ ] Probar con API real

---

## Notas Técnicas
Ver app.js líneas 1200+ para la tabla de customers en V1.
La tabla de V1 incluye: nombre, documento, saldo, dpd, status, priority, contactability, agente, próxima acción.