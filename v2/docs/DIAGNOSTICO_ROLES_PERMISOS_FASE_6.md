# Diagnostico Roles y Permisos Fase 6

## 1. Roles legacy actuales

Los roles legacy definidos en `v2/backend/app/core/roles.py` son:

- `platform_admin`: super administrador interno de Icodeup.
- `tenant_admin`: administrador de empresa cliente.
- `coordinator`: lider/coordinador operativo.
- `quality_supervisor`: supervisor de calidad con lectura amplia.
- `agent`: gestor operativo.

Estos valores viven en `User.role` y siguen siendo necesarios como fallback de compatibilidad para login, tokens, administracion inicial y reglas legacy.

## 2. Roles custom actuales

El modelo `Role` permite roles globales (`tenant_id = null`) y roles por tenant (`tenant_id = empresa`). La asignacion granular vive en `UserProfile.role_id`.

Antes de Fase 6, los roles custom existian como capacidad administrativa, pero la demo especializada de abogado y comercial seguia usando `User.role = coordinator`, lo que les otorgaba permisos operativos amplios por fallback legacy.

## 3. Permisos actuales por modulo

El bootstrap registra permisos para:

- `core`: menu, salud y gobierno SaaS.
- `administration`: usuarios, roles, permisos, modulos, auditoria y configuracion tenant.
- `crm`: clientes, terceros, importes y exportes.
- `collections`: cola, promesas, pagos, acuerdos y exportes.
- `legal`: casos, vencimientos y exportes juridicos.
- `documents`: lectura, creacion, actualizacion y exportes.
- `sales`: leads, oportunidades y exportes.
- `bi`: reportes y exportes.
- `integrations`: canales.

## 4. Dependencias actuales de User.role

Se detectaron dependencias fuertes en:

- `access_control.py`: fallback legacy por `User.role`.
- `menu_service.py`: audiencia del menu por `User.role`.
- `legal.py`: `LEGAL_READ_ROLES` y `LEGAL_MANAGE_ROLES`.
- `sales.py`: `SALES_READ_ROLES` y `SALES_MANAGE_ROLES`.
- `documents.py`: `DOCUMENT_READ_ROLES` y `DOCUMENT_MANAGE_ROLES`.
- `crm/access.py`: lectura, escritura y alcance de clientes por rol legacy.

## 5. Riesgos de usar coordinator para abogado/comercial

- Abogado ve capacidades de cobranzas, ventas y reportes que no necesariamente corresponden a su perfil.
- Comercial ve juridico y cobranzas porque hereda permisos de coordinador.
- El menu puede parecer correcto por modulo, pero los permisos reales quedan demasiado amplios.
- En un SaaS comercial, esto complica auditoria, segregacion de funciones y venta por modulos.

## 6. Endpoints que aun dependen fuerte de roles legacy

- `/api/legal/*`: lectura/gestion juridica valida permiso granular, pero tambien valida rol legacy.
- `/api/sales/*`: lectura/gestion comercial valida permiso granular, pero tambien valida rol legacy.
- `/api/documents/*`: lectura/gestion documental valida permiso granular, pero tambien valida rol legacy.
- `/api/crm/*`: mantiene `customer_query` y `customer_for_access` por rol legacy, especialmente para agentes asignados.

## 7. Recomendacion de transicion segura

1. Mantener `User.role` como fallback legacy.
2. Dar prioridad a `UserProfile.role_id` cuando exista un rol activo con permisos explicitos.
3. Crear roles especializados por tenant demo y asignarlos por perfil.
4. Mantener `User.role` compatible, pero reducirlo a `agent` para perfiles especializados cuando sea seguro.
5. Ajustar menu para calcular audiencia desde rol especializado cuando exista.
6. Ajustar juridico y ventas para aceptar permisos granulares sin depender de `coordinator`.
7. Documentar que una fase futura eliminara dependencias legacy por modulo.

## 8. Matriz propuesta de perfiles especializados

| Perfil | Role.code especializado | User.role legacy recomendado | Proposito |
| --- | --- | --- | --- |
| Director Juridico | `legal_director` | `agent` | Gestion juridica del tenant con lectura documental y clientes. |
| Abogado | `lawyer` | `agent` | Gestion de casos asignados o del tenant segun permisos. |
| Lider Comercial | `sales_leader` | `agent` | Gestion comercial de leads y oportunidades del tenant. |
| Asesor Comercial | `sales_advisor` | `agent` | Gestion comercial asignada con clientes en lectura. |
| Lider Cobranzas | `collections_leader` | `coordinator` | Operacion de cobranzas equivalente a coordinador, pero configurable. |
| Gestor Cobranzas | `collections_agent` | `agent` | Operacion asignada equivalente a agente, pero configurable. |
| Auditor | `tenant_auditor` | `quality_supervisor` | Lectura, auditoria tenant y reportes sin gestion. |

La prioridad para Fase 6 es activar `lawyer` y `sales_advisor` en la demo de Andina, reduciendo la dependencia funcional de `coordinator`.
