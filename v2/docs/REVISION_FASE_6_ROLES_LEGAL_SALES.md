# Revision Fase 6 Roles Legal Sales

## 1. Resumen ejecutivo

Fase 6 fortalece los perfiles especializados de Icodeup 360 para juridico y ventas sin romper la compatibilidad legacy. El cambio principal es que Abogado y Comercial dejan de depender funcionalmente de `User.role = coordinator`; ahora usan roles configurables por tenant con permisos granulares desde `UserProfile.role_id`.

La validacion con `TestClient` confirma que:

- Abogado ve juridico y documentos, no gobierno ni ventas.
- Comercial ve ventas, no juridico, documentos ni gobierno.
- Gestor de cobranzas conserva operacion de cartera y no accede a ventas por URL.
- Admin Empresa y SuperAdmin mantienen sus experiencias anteriores.

## 2. Cambios realizados

- Se agregaron roles especializados idempotentes en bootstrap demo.
- Se asignaron perfiles especializados a usuarios demo de Andina.
- Se ajusto `access_control.py` para priorizar `UserProfile.role_id` sobre fallback legacy.
- Se ajusto el menu dinamico para usar `profile_role` en perfiles especializados.
- Se reforzaron rutas de juridico, ventas y documentos con permisos granulares.
- Se agregaron dashboards operativos especializados para juridico y ventas.
- Se actualizo el frontend para mostrar etiquetas como Abogado y Asesor Comercial.
- Se agregaron pruebas de integracion preparadas para perfiles especializados.

## 3. Roles especializados creados

- `legal_director`
- `lawyer`
- `sales_leader`
- `sales_advisor`
- `collections_leader`
- `collections_agent`
- `tenant_auditor`

## 4. Permisos agregados o ajustados

No se agregaron nuevos codigos de permisos. Se reorganizaron asignaciones existentes:

- `lawyer`: `legal.cases.view/create/update`, `legal.deadlines.view`, `documents.view/create`, `crm.clients.view`.
- `sales_advisor`: `sales.leads.view/create/update`, `sales.opportunities.view/create/update`, `crm.clients.view`.
- `collections_agent`: conserva cobranzas asignadas, documentos lectura y clientes asignados; ya no hereda permisos comerciales legacy.

## 5. Usuarios demo ajustados

- `abogado.andina@demo.icodeup.local`: `User.role = agent`, `Role.code = lawyer`.
- `comercial.andina@demo.icodeup.local`: `User.role = agent`, `Role.code = sales_advisor`.
- `gestor1.andina@demo.icodeup.local`: `Role.code = collections_agent`.
- `gestor2.andina@demo.icodeup.local`: `Role.code = collections_agent`.
- `coord.cobranzas.andina@demo.icodeup.local`: `Role.code = collections_leader`.
- `calidad.andina@demo.icodeup.local`: `Role.code = tenant_auditor`.

## 6. Endpoints revisados

- `/api/menu/me`
- `/api/dashboard/me`
- `/api/legal/cases`
- `/api/legal/deadlines`
- `/api/documents`
- `/api/sales/leads`
- `/api/sales/opportunities`
- `/api/crm/customers`
- `/api/crm/customers/export`
- `/api/crm/payments/export`
- `/api/governance/roles`

## 7. Validaciones realizadas

- `python -m compileall` sobre archivos modificados de backend.
- `node --check` sobre `v2/frontend/static/assets/app.js`.
- Bootstrap demo ejecutado con `ENABLE_DEMO_DATA=true`.
- Smoke test con `TestClient` para SuperAdmin, Admin Empresa, Gestor, Abogado y Comercial.
- Health local respondio en `http://127.0.0.1:8020/api/health`.

## 8. Riesgos resueltos

- Abogado ya no requiere permisos amplios de coordinador para operar juridico.
- Comercial ya no requiere permisos amplios de coordinador para operar ventas.
- Gestor de cobranzas ya no accede a ventas por URL mediante fallback de `agent`.
- Documento juridico creado por abogado valida que el caso pertenezca a su asignacion.
- El dashboard y el shell muestran el perfil especializado en lugar del rol legacy.

## 9. Riesgos pendientes

- `User.role` sigue existiendo y algunos endpoints aun lo usan como compatibilidad.
- La UI de administracion de usuarios todavia debe mejorar para distinguir claramente rol legacy vs rol especializado.
- Algunas reglas finas de asignacion comercial dependen de `assigned_user_id`; una fase futura deberia revisar equipos comerciales y supervisores.
- La app local en 8020 puede quedar corriendo con codigo anterior si no se reinicia el proceso; por eso se uso `TestClient` para validar la rama actual.

## 10. Recomendacion

La Fase 6 queda lista para revision pre-merge. Antes del PR se recomienda ejecutar validaciones completas de regresion, incluyendo `pytest` en modo seguro y, si se reinicia el servicio local, smoke test HTTP real contra `127.0.0.1:8020`.
