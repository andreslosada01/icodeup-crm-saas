# Decision Arquitectura Tenancy Icodeup 360

Estado: Aprobada para servidor test  
Fecha: 2026-06-10  
Decision: `shared database / shared schema` con `tenant_id`

## 1. Contexto

Icodeup 360 debe operar como SaaS multiempresa para clientes con modulos CRM, cobranzas, juridico, documentos, ventas, BI, cargas, Excel Web e integraciones. La plataforma debe permitir que varias empresas usen el mismo producto sin ver ni modificar datos de otras empresas.

## 2. Decision

Para la produccion inicial y servidor test se mantiene:

**Una base PostgreSQL compartida, un schema compartido y aislamiento por `tenant_id`.**

No se implementa una base de datos independiente por empresa en esta etapa.

Nota de configuracion: si algun `.env` local usa `TENANT_MODE=row_level`, debe entenderse como una bandera no operativa para RLS. El codigo actual no crea politicas PostgreSQL Row Level Security ni establece contexto de tenant por sesion. Hasta que esa capacidad exista, la configuracion recomendada para test y produccion controlada es `TENANT_MODE=shared_schema`.

## 3. Justificacion

- Menor complejidad operativa para MVP comercial y primeras ventas.
- Menor costo de infraestructura.
- Permite administrar planes, modulos y usuarios desde un gobierno SaaS central.
- Facilita reporting global de Icodeup sin procesos ETL entre bases.
- Es compatible con Alembic, pruebas multi-tenant, auditoria y dashboards globales.
- Permite evolucionar mas rapido mientras se valida mercado.

## 4. Riesgos aceptados

| Riesgo | Control actual | Control futuro |
|---|---|---|
| Aislamiento depende del codigo | `tenant_id`, helpers de acceso, permisos, tests | Politicas automatizadas de revision y tests obligatorios en CI |
| Consulta sin tenant accidental | Tests de aislamiento y auditoria de endpoints | Linters/reglas internas para consultas operativas |
| Datos globales expuestos por error | Menus/permisos y rutas platform-only | Pruebas por rol y monitoreo de errores 403/200 |
| Backups no separados por cliente | Backups por base/ambiente | Backups logicos por tenant o base dedicada Enterprise |
| Cliente enterprise exige aislamiento fisico | No cubierto hoy | Database-per-tenant opcional futuro |

## 5. Controles obligatorios

1. Todo registro operativo debe tener `tenant_id` directo o padre validado con `tenant_id`.
2. Toda ruta operativa debe requerir autenticacion.
3. Toda ruta operativa debe validar permiso.
4. Toda ruta operativa debe validar modulo activo cuando aplique.
5. Toda consulta de usuario cliente debe filtrar por tenant.
6. Todo acceso por ID directo debe validar tenant del registro.
7. Gestores solo ven su alcance asignado.
8. Lideres solo ven su equipo/carteras salvo permisos administrativos.
9. Admin empresa solo administra su tenant.
10. SuperAdmin Icodeup puede ver gobierno global.
11. Exportes requieren permiso explicito y respetan tenant.
12. Auditoria no debe guardar passwords, tokens, secretos ni CSV completo.

## 6. Evolucion futura Enterprise

Se podra evaluar database-per-tenant para clientes Enterprise cuando exista una necesidad contractual o regulatoria. Requisitos:

- tabla de provisioning con modo de tenancy por tenant
- connection routing por tenant
- Alembic por base dedicada
- migracion de datos desde shared schema
- backups y restore por tenant
- observabilidad por base
- soporte operativo diferenciado
- pruebas de ambos modos en CI

## 7. Recomendacion oficial

Para Icodeup 360 en etapa actual:

- Mantener `TENANT_MODE=shared_schema`.
- No usar `TENANT_MODE=row_level` como promesa de seguridad hasta implementar RLS real, politicas por tabla y pruebas especificas.
- Usar base separada por ambiente: local, test, produccion.
- No crear base por empresa todavia.
- No mezclar datos demo con produccion.
- Activar demo solo en ambiente demo/test.
- Ejecutar pruebas multi-tenant antes de cada merge y despliegue.
- Considerar base dedicada solo para clientes Enterprise con contrato especifico.

## 8. Decision de despliegue

Servidor test: **aprobado con observaciones**.  
Produccion inicial controlada: **viable si se completa hardening operativo**.  
Produccion publica amplia: **requiere controles adicionales de seguridad, CORS, storage, backups y monitoreo**.
