# Plan Pruebas Automatizadas V2

## Objetivo

Crear una base de pruebas de integracion para validar seguridad SaaS, aislamiento multi-tenant, permisos, modulos activos y exportes criticos sin tocar bases locales por accidente.

## Estructura

```text
v2/backend/tests/
  conftest.py
  test_auth.py
  test_tenant_isolation.py
  test_permissions.py
  test_modules.py
  test_exports.py
  test_governance.py
```

## Dependencias

`v2/backend/pyproject.toml` incluye:

- `pytest`
- `httpx`

## Seguridad de ejecucion

Las pruebas quedan protegidas por `ICODEUP_RUN_INTEGRATION_TESTS`.

Por defecto se saltan porque usan HTTP contra una instancia real de la app y podrian crear auditoria o modificar el estado de modulos si se ejecutan contra una base productiva.

## Comandos

Desde `v2/backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Para ejecutar integracion contra un ambiente seguro y sembrado:

```powershell
$env:ICODEUP_RUN_INTEGRATION_TESTS="1"
$env:ICODEUP_TEST_BASE_URL="http://127.0.0.1:8020"
$env:ICODEUP_TEST_PLATFORM_EMAIL="platform@icodeup.com"
$env:ICODEUP_TEST_PLATFORM_PASSWORD="<password_platform_test>"
$env:ICODEUP_TEST_TENANT_ADMIN_EMAIL="admin.andinaservicios@demo.icodeup.local"
$env:ICODEUP_TEST_AGENT_EMAIL="agente1.andinaservicios.bancoferias@demo.icodeup.local"
$env:ICODEUP_TEST_TENANT_PASSWORD="<password_tenant_test>"
.\.venv\Scripts\python.exe -m pytest
```

## Pruebas implementadas

| Archivo | Cobertura |
| --- | --- |
| `test_auth.py` | Login platform admin, admin empresa, agente y login fallido. |
| `test_tenant_isolation.py` | Bloqueo de terceros de otro tenant, scope de agente y export sin fuga por `tenant_id`. |
| `test_permissions.py` | 403 por falta de permisos, bloqueo de exportes para agente y permisos reservados. |
| `test_modules.py` | Modulo `sales` desactivado oculta menu y bloquea URL; restauracion posterior. |
| `test_exports.py` | Exportes de clientes y pagos requieren permiso y respetan tenant. |
| `test_governance.py` | Menus por audiencia y bloqueo de gobierno global a clientes. |

## Pruebas pendientes

- Suite con `TEST_DATABASE_URL` dedicada y recreable.
- Fixtures transaccionales directas a base de datos.
- Pruebas de creacion de acuerdos, juridico, documentos y ventas con rollback controlado.
- Pruebas de concurrencia para limites de plan.
- Pruebas de expiracion de token y usuarios inactivos.

## Riesgos cubiertos

- Fuga por menu dinamico.
- Acceso por URL a gobierno global.
- Exportes sin permiso.
- Modulo desactivado accesible por URL.
- Consulta cross-tenant via parametros.

## Riesgos no cubiertos todavia

- Carga CSV masiva en base temporal.
- Storage documental real.
- Retencion y masking avanzado de auditoria.
- Migraciones Alembic contra una copia real de produccion.
