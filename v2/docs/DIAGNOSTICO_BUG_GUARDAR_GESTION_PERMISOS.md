# Diagnostico Bug Guardar Gestion Permisos

## 1. Endpoint llamado desde UI

La UI usa:

`POST /api/crm/customers/{customer_id}/activities`

desde `submitActivity()` en `v2/frontend/static/assets/app.js`.

## 2. Payload enviado

Payload real del frontend:

```json
{
  "typification_id": null,
  "channel": "phone",
  "result": "Contactado",
  "note": "Texto de gestion",
  "next_contact_at": "2026-06-04T00:00:00Z",
  "promise_amount": null,
  "promise_due_date": null
}
```

## 3. Permiso requerido

El permiso funcional correcto para crear gestion es:

`crm.activities.create`

Antes del hotfix, si el usuario no pasaba `user_has_permission(db, user, "crm.activities.create")`, el endpoint caia a `require_permission(db, user, "crm.clients.update")`.

## 4. Permisos reales del usuario gestor

El gestor demo usa:

- Usuario: `gestor1.andina@demo.icodeup.local`
- `User.role`: `agent`
- Rol especializado esperado: `collections_agent`

El rol `collections_agent` debe tener `crm.activities.create`, pero una base local ya sembrada podia conservar permisos antiguos hasta reiniciar/bootstrap.

## 5. Rol legacy del usuario

`agent`.

## 6. Rol especializado del usuario

`collections_agent`.

## 7. Cliente usado en prueba

La prueba automatizada toma el primer cliente visible para el gestor desde:

`GET /api/crm/customers?page=1&page_size=1`

Ese listado ya viene filtrado por tenant y asignacion cuando el usuario es agente.

## 8. Validacion tenant

`customer_for_access()` bloquea clientes de otro tenant con 403.

## 9. Validacion asignacion

`customer_for_access(write=True)` mantiene la regla:

- `agent` solo gestiona clientes asignados.
- coordinador/admin puede gestionar dentro del tenant.
- quality supervisor queda lectura.

## 10. Causa raiz exacta

La causa raiz fue una combinacion de:

1. El endpoint dependia de permisos granulares y caia a `crm.clients.update` como fallback.
2. Con `UserProfile.role_id`, `get_user_permissions()` usa el rol especializado como fuente principal.
3. Si el rol especializado `collections_agent` quedaba desactualizado en una base ya sembrada, el gestor no pasaba `crm.activities.create`.
4. El fallback a `crm.clients.update` producia `Permiso insuficiente`, aunque el usuario fuera un gestor valido sobre cliente asignado.
5. En frontend, el toast de exito podia dispararse antes de terminar refrescos posteriores, generando feedback contradictorio si luego fallaba alguna carga.

## 11. Correccion aplicada

- Se agrego `_can_create_activity()` en `crm/activities.py`.
- La creacion de gestion acepta:
  - platform admin,
  - tenant admin,
  - coordinator,
  - usuario con `crm.activities.create`,
  - `agent` con perfil `collections_agent` o `collections_leader`.
- Se mantiene `customer_for_access(write=True)` para evitar gestion cross-tenant o cliente no asignado.
- Se retiro `recordings.view`/`recordings.playback` del fallback legacy de `agent`.
- Se ajusto el frontend para validar resultado/nota y mostrar exito solo al finalizar correctamente.
