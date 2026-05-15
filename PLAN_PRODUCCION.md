# IcodeUp CRM - Plan funcional y produccion

Este documento define el camino para convertir el prototipo en un CRM de cobranzas funcional, multiempresa, auditable y listo para servidor.

## 1. Estado actual

Ya existe una primera fase funcional local:

- Frontend web con tablero, cola, clientes, promesas, pagos, campanas, reportes y configuracion.
- Backend local en `server.py`.
- Base de plataforma SQLite en `data/platform.sqlite3`.
- Bases SQLite independientes por empresa en `data/tenants/`.
- Login por usuario con autodeteccion de empresa.
- Separacion fisica local por empresa tenant, mas `company_id` como control adicional.
- Rol plataforma IcodeUp para alta de empresas contratantes y proyectos.
- Roles operativos: super usuario, administrador, coordinador/lider, gestor y supervisor de calidad.
- Arbol de tipificaciones por empresa.
- Omnicanalidad inicial: click to call con `tel:`, WhatsApp con enlace `wa.me`, correo con `mailto:`.

## 2. Empresas y usuarios

La base soporta multiples empresas. Cada cliente, pago, promesa, campana, tipificacion y auditoria queda asociado a `company_id`.

Empresas demo:

- Pepe Perez
- Inversiones Martinez

Usuarios demo por empresa:

- Plataforma IcodeUp: `platform@icodeup.com` / `Platform123!`
- Administrador: `admin@pepeperez.com` / `Admin123!`
- Usuario estandar: `gestor@pepeperez.com` / `Gestor123!`
- Supervisor calidad: `calidad@pepeperez.com` / `Calidad123!`
- Administrador Martinez: `admin@martinez.com` / `Admin123!`
- Usuario Martinez: `gestor@martinez.com` / `Gestor123!`
- Calidad Martinez: `calidad@martinez.com` / `Calidad123!`

## 3. Roles

IcodeUp plataforma:

- Administra empresas contratantes del SaaS.
- Crea el administrador inicial de cada empresa.
- Crea proyectos/carteras base por empresa.
- No opera gestiones de cobranza de los clientes.

Super usuario:

- Accede a variables globales, parametros, configuracion sensible y toda la operacion de la empresa.
- A futuro: administra permisos, integraciones, limites, tipificaciones maestras y seguridad.

Administrador operativo:

- Gestiona cartera, promesas, pagos, campanas y parametros.
- Puede cargar repartos, ver la cartera de la empresa y coordinar asignaciones.

Coordinador o lider:

- Carga repartos operativos.
- Visualiza los clientes de su equipo.
- Puede asociar gestores a carteras, proyectos o campanas.

Usuario estandar:

- Gestiona clientes asignados.
- Registra llamadas, WhatsApp, correos, tipificaciones, promesas y pagos.
- No debe cargar repartos ni modificar variables globales.

Supervisor de calidad:

- Acceso de solo lectura en esta fase.
- A futuro: escucha/valida gestiones, audita grabaciones, califica agentes y genera hallazgos.

## 3.1 Repartos y carteras

El reparto debe entrar como archivo CSV o Excel y convertirse en una cartera/proyecto. Cada cliente queda asociado a:

- Empresa.
- Cartera o proyecto.
- Lider/coordinador.
- Gestor asignado.
- Datos demograficos.
- Datos financieros.
- Obligaciones o cuentas.
- Historial de gestiones.

Columnas recomendadas para carga inicial:

- `nombre`
- `documento`
- `telefono`
- `email`
- `ciudad`
- `segmento`
- `saldo`
- `saldo_original`
- `mora`
- `gestor`
- `obligacion`
- `producto`
- `direccion`
- `ingreso`
- `score`
- `observacion`

## 4. Tipificaciones

El modelo usa un arbol:

- Nivel 1: Contacto, No contacto, Disputa.
- Nivel 2: Titular contactado, tercero contactado, no contesta, numero errado.
- Nivel 3: Promesa de pago, pago realizado, refinanciacion, no puede pagar, pago no aplicado.

Cada nodo puede definir:

- Estado siguiente del caso.
- Si requiere promesa.
- Si requiere pago.
- Canal recomendado.

En produccion esto debe ser configurable por empresa desde un modulo de administracion.

## 5. Omnicanalidad

Fase actual:

