# QA Hallazgo Telefonia: Extension no configurada

## Usuario usado

El hallazgo se reprodujo con un usuario operativo de cobranzas al abrir un cliente y presionar el boton `Llamar`.

## Modulo

Telefonia / Click-to-call desde ficha o cola de gestion.

## Accion realizada

1. Ingresar al CRM.
2. Abrir un cliente desde la cola o ficha de gestion.
3. Presionar `Llamar`.

## Error observado

La aplicacion mostraba varios toasts repetidos con mensajes como:

- `Accion no completada`
- `Extension no configurada para el usuario autenticado.`

El backend validaba correctamente que el usuario no tenia extension activa, pero la experiencia visual era ruidosa y no guiaba al administrador sobre como resolverlo.

## Causa tecnica

- El endpoint `POST /api/telephony/click-to-call` exige una `TelephonyExtension` activa para el usuario autenticado.
- Algunos usuarios demo/piloto no tenian extension simulada creada por bootstrap.
- El frontend usaba el manejador generico `runAction`, que mostraba toast de error generico.
- El boton no tenia proteccion por cliente contra clicks repetidos o acciones simultaneas.
- La UI de Telefonia tenia formulario base, pero no mostraba claramente usuarios sin extension ni acciones de editar/activar/desactivar.

## Correccion propuesta y aplicada

1. Crear proveedor simulado local idempotente para tenants demo/piloto.
2. Asignar extensiones simuladas a gestores, lideres y admins demo.
3. Mejorar el mensaje backend cuando falta extension.
4. Agregar deduplicacion de toasts iguales.
5. Bloquear click-to-call por cliente mientras procesa.
6. Mostrar un solo mensaje claro:
   `No tienes una extension telefonica configurada. Solicita al administrador configurarla en Telefonia > Extensiones.`
7. Completar UI de extensiones con matriz de usuarios, estado, editar, crear y activar/desactivar.

## Resultado esperado

- Usuario con extension activa registra llamada simulada.
- Usuario sin extension recibe un solo aviso claro.
- Admin empresa puede configurar extensiones desde `Telefonia > Extensiones`.
- No se hacen llamadas reales.
- No se guardan credenciales SIP reales.
