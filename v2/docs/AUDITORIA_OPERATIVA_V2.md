# Auditoria Operativa V2

## Objetivo

Registrar eventos criticos de seguridad, administracion y operacion sin guardar secretos ni contenido sensible.

## Modelo

`AuditLog` registra:

- `tenant_id`
- `user_id`
- `module`
- `object_type`
- `object_id`
- `entity_type`
- `entity_id`
- `action`
- `old_value`
- `new_value`
- `before_json`
- `after_json`
- `ip_address`
- `user_agent`
- `created_at`

## Servicio

Archivo:

`v2/backend/app/services/audit_service.py`

Funciones:

- `record_audit(...)`
- `safe_audit_payload(...)`

`safe_audit_payload` limpia claves sensibles y trunca strings largos.

## Campos prohibidos

No se deben guardar:

- contrasenas;
- hashes de contrasenas;
- tokens;
- secretos;
- API keys;
- contenido CSV completo;
- contenido binario;
- archivos;
- llaves privadas.

## Eventos auditados

| Evento | Accion |
| --- | --- |
| Login exitoso | `auth/login_success` |
| Login fallido | `auth/login_failed` |
| Crear tenant | `tenant/create` |
| Actualizar tenant | `tenant/update` |
| Crear proyecto | `project/create` |
| Crear usuario | `user/create` |
| Actualizar usuario | `user/update` |
| Crear rol | `role/create` |
| Actualizar rol | `role/update` |
| Cambiar permisos de rol | `role_permission/update` |
| Asignar rol a usuario | `user_role/assign` |
| Activar/desactivar modulo | `tenant_module/update` |
| Actualizar settings/branding | `tenant_settings/update` |
| Crear tercero | `party/create` |
| Actualizar tercero | `party/update` |
| Crear cliente | `customer/create` |
| Exportar clientes | `customer/export` |
| Importar clientes | `import_batch/create` |
| Crear promesa | `payment_promise/create` |
| Crear pago | `payment/create` |
| Exportar pagos | `payment/export` |
| Crear acuerdo | `payment_agreement/create` |
| Actualizar cuota de acuerdo | `payment_agreement_installment/update` |
| Crear caso juridico | `legal_case/create` |
| Actualizar caso juridico | `legal_case/update` |
| Crear accion juridica | `legal_action/create` |
| Crear audiencia juridica | `legal_hearing/create` |
| Crear documento | `document/create` |
| Actualizar documento | `document/update` |
| Crear lead | `lead/create` |
| Actualizar lead | `lead/update` |
| Crear oportunidad | `opportunity/create` |
| Actualizar oportunidad | `opportunity/update` |
| Permitir legacy por falta de plan | `plan_limit/legacy_allow` |

## Consulta de logs

- SuperAdmin Icodeup: `GET /api/governance/audit-logs` con filtros globales.
- Admin Empresa: mismo endpoint, filtrado automaticamente a su tenant.
- Usuario operativo: sin acceso salvo permiso explicito.

## Eventos pendientes

- Fallos de permisos 403 centralizados.
- Descarga real de documentos cuando exista storage binario.
- Exportes futuros PDF/Excel.
- Cambios de suscripcion comercial desde endpoints de subscriptions.
- Intentos fallidos de MFA cuando se implemente.

## Recomendaciones para produccion

- Retener logs segun politica contractual.
- Evitar payloads completos en operaciones de alto volumen.
- Enviar logs criticos a un sink externo.
- Monitorear `login_failed`, `export`, `tenant_module/update` y `role_permission/update`.
