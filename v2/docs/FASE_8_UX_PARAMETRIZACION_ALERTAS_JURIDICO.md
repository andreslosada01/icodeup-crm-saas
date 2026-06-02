# Fase 8 - UX, Parametrizacion, Alertas, Juridico y Ventas

## 1. Resumen ejecutivo

La Fase 8 convierte Icodeup 360 en una experiencia mas cercana a un CRM/ERP SaaS moderno: agrega Centro de Configuracion funcional, motor transversal de alertas, mejoras operativas en juridico y pipeline comercial, sin rehacer el frontend ni romper modulos existentes.

## 2. Mejoras visuales

- Nueva seccion `Centro de Configuracion`.
- Nueva seccion `Alertas`.
- Juridico deja de ser placeholder y muestra KPIs, kanban procesal, agenda y tabla de expedientes.
- Ventas deja de ser placeholder y muestra KPIs, kanban comercial, pipeline y leads.
- Nuevo badge superior de alertas criticas.
- Componentes visuales agregados: `kanban-board`, `kanban-column`, `kanban-card`, `configuration-card` y `workflow-dot`.

## 3. Centro de Configuracion

Disponible para SuperAdmin Icodeup y Admin Empresa segun permisos. Permite consultar y administrar por API:

- Catalogos funcionales.
- Reglas de negocio.
- Reglas de alertas.
- Workflows y etapas.

Los registros `tenant_id = null` son plantillas globales de Icodeup. Los registros con `tenant_id` son configuraciones propias del cliente.

## 4. Catalogos configurables

Modelo: `FunctionalCatalog`.

Incluye estado de cliente, riesgo, tipos documentales, etapas juridicas, tipos de actuacion, fuentes de lead y etapas comerciales.

## 5. Reglas configurables

Modelo: `BusinessRule`.

Se prepararon reglas de SLA para clientes sin gestion, promesas, vencimientos juridicos, casos sin actuacion, leads sin seguimiento y oportunidades proximas a cierre.

## 6. Alertas configurables

Modelo: `AlertRule`.

Permite definir modulo, condicion, umbral en dias, severidad, rol objetivo y plantilla de mensaje.

## 7. Workflows configurables

Modelos:

- `WorkflowDefinition`
- `WorkflowStage`
- `WorkflowTransition`

Se sembraron flujos globales para juridico y ventas, usados por los endpoints de kanban.

## 8. Juridico avanzado

Endpoints nuevos:

- `GET /api/legal/dashboard`
- `GET /api/legal/kanban`
- `GET /api/legal/cases/{case_id}/progress`
- `GET /api/legal/cases/{case_id}/timeline`

La vista juridica ahora puede mostrar casos activos, vencimientos, audiencias, riesgos, kanban por etapa y expediente procesal.

## 9. Ventas avanzado

Endpoints nuevos:

- `GET /api/sales/dashboard`
- `GET /api/sales/pipeline`
- `GET /api/sales/kanban`

La vista comercial ahora muestra leads, oportunidades, valor de pipeline, valor ponderado, etapa y forecast base.

## 10. Endpoints nuevos

- `GET /api/configuration/catalogs`
- `POST /api/configuration/catalogs`
- `PATCH /api/configuration/catalogs/{id}`
- `GET /api/configuration/rules`
- `POST /api/configuration/rules`
- `PATCH /api/configuration/rules/{id}`
- `GET /api/configuration/alert-rules`
- `POST /api/configuration/alert-rules`
- `PATCH /api/configuration/alert-rules/{id}`
- `GET /api/configuration/workflows`
- `POST /api/configuration/workflows`
- `PATCH /api/configuration/workflows/{id}`
- `GET /api/configuration/workflows/{id}/stages`
- `POST /api/configuration/workflows/{id}/stages`
- `GET /api/alerts`
- `GET /api/alerts/summary`
- `GET /api/legal/dashboard`
- `GET /api/legal/kanban`
- `GET /api/legal/cases/{case_id}/progress`
- `GET /api/legal/cases/{case_id}/timeline`
- `GET /api/sales/dashboard`
- `GET /api/sales/pipeline`
- `GET /api/sales/kanban`

## 11. Modelos nuevos

- `FunctionalCatalog`
- `BusinessRule`
- `AlertRule`
- `WorkflowDefinition`
- `WorkflowStage`
- `WorkflowTransition`
- `GeneratedAlert`

`GeneratedAlert` queda preparado para persistencia futura. En esta fase las alertas se calculan dinamicamente desde `alert_engine.py`.

## 12. Permisos nuevos

- `configuration.view`
- `configuration.manage`
- `configuration.catalogs.manage`
- `configuration.rules.manage`
- `configuration.alerts.manage`
- `configuration.workflows.manage`
- `alerts.view`
- `alerts.manage`

## 13. Riesgos pendientes

- El frontend sigue siendo monolitico y requiere disciplina para futuras fases.
- Las alertas son calculadas dinamicamente; persistencia, resolucion y workflow de cierre quedan para fase posterior.
- El editor visual de configuracion aun es principalmente de consulta en UI; las APIs de creacion/edicion estan listas.
- Se recomienda QA visual manual despues de reiniciar el servicio local.

## 14. Recomendaciones Fase 9

- Crear formularios visuales completos para editar catalogos, reglas, alertas y workflows.
- Persistir alertas con estados `open`, `acknowledged`, `resolved`.
- Crear detalle lateral de caso juridico con timeline y acciones.
- Crear conversion comercial lead -> oportunidad -> tercero/cliente.
- Agregar pruebas visuales automatizadas por rol.
