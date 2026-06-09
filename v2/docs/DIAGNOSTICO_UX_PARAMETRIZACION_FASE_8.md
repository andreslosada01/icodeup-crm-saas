# Diagnostico UX, Parametrizacion y Alertas - Fase 8

## 1. Estado visual actual

Icodeup 360 ya cuenta con una experiencia SaaS corporativa: login premium, shell con sidebar/topbar, menu dinamico por rol/modulo, dashboard por experiencia y secciones administrativas para usuarios, roles, permisos, modulos, auditoria y branding. La interfaz es usable para demo comercial y separa gobierno Icodeup, administracion de empresa y operacion.

El frontend sigue siendo HTML/CSS/JavaScript monolitico servido por FastAPI. Esto permite avanzar rapido, pero exige cambios compatibles y bien acotados para no romper el flujo existente.

## 2. Brechas frente a experiencia CRM/ERP moderna

- Juridico y ventas aun se perciben como capacidades base con placeholders visuales.
- No existe un Centro de Configuracion funcional centralizado para catalogos, reglas, alertas, workflows y plantillas.
- Las alertas aparecen como analitica local en algunos paneles, pero no como motor transversal consultable.
- No hay vista operacional tipo kanban para juridico o ventas.
- Las reglas de tiempo y etapas viven mezcladas entre datos, convenciones y codigo.
- Faltan componentes reutilizables para timeline, workflow, alert center y configuracion funcional.

## 3. Modulos que aun se ven como MVP

- Juridico: tiene casos, actuaciones, audiencias y vencimientos, pero faltan avance procesal, timeline, kanban y tablero juridico.
- Ventas: tiene leads y oportunidades, pero faltan pipeline, tablero comercial y kanban.
- Documentos: existe como metadata, pero sin bandeja visual avanzada ni validacion documental.
- Configuracion: existe tenant branding/settings y tipificaciones, pero no una consola funcional unificada.

## 4. Elementos que deben volverse configurables

- Estados de cliente, riesgo, prioridad y contactabilidad.
- Tipos y resultados de gestion.
- Motivos de no pago y cierre.
- Tipos documentales.
- Tipos de proceso juridico, etapas procesales, actuaciones y audiencias.
- Etapas de lead, oportunidad y pipeline.
- Umbrales de alertas por modulo, riesgo, etapa y dias.
- Transiciones de workflow y restricciones por rol.
- Plantillas de mensajes, observaciones y alertas.

## 5. Catalogos actuales

- Tipificaciones de cobranza por tenant/proyecto.
- Roles, permisos y modulos.
- Tenants, proyectos, usuarios y branding.
- Planes, suscripciones y modulos SaaS.
- Algunos estados operativos en modelos: clientes, promesas, pagos, acuerdos, casos, documentos, leads y oportunidades.

## 6. Catalogos faltantes

- Catalogo funcional generico por modulo y tipo.
- Catalogo de reglas de negocio.
- Catalogo de alertas configurables.
- Catalogo de workflows, etapas y transiciones.
- Catalogo de plantillas funcionales.

## 7. Reglas actuales quemadas en codigo

- Permisos fallback por rol legacy.
- Etapas juridicas sugeridas y de ventas sugeridas.
- Umbrales visuales de alertas en paneles.
- Visibilidad por audiencia del menu, aunque ya se alimenta desde base.
- Algunas condiciones de asignacion para abogado, comercial y gestor.

## 8. Reglas que deben pasar a parametrizacion

- Dias maximos sin gestion.
- Dias de alerta para promesas, audiencias y vencimientos juridicos.
- Dias de estancamiento comercial.
- Reglas por riesgo, prioridad, etapa y tipo de proceso.
- Flujo de etapas juridicas y comerciales.
- Mensajes de alertas y destinatarios por rol.

## 9. Alertas actuales

Existen alertas visuales derivadas en dashboards, BI y algunos paneles operativos. No hay todavia endpoint transversal unico ni reglas administrables por tenant.

## 10. Alertas faltantes

- Cliente sin gestion.
- Promesa vencida o proxima a vencer.
- Cuota de acuerdo vencida.
- Caso juridico sin actuacion.
- Vencimiento juridico vencido/proximo.
- Audiencia proxima.
- Lead sin seguimiento.
- Oportunidad estancada o proxima a cierre.
- Tenant sin plan, modulo activo sin usuarios, limite de plan cercano y data demo activa.

## 11. Brechas del modulo juridico

- Falta endpoint de dashboard juridico.
- Falta timeline del expediente.
- Falta progreso procesal calculado.
- Falta kanban por etapa.
- Falta usar configuracion como fuente de etapas.
- Falta vista visual operacional real en frontend.

## 12. Brechas del modulo ventas

- Falta endpoint de dashboard comercial.
- Falta pipeline agregable.
- Falta kanban por etapa.
- Falta alertas de seguimiento y cierre.
- Falta vista visual operacional real en frontend.

## 13. Recomendacion de implementacion progresiva

Implementar Fase 8 con un nucleo compatible:

1. Crear modelos genericos de catalogos, reglas, alertas y workflows con `tenant_id` nullable para defaults globales.
2. Agregar endpoints `/api/configuration`, `/api/alerts`, `/api/legal/dashboard|timeline|progress|kanban` y `/api/sales/dashboard|pipeline|kanban`.
3. Sembrar permisos y menu de forma idempotente.
4. Mantener defaults si no hay configuracion tenant.
5. Conectar frontend con vistas compactas sin reescribir el shell.
6. Documentar persistencia futura de alertas si se decide no depender solo de calculo dinamico.
