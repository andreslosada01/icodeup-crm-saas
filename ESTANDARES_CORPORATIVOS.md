# IcodeUp CRM - Estandares corporativos objetivo

Este documento define los criterios que debe cumplir IcodeUp CRM para convertirse en una solucion corporativa de cobranzas.

## 1. Seguridad

- Autenticacion segura con politicas de contrasena, bloqueo por intentos y recuperacion controlada.
- Sesiones con expiracion, cookies seguras y proteccion CSRF cuando se despliegue con HTTPS.
- Roles y permisos por modulo: super usuario, administrador, coordinador, gestor y calidad.
- Administracion de usuarios con lider directo, cartera/proyecto y rol operativo por asociacion.
- Separacion estricta por empresa mediante `company_id` y validaciones en backend.
- Cifrado en transito con HTTPS.
- Cifrado o proteccion de secretos: credenciales SMTP, tokens WhatsApp, claves SIP y API keys.
- Registro de auditoria para cambios sensibles.

## 2. Datos y multiempresa

- Cada tabla operativa debe tener `company_id`.
- Los usuarios solo deben consultar datos de su empresa y de su alcance operativo.
- Los gestores ven solo clientes asignados.
- Los coordinadores ven su equipo.
- Los administradores operativos ven la empresa.
- El super usuario administra variables sensibles.
- Las cargas masivas deben validar duplicados, documentos, saldos, fechas, telefonos y campos obligatorios.

## 3. Auditoria y trazabilidad

- Cada gestion debe guardar usuario, fecha, cliente, canal, tipificacion, nota y resultado.
- Pagos, promesas, cambios de gestor y cambios de cartera deben quedar auditados.
- Las integraciones futuras deben guardar estados: enviado, entregado, leido, contestado, fallido, duracion y grabacion.
- La auditoria no debe ser editable desde la interfaz normal.

## 4. Cumplimiento operativo

- Parametrizar horarios permitidos de contacto.
- Manejar consentimiento y opt-out por canal.
- Registrar fuente de datos y fecha de carga.
- Aplicar reglas de privacidad y tratamiento de datos segun el pais de operacion.
- Para Colombia, considerar habeas data, autorizacion de tratamiento y politicas de cobranza respetuosa.

## 5. Omnicanalidad

- WhatsApp: iniciar con configuracion de lineas, luego conectar WhatsApp Business Cloud API o proveedor certificado.
- Email: iniciar con cuentas configuradas, luego SMTP/API con plantillas y tracking.
- Telefonia: iniciar con click-to-call, luego WebRTC/SIP embebido.
- Todos los canales deben compartir plantillas, trazabilidad, tipificaciones y reportes.

## 6. Disponibilidad y produccion

- Migrar SQLite a PostgreSQL.
- Usar migraciones versionadas.
- Desplegar con Docker.
- Servir por HTTPS con dominio propio.
- Backups automaticos y pruebas de restauracion.
- Logs centralizados.
- Monitoreo de disponibilidad, errores y rendimiento.
- Ambientes separados: desarrollo, pruebas, produccion.

## 7. Experiencia corporativa

- Interfaz sobria, densa y eficiente para operacion diaria.
- Dashboard ejecutivo con salud operacional, recuperacion, riesgo, productividad y cumplimiento.
- Capa BI para administradores y directivos con graficos, tendencias, concentracion, productividad y recomendaciones.
- Vistas de gestores optimizadas para cientos o miles de clientes.
- Flujos cortos para registrar gestion sin perder contexto.
- Accesibilidad: contraste, foco visible, etiquetas, tablas legibles y responsive.

## 8. Siguiente salto tecnico

Cuando el producto estabilice sus flujos, se recomienda modularizar:

- Backend con FastAPI o Django.
- Frontend con React o Vue.
- PostgreSQL.
- Cola de trabajos para envios masivos.
- Proveedor real de WhatsApp/email/telefonia.
- Sistema de permisos granular por modulo y accion.
