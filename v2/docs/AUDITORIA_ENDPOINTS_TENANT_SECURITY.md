# Auditoria de Endpoints y Seguridad Tenant

Fecha: 2026-06-10  
Rama auditada: `feature/deploy-test-server`

## 1. Resumen

La revision de routers confirma que los endpoints criticos usan autenticacion, permisos y filtros de tenant en la mayoria de los flujos. Se aplico una correccion menor para cerrar exceso de visibilidad interna entre lideres operativos.

Estado general: **Listo para servidor test con observaciones**.

## 2. Matriz por grupo de endpoints

| Grupo | Autenticacion | Permiso | Tenant filter | ID directo | Riesgo | Observacion |
|---|---|---|---|---|---|---|
| Auth | Parcial | N/A | N/A | N/A | Bajo | Login audita exito/fallo; no lista datos operativos. |
| Health | No | N/A | N/A | N/A | Bajo | Expone estado basico. En prod evitar detalles sensibles. |
| Menu | Si | Por permiso/modulo | Si | N/A | Bajo | `build_menu` filtra audiencia, modulo y permiso. |
| Dashboard role | Si | Permisos indirectos | Si | N/A | Bajo | Servicio diferencia platform, admin, lider, operativo, legal, sales. |
| CRM customers | Si | `crm.clients.*` | Si | Si | Bajo | `customer_query` y `customer_for_access`; se reforzo alcance de lider. |
| Obligations | Si | `crm.clients.*` | Si | Si | Bajo | `obligation_query` y `obligation_for_access`; se reforzo alcance de lider. |
| Activities | Si | `crm.activities.*` / `crm.clients.view` | Si via cliente | Si | Bajo | Acceso por `customer_for_access`; actividad hereda cliente. |
| Promises | Si | `collections.promises.*` | Si via cliente | Si | Bajo | Completar promesa valida cliente antes de actualizar. |
| Payments | Si | `collections.payments.*` | Si via cliente | Export seguro | Bajo | Export usa `customer_query`. |
| Agreements | Si | `collections.agreements.*` | Si via cliente | Si | Bajo | Cuotas se modifican despues de validar acuerdo. |
| BI CRM | Si | `reports.view` | Si | N/A | Bajo | Usa clientes visibles; no filtra proyectos global al inicio pero solo emite proyectos con clientes visibles. |
| Dashboard CRM | Si | `crm.dashboard.view` | Si | N/A | Bajo | Usa clientes visibles por `customer_query`. |
| Imports CSV legacy | Si | `crm.clients.import` | Si via proyecto | N/A | Bajo | Proyecto determina tenant; valida usuario asignado. |
| Uploads/Repartos | Si | `uploads.*` | Si | Si | Bajo | `_resolve_scope`, `_project_from_row`, `_user_from_row` validan tenant. |
| Excel Web | Si | `excel_web.*` | Si | Si | Bajo | `_apply_role_scope`, `_apply_sheet_scope` y limites de export. |
| Teams | Si | `teams.*` / `project_users.*` | Si | Si | Bajo/Medio corregido | Se cerro consulta de otros lideres sin alcance administrativo. |
| Governance roles/perms | Si | `roles.*`, `users.*`, admin | Si | Si | Bajo | `target_tenant` y permisos reservados para Icodeup. |
| Governance modules | Si | `modules.view`; cambios solo platform | Si | Si | Bajo | Admin tenant consulta; platform activa/desactiva. |
| Governance parties | Si | `parties.*` | Si | Si | Bajo | `target_tenant` bloquea tenant ajeno. |
| Governance subscriptions | Si | Platform only | Global permitido | N/A | Bajo | Inventario comercial solo Icodeup. |
| Configuration | Si | `configuration.*` | Si/global controlado | Si | Bajo | Global solo Icodeup; tenant admin su empresa. |
| Alerts | Si | `alerts.view` | Si via servicio | N/A | Bajo | Alcance por tenant/asignacion. |
| Documents | Si | `documents.*` | Si | Si | Bajo | Valida relaciones con customer, legal_case, payment, agreement. |
| Legal | Si | `legal.*` | Si | Si | Bajo | Lawyer ve asignados; director/admin ve tenant. |
| Sales | Si | `sales.*` | Si | Si | Bajo | Sales advisor ve asignados; leader/admin ve tenant. |
| Recordings | Si | `recordings.*` | Si | Si | Bajo/Medio | Debe mantener storage real por tenant. |
| Integrations | Si | `integrations.*` | Si | Si | Bajo/Medio | Secretos enmascarados; cifrado pendiente para proveedores reales. |
| Subscriptions API | Si | Platform/tenant admin | Si/global segun rol | Si | Bajo | No bloquea tenants sin plan por compatibilidad. |
| Tenants legacy | Si | Platform admin | Global permitido | N/A | Bajo | Solo plataforma. |
| Typifications | Si | `typifications.*` | Si | Si via arbol/nodo | Bajo | Revisar nodos hijos siempre por arbol padre. |

## 3. Correccion aplicada en esta auditoria

Se reforzo el alcance interno de lideres:

- `crm/access.py`: `customer_query` ahora limita `COORDINATOR` y `collections_leader` a clientes de su equipo o carteras asignadas.
- `crm/obligations.py`: `obligation_query` ahora limita `COORDINATOR` y `collections_leader` a obligaciones de su equipo, asignacion como lider o carteras asignadas.
- `teams.py`: un lider sin permisos administrativos ya no puede abrir por URL el equipo de otro lider; `list_leaders` y `list_agents` se ajustan al alcance del usuario.

Esto reduce el riesgo de que un lider operativo vea informacion de otro equipo dentro del mismo tenant.

## 4. Validaciones de acceso por ID directo

Revisado y cubierto por tests:

- cliente ajeno por actividades
- obligacion ajena por patch
- documento ajeno por detail
- lote de carga ajeno por detail
- fila Excel Web ajena por patch
- caso juridico ajeno por detail
- equipo de otro lider
- exportes por agente
- governance global para admin tenant

## 5. Riesgos pendientes

| Riesgo | Severidad | Bloquea test | Recomendacion |
|---|---:|---:|---|
| `DEBUG`, `ALLOWED_ORIGINS` documentados pero sin middleware/enforcement activo | Media | No | Implementar CORS/config hardening antes de produccion publica. |
| `Base.metadata.create_all` y compatibility migrations en startup | Media | No | Mantener en test; en produccion depender de Alembic y ejecutar startup controlado. |
| Hijos sin tenant directo dependen del padre | Baja/Media | No | Agregar `tenant_id` redundante en futuras migraciones si se requiere auditoria fuerte. |
| Roles legacy siguen como fallback | Media | No | Mantener transicion gradual a RolePermission como fuente principal. |
| Integraciones reales necesitaran cifrado de secretos | Media | No | No guardar secretos en claro cuando se conecten proveedores reales. |

## 6. Decision

Los endpoints revisados soportan el modelo SaaS shared schema con aislamiento por tenant. La rama queda apta para servidor test, con QA de integracion demo y smoke tests posteriores al despliegue.
