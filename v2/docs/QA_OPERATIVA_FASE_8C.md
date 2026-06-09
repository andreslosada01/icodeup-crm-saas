# QA Operativa Fase 8C

## Usuarios

- `superadmin@demo.icodeup.local`
- `admin.andina@demo.icodeup.local`
- `coord.cobranzas.andina@demo.icodeup.local`
- `gestor1.andina@demo.icodeup.local`
- `abogado.andina@demo.icodeup.local`
- `comercial.andina@demo.icodeup.local`

## Gestor

1. Iniciar sesion como gestor.
2. Confirmar que no ve Gobierno SaaS, Integraciones, Cargas ni Grabaciones.
3. Abrir Cola de gestion.
4. Hacer clic en Gestionar.
5. Confirmar que abre drawer lateral.
6. Registrar tipificacion, canal, resultado, fecha y nota.
7. Guardar gestion.
8. Esperar toast de exito.
9. Confirmar que actividad reciente se actualiza.

Resultado esperado: el gestor opera sin pantallas administrativas y sin errores silenciosos.

## Admin Empresa

1. Iniciar sesion como admin Andina.
2. Abrir Centro de Configuracion.
3. Crear catalogo.
4. Crear regla.
5. Crear alerta.
6. Crear workflow y etapa.
7. Abrir Integraciones.
8. Crear proveedor, canal, plantilla y webhook.
9. Probar canal y webhook.
10. Abrir Cargas y Repartos.
11. Seleccionar CSV, previsualizar y confirmar.
12. Abrir Mi Excel Web.
13. Ejecutar consulta, guardar vista y exportar si tiene permiso.
14. Abrir Grabaciones y probar detalle/playback.

Resultado esperado: el administrador configura y opera tenant sin tocar base de datos.

## Coordinador

1. Iniciar sesion como coordinador.
2. Confirmar acceso a operacion, reportes y modulos permitidos.
3. Gestionar cliente de la cola.
4. Validar que puede usar grabaciones/cargas solo si el menu y permisos lo permiten.

Resultado esperado: liderazgo operativo con permisos intermedios.

## SuperAdmin

1. Iniciar sesion como superadmin.
2. Confirmar Gobierno SaaS.
3. Confirmar acceso a Centro de Configuracion, Integraciones y Auditoria.
4. Validar que puede operar global/tenant segun permisos.

Resultado esperado: control total de plataforma.

## Abogado y Comercial

1. Iniciar sesion con cada perfil.
2. Confirmar que conservan Juridico o Ventas respectivamente.
3. Confirmar que no ven Gobierno SaaS.
4. Confirmar que no ganan permisos administrativos indebidos.

Resultado esperado: experiencia especializada coherente.

## Checklist tecnico

- Backend compila.
- Frontend pasa `node --check`.
- Alembic apunta a head.
- Pytest modo seguro no falla.
- Health responde.
- No hay secretos en repo.
- No hay archivos reales de carga/grabacion.
- No hay botones principales sin feedback.
