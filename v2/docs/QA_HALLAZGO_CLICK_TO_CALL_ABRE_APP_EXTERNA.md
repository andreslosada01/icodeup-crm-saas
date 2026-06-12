# QA Hallazgo Click-to-Call: Apertura de App Externa

## Usuario probado

- Piloto Icodeup Advisors: `gestor1.icodeup@demo.icodeup.local`.
- Tambien aplica a usuarios que abren la ficha o cola de gestion sin que el frontend detecte la seccion `telephony` en el menu.

## Pantalla

- Cola de gestion.
- Drawer/ficha de gestion de cliente.

## Accion

El usuario pulsa el boton `Llamar` en la ficha del cliente.

## Comportamiento observado

El navegador/sistema operativo muestra un dialogo tipo:

`This site is trying to open Pick an app.`

Esto ocurre cuando el frontend renderiza un enlace con protocolo externo de llamada, por ejemplo `tel:`.

## Causa tecnica

El helper `channelHref("telephony", customer)` devolvia `tel:${customer.phone}` como fallback. En la cola y en el drawer, si `menuHasSection("telephony")` no detectaba la seccion, el boton `Llamar` se renderizaba como:

`<a href="tel:...">Llamar</a>`

Ese enlace delega la llamada al sistema operativo y dispara el dialogo para abrir Chrome, Teams, Skype, MicroSIP, Zoiper u otra aplicacion registrada.

## Correccion aplicada

- Se elimino el fallback `tel:` del frontend.
- `Llamar` se renderiza como `<button type="button" data-click-to-call="...">Llamar</button>`.
- El flujo usa exclusivamente `fetch` hacia `POST /api/telephony/click-to-call`.
- El payload incluye `customer_id`, `phone_number`, `obligation_id` cuando existe y `source: "crm_customer_drawer"`.
- El boton queda bloqueado mientras procesa para evitar doble click.
- La UI mantiene un solo toast claro por resultado.
- El backend acepta `source`, registra el origen en metadata/auditoria y responde `call_log_id`.
- El error de extension no configurada devuelve codigo estructurado `extension_not_configured` y mensaje funcional.
- Se agrego prueba estatica para impedir que `app.js` vuelva a abrir `tel:`, `sip:` o `callto:`.

## Resultado esperado

Con extension activa:

`Llamada registrada en modo simulado.`

Sin extension:

`No tienes una extension telefonica configurada. Solicita al administrador configurarla en Telefonia > Extensiones.`

En ningun caso debe aparecer un prompt del navegador para abrir aplicaciones externas.
