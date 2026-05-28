# Checklist Pruebas Regresion V2

Usar este checklist antes de publicar una version de `v2/`.

| # | Prueba | Resultado esperado | Estado |
| ---: | --- | --- | --- |
| 1 | La app inicia correctamente | Uvicorn sirve `http://127.0.0.1:8020/` sin errores | Pendiente |
| 2 | Health endpoint responde | `GET /api/health` retorna app y base de datos OK | Pendiente |
| 3 | Login exitoso | Credenciales validas retornan token y usuario | Pendiente |
| 4 | Login fallido | Credenciales invalidas retornan 401 | Pendiente |
| 5 | Dashboard carga | `GET /api/crm/dashboard` retorna metricas | Pendiente |
| 6 | Listado de clientes carga | `GET /api/crm/customers` retorna pagina de clientes | Pendiente |
| 7 | Filtro de clientes funciona | Busqueda por nombre/documento filtra resultados | Pendiente |
| 8 | Cola de gestion carga | Se muestra maximo 10 clientes por pagina | Pendiente |
| 9 | Crear cliente funciona | `POST /api/crm/customers` crea cliente y audita evento | Pendiente |
| 10 | Cargar CSV funciona | `POST /api/crm/customers/import` crea/actualiza registros | Pendiente |
| 11 | Crear promesa funciona | `POST /api/crm/promises` crea promesa y actualiza cliente | Pendiente |
| 12 | Crear pago funciona | `POST /api/crm/payments` crea pago y reduce saldo | Pendiente |
| 13 | Tipificaciones funcionan | Se listan, crean, editan y eliminan nodos | Pendiente |
| 14 | Platform admin ve empresas, proyectos y usuarios | Modulos admin cargan datos globales | Pendiente |
| 15 | Usuario tenant no ve datos de otro tenant | APIs bloquean acceso cruzado | Pendiente |
| 16 | Agent solo ve clientes asignados | Listados y detalle respetan asignacion | Pendiente |
| 17 | Quality supervisor solo lectura | No puede crear o modificar registros operativos | Pendiente |
| 18 | Crear acuerdo funciona | `POST /api/crm/agreements` crea acuerdo y cuotas | Pendiente |
| 19 | Crear caso juridico funciona | `POST /api/legal/cases` valida tenant y crea expediente | Pendiente |
| 20 | Crear documento funciona | `POST /api/documents` registra metadata documental | Pendiente |
| 21 | Crear lead funciona | `POST /api/sales/leads` crea lead de tenant | Pendiente |
| 22 | Auditoria registra eventos criticos | `GET /api/admin/audit-logs` muestra eventos creados | Pendiente |

## Pruebas automatizadas sugeridas

- Auth: login correcto, login incorrecto y token invalido.
- CRM: clientes paginados, promesas, pagos y carga CSV.
- Seguridad: platform admin global, tenant admin aislado, agent asignado, quality lectura.
- Nuevos modulos: agreements, legal, documents, sales y subscriptions.

## Comandos de validacion local

```powershell
.\v2\backend\.venv\Scripts\python.exe -m compileall .\v2\backend\app
node --check .\v2\frontend\static\assets\app.js
powershell -ExecutionPolicy Bypass -File .\v2\scripts\start-v2.ps1
```
