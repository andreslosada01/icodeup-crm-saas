# Contact Compliance Rules MVP

## Objetivo

Agregar a IEP / Collects 360 una capa configurable de cumplimiento operativo para decidir si un cliente puede ser contactado por llamada, WhatsApp, email, SMS, canal presencial o web.

El MVP no codifica limites legales fijos. Las empresas definen sus propios parametros por tenant y, si aplica, por cartera.

## Alcance MVP

- Seccion visible: `Cumplimiento y contacto`.
- Persistencia reutilizada: `business_rules`.
- Tipo de regla: `rule_type = contact_compliance`.
- Modulo funcional: `collections`.
- Auditoria reutilizada: `audit_logs`.
- Paginacion maxima: 10 reglas por pagina.

## Reglas Configurables

Cada regla usa:

- `condition_json`: cartera, canales permitidos, canales bloqueados, dias, horario, maximos de intentos, clientes u obligaciones restringidas, consentimiento, vigencia y prioridad.
- `action_json`: severidad, prioridad y accion recomendada.

La prioridad de evaluacion es configurable. No hay valores legales quemados en codigo.

## Servicio Evaluador

El servicio `app.services.contact_compliance.evaluate_contact_rules` recibe:

- `tenant_id` inferido desde el cliente.
- `project_id` inferido desde cliente u obligacion.
- `customer_id`.
- `obligation_id` opcional.
- canal solicitado.
- usuario autenticado.
- fecha/hora actual.

Devuelve:

- `allowed`.
- `severity`: `info`, `warning`, `block`.
- `reason`.
- `matched_rules`.
- `recommended_action`.
- canales habilitados.
- intentos del dia y semana.
- siguiente ventana recomendada si aplica.

## Endpoints

- `GET /api/compliance/contact-rules`
- `POST /api/compliance/contact-rules`
- `PATCH /api/compliance/contact-rules/{id}`
- `POST /api/compliance/contact-rules/{id}/toggle`
- `POST /api/compliance/evaluate-contact`
- `GET /api/compliance/customer/{customer_id}/contact-status`

## Roles y Permisos

- `platform_admin`: acceso total.
- `tenant_admin`: consulta, configuracion y evaluacion.
- `coordinator`: consulta, configuracion y evaluacion si tiene permisos.
- `quality_supervisor`: consulta y evaluacion para auditoria.
- `agent`: evaluacion operativa sin configuracion visible.

Permisos:

- `contact_compliance.view`
- `contact_compliance.manage`
- `contact_compliance.evaluate`

## Integracion con Drawer Cliente

El drawer muestra `Estado de contacto`:

- permitido, advertencia o bloqueado.
- canales habilitados.
- ultima gestion por canal.
- intentos del dia.
- intentos de la semana.
- restricciones activas.
- siguiente ventana sugerida si aplica.

## Integracion con Canales

Antes de ejecutar acciones rapidas:

- `Llamar` valida en frontend y backend.
- `WhatsApp` valida antes de abrir el canal.
- `Email` valida antes de abrir `mailto`.
- gestiones por `phone`, `whatsapp`, `email` o `sms` validan antes de guardarse.

Si `allowed=false`, la accion no se ejecuta y se muestra:

`Contacto restringido por regla de cumplimiento`

Si `severity=warning`, se permite continuar con advertencia y auditoria.

## Auditoria

Se registra en `audit_logs` cuando una evaluacion:

- permite contacto.
- advierte.
- bloquea.

Las acciones bloqueadas en backend hacen commit del audit antes de responder `422`.

## Seed TEST

Seed separado:

```bash
python -m app.seeds.contact_compliance_demo --tenant-slug andina-servicios --dry-run
python -m app.seeds.contact_compliance_demo --tenant-slug andina-servicios --confirm-test
```

El seed es idempotente y crea reglas demo para:

- ventana horaria.
- canales por cartera.
- maximos de intentos.
- cliente/obligacion con bloqueo demo.

## Checklist QA

- Ingresar como tenant admin y abrir `Cumplimiento y contacto`.
- Crear una regla general activa con severidad `warning`.
- Crear una regla de bloqueo para una cartera.
- Validar que el listado pagina maximo 10.
- Abrir un cliente y revisar `Estado de contacto`.
- Probar `Llamar` con regla de bloqueo: debe mostrar mensaje claro y no ejecutar llamada.
- Probar WhatsApp/email con regla de advertencia: debe mostrar advertencia y continuar.
- Ingresar como agent: no debe ver configuracion, pero si advertencias en acciones operativas.
- Ingresar como coordinator: debe ver la seccion y gestionar reglas si su rol tiene permiso.
- Revisar `audit_logs` con `module=collections` y `entity_type=contact_compliance`.

## Siguientes Fases

- Excepciones temporales aprobadas por coordinador.
- Motor de consentimiento por canal y fuente.
- Reglas por segmento, riesgo, mora y producto.
- Reporteria de intentos bloqueados por asesor/cartera.
- Integracion ChatBOX 360 para WhatsApp/SMS real.
- Calendario de ventanas de contacto por festivos y zona horaria.
