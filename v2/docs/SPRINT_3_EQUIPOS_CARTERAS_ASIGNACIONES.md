# Sprint 3 - Equipos, carteras y asignaciones operativas

## 1. Resumen ejecutivo
Sprint 3 convierte la operacion de cobranzas en una estructura mas real: admin configura carteras y equipos, lider consulta su equipo, gestor mantiene alcance propio, y clientes/obligaciones pueden reasignarse con permisos especificos.

## 2. Modelo empresa / proyecto / lider / agente
- Empresa: `Tenant`
- Cartera/proyecto: `Project`
- Usuario: `User`
- Perfil funcional: `UserProfile` + `Role`
- Relacion lider/agente: `User.leader_id`
- Asignacion usuario/cartera: `UserProjectAssignment`

## 3. Asignacion de usuarios a proyectos
`UserProjectAssignment` fue extendido sin destruir datos:
- `tenant_id`
- `role_in_project`: `leader`, `agent`, `quality`, `lawyer`, `sales`, `auditor`
- `is_active`
- `updated_at`

El cambio legacy de proyectos ya no borra filas; marca asignaciones como inactivas.

## 4. Asignacion lider / agentes
Se usa `User.leader_id` como relacion principal. El endpoint `POST /api/teams/leaders/{leader_id}/agents` asigna agente a lider y opcionalmente refuerza asignacion por cartera.

## 5. Asignacion de clientes
Nuevo endpoint:
- `PATCH /api/crm/customers/{customer_id}/assignment`

Requiere `crm.assignments.manage`, valida tenant, proyecto y usuario asignado.

## 6. Asignacion de obligaciones
Nuevo endpoint:
- `PATCH /api/crm/obligations/{obligation_id}/assignment`

Permite asignar gestor, lider y proyecto. Requiere `crm.assignments.manage`.

## 7. Dashboard lider
El dashboard de lider ahora resume:
- equipo directo
- clientes del equipo
- obligaciones y saldo
- gestiones de hoy
- promesas vigentes/vencidas
- pagos del mes
- acuerdos activos

## 8. Excel Web lider
No se cambio la arquitectura de Mi Excel Web. Ya venia filtrando por `leader_id`, `UserProjectAssignment` y fuentes de equipo. Sprint 3 conserva esa logica y mantiene labels de alcance de equipo.

## 9. Menu por rol
Se agrega "Equipos y carteras" para:
- Admin empresa con `teams.view`
- Lider operativo con `teams.view`

Gestor no recibe este permiso y no ve la seccion.

## 10. Permisos
Permisos nuevos:
- `teams.view`
- `teams.manage`
- `project_users.view`
- `project_users.manage`
- `crm.assignments.view`
- `crm.assignments.manage`

Admin empresa puede administrar. Lider puede ver y, si su rol tiene permiso, gestionar asignaciones. Gestor queda bloqueado.

## 11. Endpoints nuevos
- `GET /api/teams/projects`
- `GET /api/teams/projects/{project_id}/users`
- `POST /api/teams/projects/{project_id}/users`
- `PATCH /api/teams/project-users/{assignment_id}`
- `GET /api/teams/leaders`
- `GET /api/teams/agents`
- `GET /api/teams/leaders/{leader_id}/agents`
- `POST /api/teams/leaders/{leader_id}/agents`
- `GET /api/teams/leaders/{leader_id}/summary`
- `GET /api/teams/dashboard`
- `PATCH /api/crm/customers/{customer_id}/assignment`
- `PATCH /api/crm/obligations/{obligation_id}/assignment`

## 12. UI
Nueva seccion `teams`:
- resumen de carteras
- usuarios por cartera
- formulario asignar usuario/cartera
- formulario asignar agente/lider
- resumen del lider
- ranking basico de equipo

Todas las tablas usan paginacion maxima de 20 registros por pagina.

## 13. Pruebas
Nuevo archivo:
- `v2/backend/tests/test_sprint3_teams_portfolios.py`

Cubre admin, lider, gestor y restricciones de reasignacion.

## 14. Riesgos pendientes
- Para multiples lideres por agente en distintas carteras podria requerirse un modelo futuro `LeaderAgentAssignment`.
- La UI permite gestion basica; edicion avanzada por cartera puede ampliarse en otro sprint.
- El alcance de lider se mantiene por `leader_id` y asignaciones activas; si un cliente necesita matrices complejas por campana, conviene evolucionar a relacion lider-agente por proyecto.
