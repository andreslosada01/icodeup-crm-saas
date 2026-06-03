# Hotfix Final CRM Cobranzas Demo

## 1. Causa real del error "Permiso insuficiente"

El guardado principal de gestion ya podia crear la actividad, pero el frontend ejecutaba cargas posteriores demasiado amplias despues del `POST /api/crm/customers/{customer_id}/activities`.

El flujo anterior llamaba `loadCrmData()`, `loadBi()`, `loadPhase8BData()`, `selectCustomer()` y `renderAll()`. Para un gestor, esa cadena podia terminar consultando modulos como Excel Web, grabaciones, cargas o integraciones si la base local conservaba permisos historicos. Cuando alguna llamada secundaria devolvia 403, `runAction()` mostraba un error global aunque la actividad ya se habia creado.

## 2. Gestion guardada pero refresh posterior fallaba

Si. El comportamiento visible podia ser contradictorio: la gestion aparecia en actividad reciente, pero luego se mostraba "Accion no completada" o "Permiso insuficiente" por un refresh posterior no relacionado con la accion principal.

## 3. Correccion aplicada

- `submitActivity()` ya no llama `loadPhase8BData()`, `loadBi()` ni `renderAll()` despues de guardar.
- Se creo `refreshCustomerAfterActivity(customerId)` para refrescar solo cola, clientes, actividades, promesas y pagos permitidos.
- Si un refresh accesorio falla, se registra con `console.warn` y no contamina el toast de guardado.
- El toast de error solo aparece si falla el `POST` principal.
- El toast de exito aparece solo despues de guardar y refrescar el contexto minimo.

## 4. Modulos ocultados al gestor

Para el perfil gestor de cobranzas se ocultaron o bloquearon:

- Grabaciones
- Cargas y repartos
- Integraciones
- Centro de configuracion
- Mi Excel Web
- Gobierno SaaS
- Auditoria
- Salud de sistema

## 5. Estado final de Mi Excel Web

Mi Excel Web queda enfocado en Admin Empresa para demo:

- Carga fuentes operativas desde `/api/excel-web/sources`.
- Ejecuta consulta inicial de clientes.
- Permite seleccionar fuente.
- Muestra columnas disponibles con checkboxes.
- Permite filtros por texto, estado, riesgo, proyecto, gestor y mora.
- Permite guardar vistas.
- Permite solicitar exportacion auditada.

Para gestor, Mi Excel Web queda oculto del menu y bloqueado por backend con 403.

## 6. Pruebas con gestor

Usuario probado:

- `gestor1.andina@demo.icodeup.local`

Validaciones:

- Login correcto.
- Menu operativo sin grabaciones ni Mi Excel Web.
- Cliente visible pertenece a su tenant y esta asignado al gestor.
- `POST /api/crm/customers/{id}/activities` responde 201.
- `GET /api/crm/customers/{id}/activities` muestra la gestion creada.
- Cliente no asignado queda bloqueado.
- Cliente cross-tenant queda bloqueado.
- `/api/excel-web/sources` responde 403.
- `/api/recordings` responde 403.

## 7. Pruebas con admin

Usuario probado:

- `admin.andina@demo.icodeup.local`

Validaciones:

- `/api/excel-web/sources` devuelve fuentes.
- `/api/excel-web/query` con fuente `customers` devuelve filas demo.
- `/api/excel-web/views` permite guardar vista.
- `/api/excel-web/export` registra exportacion.

## 8. Usuarios recomendados para demo

- SuperAdmin: `superadmin@demo.icodeup.local`
- Admin empresa: `admin.andina@demo.icodeup.local`
- Gestor: `gestor1.andina@demo.icodeup.local`

## 9. Modulos que no se deben mostrar al gestor

- Grabaciones
- Mi Excel Web
- Cargas
- Integraciones
- Configuracion
- Gobierno SaaS
- Auditoria
- Salud del sistema

## 10. Riesgos pendientes

- La validacion visual con navegador integrado puede requerir reiniciar el servicio local si el proceso no recarga automaticamente.
- Las pruebas automatizadas completas siguen protegidas por variables de entorno para evitar tocar bases no preparadas.
- Excel Web registra exportacion, pero la descarga fisica con storage seguro queda para una fase posterior.
