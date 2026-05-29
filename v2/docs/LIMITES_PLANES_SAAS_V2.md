# Limites Planes SaaS V2

## Objetivo

Aplicar enforcement inicial de limites comerciales sin romper tenants existentes ni datos demo.

## Servicio

El servicio queda en:

`v2/backend/app/services/plan_limits.py`

Funciones principales:

- `get_active_subscription(db, tenant_id)`
- `get_active_plan(db, tenant_id)`
- `get_tenant_usage(db, tenant_id)`
- `check_user_limit(db, tenant_id)`
- `check_project_limit(db, tenant_id)`
- `check_customer_limit(db, tenant_id, increment=1)`
- `check_storage_limit(db, tenant_id, additional_mb=0)`
- `enforce_or_allow_legacy(db, tenant_id, limit_type)`

## Limites actuales

| Limite | Campo plan | Uso calculado |
| --- | --- | --- |
| Usuarios | `max_users` | conteo de `users` por tenant |
| Proyectos | `max_projects` | conteo de `projects` por tenant |
| Clientes | `max_customers` o `max_records` | conteo de `customers` por tenant |
| Almacenamiento | `max_storage_mb` | suma de `documents.size_bytes` por tenant |

## Donde se aplican

| Operacion | Archivo | Validacion |
| --- | --- | --- |
| Crear usuario | `app/api/routes/administration.py` | `check_user_limit` |
| Crear proyecto | `app/api/routes/administration.py` | `check_project_limit` |
| Crear cliente | `app/api/routes/crm/customers.py` | `check_customer_limit` |
| Importar clientes | `app/api/routes/crm/imports.py` | `check_customer_limit` con nuevos registros |
| Crear documento metadata | `app/api/routes/documents.py` | `check_storage_limit` |
| Actualizar metadata documental | `app/api/routes/documents.py` | `check_storage_limit` por crecimiento de bytes |

## Compatibilidad legacy

Si un tenant no tiene suscripcion activa o no tiene plan:

- se permite la operacion;
- se registra auditoria `plan_limit/legacy_allow` cuando hay usuario disponible;
- no se bloquea la operacion local o demo.

Esto evita romper empresas creadas antes del hardening comercial.

## Limite 0

En esta fase, `0` significa ilimitado o no definido.

La regla queda documentada asi para evitar bloqueos accidentales. En una fase comercial posterior se puede cambiar a "no incluido" solo si se actualizan planes, UI y comunicacion de producto.

## Riesgos pendientes

- Validacion concurrente: dos solicitudes simultaneas podrian superar un limite por carrera.
- No hay bloqueo por plan en todos los modulos futuros.
- No se valida todavia almacenamiento fisico real, solo metadata documental.
- No se aplican todavia limites por automatizaciones, BI, IA o integraciones.

## Proximos pasos

- Agregar tests con base temporal para sobrepasar limites.
- Definir planes comerciales finales.
- Exponer uso y limites en gobierno SaaS.
- Evaluar locks transaccionales para operaciones masivas.