- Llamadas: `tel:` abre el marcador del sistema o softphone compatible.
- WhatsApp: `wa.me` abre conversacion con mensaje precargado.
- Email: `mailto:` abre el cliente de correo.
- Cada click deja trazabilidad en la bitacora.
- El administrador puede configurar lineas de WhatsApp, cuentas de correo y preconfiguracion de telefonia por empresa.
- Los expedientes muestran el canal predeterminado que se usa para cada gestion.

Importante: con enlaces `wa.me` y `mailto:` el navegador abre aplicaciones externas. La linea o correo configurado queda como canal operativo dentro del CRM, pero el envio real con remitente controlado requiere API del proveedor.

Fase productiva:

- WhatsApp Business Cloud API o proveedor como Twilio, MessageBird, Gupshup o Zenvia.
- Correo transaccional con SMTP, SendGrid, Mailgun, Amazon SES o Microsoft Graph.
- Click to call con proveedor VoIP, SIP, Asterisk, Issabel, Twilio Voice, Aircall o Genesys.
- Webhooks para guardar estados: enviado, entregado, leido, contestado, fallido.
- Grabaciones y metadatos de llamadas vinculados al expediente.

## 5.1 Recomendacion de implementacion omnicanal

La mejor ruta es por fases:

1. Configuracion interna de canales por empresa: lineas WhatsApp, correos, PBX futura y responsables.
2. Trazabilidad de intentos desde expediente: quien hizo click, por que canal, fecha, cliente y tipificacion.
3. Plantillas y aprobaciones: mensajes por segmento, mora y etapa juridica.
4. Integracion API de WhatsApp y correo para enviar desde el CRM sin abrir apps externas.
5. Telefonia embebida WebRTC con SIP/PBX o proveedor cloud.
6. Reportes de productividad por canal: enviados, contestados, llamadas efectivas, promesas, pagos.

## 6. Base de datos recomendada para produccion

SQLite sirve para desarrollo local. La version actual ya separa plataforma y tenants en archivos SQLite diferentes. Para produccion se recomienda PostgreSQL.

Para el modelo de renta a multiples empresas hay dos caminos:

- Base compartida con `tenant_id` o `company_id`: mas simple y economica, pero exige controles muy estrictos para evitar fuga de datos.
- Base independiente por empresa: mayor aislamiento, mejores backups/restauraciones por cliente y mas confianza comercial. Es la opcion recomendada para IcodeUp CRM si se vendera como solucion corporativa.

La arquitectura final recomendada combina:

- `platform_db`: registro de empresas, usuarios de login, planes, dominios, estado y cadena de conexion del tenant.
- `tenant_db_empresa_1`, `tenant_db_empresa_2`, etc.: operacion completa de cada empresa.
- Migraciones versionadas: cada cambio de logica se despliega en el codigo comun y se aplica como migracion a todas las bases tenant.

Tablas base:

- `companies`
- `users`
- `roles` y `permissions`
- `customers`
- `accounts` u `obligations`
- `interactions`
- `typification_nodes`
- `promises`
- `payments`
- `campaigns`
- `message_templates`
- `channel_messages`
- `call_logs`
- `audit_log`

Regla central en el prototipo: cada request operativo se resuelve contra la base tenant autenticada y las tablas conservan `company_id` como barrera adicional. Regla central en produccion SaaS: cada request debe resolverse contra la base o esquema del tenant autenticado.

## 7. Pasos para produccion

1. Consolidar requerimientos operativos: empresas, roles, flujos, tipificaciones, horarios de contacto y reportes.
2. Definir modelo tenant: base por empresa como opcion recomendada.
3. Migrar de SQLite a PostgreSQL con migraciones versionadas.
4. Separar frontend y backend en una arquitectura mantenible.
5. Implementar `platform_db` y aprovisionamiento de tenants.
6. Implementar administracion de usuarios, permisos y empresas.
7. Implementar carga masiva de cartera por Excel/CSV.
8. Implementar auditoria inmutable de gestiones y cambios sensibles.
9. Integrar WhatsApp, email y telefonia con proveedores reales.
10. Crear dashboard de supervisor de calidad.
11. Agregar seguridad: HTTPS, backups, cifrado, politicas de contrasena, bloqueo por intentos.
12. Desplegar en servidor con Docker, Nginx/Caddy, dominio y certificado SSL.

## 8. Decisiones pendientes

- Pais y reglas legales de cobranza que debe cumplir.
- Proveedor de WhatsApp Business.
- Proveedor de telefonia o PBX actual.
- Si cada empresa tendra base de datos fisica separada o una sola base multi-tenant con `company_id`.
- Volumen esperado de clientes, gestiones y mensajes por dia.
- Reportes obligatorios para administradores y supervisores.
