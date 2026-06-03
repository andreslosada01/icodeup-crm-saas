# Hotfix Critico Guardar Gestion Funcional

## 1. Problema detectado

El gestor podia abrir el drawer/formulario de gestion, pero al guardar veia `Permiso insuficiente`.

## 2. Causa raiz

El endpoint `POST /api/crm/customers/{id}/activities` dependia de `crm.activities.create` y luego caia a `crm.clients.update`. En bases ya sembradas, el rol especializado del gestor podia no tener el permiso granular actualizado, por lo que el fallback generaba 403.

## 3. Permiso faltante o validacion incorrecta

La validacion incorrecta era exigir indirectamente `crm.clients.update` para una accion operativa de gestion. Crear una gestion debe depender de `crm.activities.create` o del perfil operativo `collections_agent` sobre cliente asignado.

## 4. Archivos corregidos

- `v2/backend/app/api/routes/crm/activities.py`
- `v2/backend/app/services/access_control.py`
- `v2/frontend/static/assets/app.js`
- `v2/frontend/static/assets/styles.css`
- `v2/backend/tests/test_critical_management_activity.py`

## 5. Prueba con gestor demo

Prueba ejecutada con TestClient:

1. Login `gestor1.andina@demo.icodeup.local`.
2. Consulta de clientes visibles.
3. Seleccion de cliente asignado.
4. POST a `/api/crm/customers/{id}/activities`.
5. Respuesta 201.
6. Consulta de historial.
7. Confirmacion de nota creada.

## 6. Resultado antes

El usuario veia error `Permiso insuficiente` al intentar guardar gestion.

## 7. Resultado despues

El gestor puede guardar gestion sobre cliente asignado y el historial refleja la nueva actividad.

## 8. Riesgos pendientes

- El backend local en puerto 8020 debe reiniciarse si estaba corriendo con codigo anterior.
- QA visual manual en navegador debe confirmar toast verde y drawer con servicio reiniciado.
- Las pruebas integradas completas siguen protegidas por variables de entorno para no tocar bases reales.

## 9. Confirmacion

El hotfix deja la regla operativa correcta: `collections_agent`/`agent` puede crear gestiones de clientes asignados, sin acceso administrativo ni exportes masivos.
