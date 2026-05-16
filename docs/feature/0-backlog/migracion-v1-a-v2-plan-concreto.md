# Feature: migracion-v1-a-v2-plan-concreto

## Criticidad
- [x] 🔴 Crítica
- [ ] 🟡 Alta
- [ ] 🟢 Media
- [ ] 🔵 Baja

## Descripción
Crear plan detallado de migración módulo por módulo de V1 a V2, con dependencias, riesgos y estrategia de conivencia

## Tipo
- [ ] Frontend
- [ ] Backend
- [x] Proceso

## Estado
- [ ] Backlog
- [ ] WIP
- [ ] Done

---

## User Story
Como equipo de desarrollo, necesitamos un mapa de migración claro que defina qué se mueve primero, qué depende de qué, y cómo mantenemos V1 operativa hasta que V2 esté lista.

---

## Criterios de Aceptación
- [ ] Documento de migración con fases claras
- [ ] Cada módulo de V1 mapeado a componente V2
- [ ] Definidas las dependencias entre módulos
- [ ] Estrategia de rollback definida
- [ ] Criterios de "V2 listo para producción"

---

## Tasks
- [ ] Inventariar todos los módulos de app.js (4000 líneas)
- [ ] Mapear cada módulo a la estructura V2
- [ ] Definir fases de migración
- [ ] Crear criterios de aceptación por fase
- [ ] Documentar estrategia de conivencia (V1 + V2 en paralelo)

---

## Notas Técnicas
app.js tiene ~4000 líneas con:
- Constantes y configuración global
- Estado default con datos demo
- Inicialización y elementos DOM
- Login y autenticación
- Navegación y vistas
- Formularios múltiples
- Renderizado de todas las vistas
- Lógica de negocio compleja
- Event listeners

El plan debe considerar:
1. V1 sigue funcionando durante migración
2. V2 consume los mismos datos (migración gradual)
3. Alternativa: paralelo total (V1 legacy, V2 nuevo)