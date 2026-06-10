# Auditoria Modulo Collection CRM Real

Fecha: 2026-06-10  
Rama auditada: `feature/deploy-test-server`

## 1. Resumen ejecutivo

El modulo Collection CRM tiene una base funcional suficiente para operar una demo comercial robusta y un servidor test con empresas reales controladas. La estructura cubre tenant, proyectos/carteras, clientes, obligaciones multiples, gestiones, promesas, pagos, acuerdos, documentos, demograficos, cargas/repartos, Excel Web, dashboards, permisos, auditoria, exportes e integraciones base.

No obstante, para produccion masiva se recomienda completar hardening operativo: CORS/origenes, storage documental real, politicas de retencion, colas/background jobs para cargas grandes, y separacion futura de `Customer`/`Obligation` si el volumen lo exige.

## 2. Clasificacion funcional

| Requisito operativo | Estado | Evidencia | Observacion |
|---|---|---|---|
| 1. Empresa/tenant | Listo | `Tenant`, `tenant_id`, governance | Shared schema con aislamiento por tenant. |
| 2. Proyecto/cartera | Listo | `Project`, `UserProjectAssignment` | Cartera por tenant y asignacion de usuarios. |
| 3. Lider | Listo | `User.leader_id`, Teams | Se reforzo scope para no ver otros equipos sin admin. |
| 4. Gestor | Listo | `assigned_user_id`, agent scope | Gestor ve asignados y crea gestiones. |
| 5. Cliente | Listo | `Customer` | Cliente/deudor operativo con riesgo, prioridad y datos de contacto. |
| 6. Obligaciones multiples | Listo | `CustomerObligation` | Multiples obligaciones por cliente y cartera. |
| 7. Gestion por cliente y obligacion | Listo | `ManagementActivity.obligation_id` | Registro con canal, resultado, nota y proximo contacto. |
| 8. Promesa por cliente y obligacion | Listo | `PaymentPromise.obligation_id` | Promesas vigentes/cumplidas/vencidas. |
| 9. Pago | Listo | `Payment` | Recaudo y export seguro por permiso. |
| 10. Acuerdo | Listo | `PaymentAgreement`, installments | Cuotas ligadas al acuerdo; cuotas heredan tenant por acuerdo. |
| 11. Soporte/documento | Listo parcial | `Document`, `OperationalFile` | Metadata lista; storage fisico real requiere politica productiva. |
| 12. Demograficos | Listo | `CustomerDemographic` | Telefonos/emails/direcciones adicionales. |
| 13. Telefonos/emails/direcciones | Listo parcial | `Customer`, `CustomerDemographic` | Modelo cubre principal y enriquecido; falta validacion avanzada/calidad de dato. |
| 14. Reparto de cartera | Listo | `UploadBatch`, reparto_cartera | Carga asigna gestor/lider/proyecto. |
| 15. Cargas masivas | Listo | `/api/uploads/preview`, `/confirm` | Para volumen alto conviene background jobs. |
| 16. Excel Web operativo | Listo | `/api/excel-web/*`, `OperationalSheetRow` | Tabla editable y export con limites. |
| 17. Dashboard gestor | Listo | Dashboard por rol y CRM | Enfocado en asignados. |
| 18. Dashboard lider | Listo | `teams/dashboard`, dashboard role | Enfocado en equipo/carteras. |
| 19. Admin empresa | Listo | Governance tenant, users, roles, modules | Admin tenant no ve gobierno global. |
| 20. Auditoria | Listo | `AuditLog`, `record_audit` | Payload sensible redactado. |
| 21. Permisos | Listo | RolePermission + fallbacks | Legacy role sigue como compatibilidad. |
| 22. Exportes controlados | Listo | customers/payments/excel exports | Permisos export y scope tenant. |
| 23. Integraciones/canales base | Funcional parcial | providers, channels, templates, webhooks | Base lista; proveedores reales pendientes. |

## 3. Flujo operativo cubierto

1. Admin empresa o plataforma crea/provisiona tenant y proyectos.
2. Se asignan lideres, gestores y carteras.
3. Se carga reparto por CSV o carga operativa.
4. El sistema crea/actualiza clientes, obligaciones, demograficos o pagos.
5. El gestor consulta cola/clientes asignados.
6. El gestor registra gestion, promesa, pago o acuerdo.
7. Lider revisa tablero, equipo, cartera, promesas y pagos.
8. Admin revisa usuarios, roles, modulos, auditoria y configuracion.
9. BI resume riesgo, recuperacion, contactabilidad y oportunidades operativas.

## 4. Gaps no bloqueantes para test

- Telefonia/WhatsApp/email aun son configuracion base y handoff; integracion real requiere proveedores.
- Documentos registran metadata; storage binario productivo debe definirse por ambiente.
- Cargas masivas grandes deben pasar a proceso asincrono en produccion.
- `Customer` aun conserva campos resumidos de obligacion para compatibilidad; el modelo nuevo ya soporta `CustomerObligation`.
- Reglas de negocio/workflows existen como base, pero aun no reemplazan toda la logica operativa legacy.

## 5. Gaps bloqueantes para produccion publica masiva

No bloquean servidor test, pero si deben atenderse antes de una salida productiva amplia:

1. Politica CORS/origenes y headers de seguridad.
2. Secretos y credenciales reales fuera del repositorio y rotacion documentada.
3. Backups/restore probados con datos productivos.
4. Storage documental por tenant y control de acceso fisico.
5. Jobs asincronos para cargas pesadas.
6. Monitoreo de errores, logs y metricas.
7. Definir SLAs y proceso de soporte.

## 6. Decision Collection CRM

El modulo esta **listo para servidor test** y para demos comerciales con empresas ficticias o clientes piloto controlados. Para produccion inicial, la estructura es viable siempre que se complete hardening operativo y se mantengan pruebas multi-tenant en cada release.
