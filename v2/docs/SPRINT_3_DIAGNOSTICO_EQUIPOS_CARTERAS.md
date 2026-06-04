# Sprint 3 - Diagnostico de equipos, carteras y asignaciones

## 1. Empresa / tenant actual
La plataforma usa modelo multi-tenant con base compartida y registros operativos filtrados por `tenant_id`. `Tenant` representa la empresa cliente y `Project` representa proyectos, carteras o workspaces operativos dentro de la empresa.

## 2. Proyectos / carteras
`Project` ya existe con `tenant_id`, `name`, `code`, `description` y `status`. Las carteras demo de Andina ya modelan consumo, microcredito, retail y judicializada.

## 3. Usuarios a proyectos
Ya existia `UserProjectAssignment` con `user_id` y `project_id`. La brecha era que no tenia rol operativo por cartera ni estado activo/inactivo. Sprint 3 agrega de forma no destructiva:
- `tenant_id`
- `role_in_project`
- `is_active`
- `updated_at`

## 4. Lideres a agentes
Ya existia `User.leader_id`, suficiente para el equipo principal del sprint. Se conserva como relacion directa lider-agente y se complementa con `UserProjectAssignment` para alcance por cartera.

## 5. Clientes a gestores
`Customer.assigned_user_id` ya existe. El gestor de cobranzas ve clientes asignados, mientras admin y lideres ven segun permisos y alcance.

## 6. Obligaciones a gestores/lideres
`CustomerObligation.assigned_user_id` y `assigned_leader_id` ya existen. Sprint 3 agrega endpoints dedicados para reasignar obligaciones con permiso `crm.assignments.manage`.

## 7. Vista actual del gestor
El gestor usa cola, clientes, promesas, pagos, acuerdos y Mi Excel Web con alcance asignado. No administra equipos.

## 8. Vista actual del lider/coordinador
El lider tenia dashboard basico y Excel Web de equipo. Sprint 3 refuerza dashboard y agrega seccion "Equipos y carteras" visible por permisos.

## 9. Vista admin empresa
Admin empresa administra usuarios, roles, modulos, branding, auditoria y ahora equipos/carteras dentro de su tenant.

## 10. Brechas detectadas
- No habia UI especifica para equipos y carteras.
- No habia endpoint dedicado `/api/teams`.
- Las asignaciones usuario-proyecto no diferenciaban lider/agente/calidad/juridico/comercial.
- Cambios legacy de proyectos borraban asignaciones; ahora se desactivan.
- Reasignacion cliente/obligacion no tenia endpoints dedicados por permiso.

## 11. Plan implementado
- Extender `UserProjectAssignment` de forma aditiva.
- Crear `/api/teams`.
- Agregar permisos `teams.*`, `project_users.*`, `crm.assignments.*`.
- Crear UI "Equipos y carteras".
- Reforzar dashboard de lider.
- Mantener `User.leader_id` como relacion principal del sprint.
- Actualizar bootstrap demo de Andina con roles por cartera.
- Agregar tests de regresion multi-rol.
