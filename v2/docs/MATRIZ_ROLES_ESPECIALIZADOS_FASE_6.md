# Matriz Roles Especializados Fase 6

## Objetivo

Fase 6 reduce la dependencia de `User.role = coordinator` para perfiles especializados. `User.role` se mantiene como fallback legacy, pero la fuente principal de acceso para perfiles nuevos es `UserProfile.role_id` + `RolePermission`.

## Matriz

| Perfil | User.role legacy recomendado | Role.code especializado | Modulos visibles | Permisos principales | Restricciones tenant | Restricciones de exportacion | Observaciones de compatibilidad |
|---|---|---|---|---|---|---|---|
| SuperAdmin Icodeup | `platform_admin` | Rol global `platform_admin` | Gobierno SaaS, administracion global, auditoria, salud | `*` por fallback y permisos globales | Puede consultar gobierno global | Puede exportar segun permisos globales | Usuario interno Icodeup. No representa cliente tenant. |
| Admin Empresa | `tenant_admin` | Rol global `tenant_admin` o rol tenant admin | Mi empresa, usuarios, roles, modulos contratados, operacion tenant, reportes | Usuarios, roles, tenant settings, modulos lectura, operacion tenant | Solo su tenant | Exporta solo si tiene permiso del tenant | No debe ver Gobierno SaaS global. |
| Lider Cobranzas | `coordinator` | `collections_leader` | Cobranzas, clientes, promesas, pagos, acuerdos, reportes y modulos autorizados | Permisos equivalentes a coordinator pero configurables por tenant | Solo su tenant/equipo segun endpoint | Sin exportes salvo permisos explicitos | Mantiene comportamiento operativo anterior, ahora parametrizable. |
| Gestor Cobranzas | `agent` | `collections_agent` | Mi operacion, cola, clientes asignados, promesas, pagos, acuerdos, documentos autorizados | `collections.*` operativo asignado, `crm.clients.view`, `crm.clients.update` | Solo clientes asignados | No exporta clientes ni pagos | Ya no hereda ventas por fallback legacy. |
| Supervisor Calidad | `quality_supervisor` | `tenant_auditor` | Lectura operativa, reportes y auditoria tenant si tiene permiso | Lectura de CRM, cobranzas, juridico, documentos, reportes, auditoria | Solo su tenant | Sin exportes salvo permisos explicitos | Se usa como perfil de auditoria/calidad sin gestion operativa. |
| Director Juridico | `agent` o `coordinator` temporal | `legal_director` | Juridico, documentos, clientes lectura, reportes, auditoria tenant | `legal.cases.*`, `legal.deadlines.view`, `documents.*`, `crm.clients.view` | Solo su tenant | Sin exportes salvo permiso explicito futuro | Puede ver casos juridicos del tenant. |
| Abogado | `agent` | `lawyer` | Inicio, Juridico, Documentos, Clientes lectura | `legal.cases.view/create/update`, `legal.deadlines.view`, `documents.view/create`, `crm.clients.view` | Solo casos asignados y clientes vinculados a sus casos | No exporta clientes ni pagos | Ya no necesita `coordinator` para operar juridico. |
| Lider Comercial | `agent` o `coordinator` temporal | `sales_leader` | Ventas, clientes lectura, reportes | `sales.leads.*`, `sales.opportunities.*`, `crm.clients.view`, `reports.view` | Solo su tenant | Puede exportar ventas si se mantiene permiso `sales.*.export` | No debe ver juridico sin permiso explicito. |
| Asesor Comercial | `agent` | `sales_advisor` | Inicio, Ventas, Clientes lectura | `sales.leads.view/create/update`, `sales.opportunities.view/create/update`, `crm.clients.view` | Solo ventas asignadas por usuario | No exporta clientes ni pagos | Ya no necesita `coordinator` para operar ventas. |
| Auditor | `quality_supervisor` | `tenant_auditor` | Lectura, reportes y auditoria tenant | Lectura transversal sin escritura | Solo su tenant | Sin exportes salvo permiso explicito | Perfil recomendado para control de calidad, auditoria y demo. |

## Reglas de transicion

1. `User.role` no se elimina en esta fase.
2. `UserProfile.role_id` tiene prioridad cuando apunta a un rol activo con permisos configurados.
3. El fallback legacy se usa solo cuando el usuario no tiene rol de perfil activo.
4. Los roles especializados se crean por tenant demo de forma idempotente.
5. Las rutas juridicas y comerciales validan permisos granulares antes de aceptar accesos por rol legacy.
6. El menu dinamico usa `profile_role` para definir la audiencia visual de perfiles especializados.

## Pendiente futuro

- Exponer en UI de usuarios el rol especializado como primer dato y dejar `User.role` como compatibilidad tecnica.
- Migrar tenants productivos a roles configurables con permisos revisados.
- Reducir mas validaciones legacy una vez existan migraciones y pruebas completas por cliente.

## Avance Fase 7

Fase 7 agrega la experiencia de perfil efectivo para que Admin Empresa y SuperAdmin puedan ver:

- rol legacy,
- rol especializado,
- permisos efectivos,
- modulos visibles,
- restricciones,
- alertas de seguridad.

Con esto, el administrador ya no necesita interpretar manualmente la relacion entre `User.role` y `UserProfile.role_id`.
