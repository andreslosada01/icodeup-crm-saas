# Configuracion Data Demo V2

## Objetivo

La data demo permite presentar Icodeup 360 con una historia comercial consistente sin usar informacion real de personas, empresas o documentos.

## Activacion

La carga comercial de Fase 5 se ejecuta desde `bootstrap_platform()` cuando alguno de estos settings esta activo:

- `ENABLE_DEMO_DATA=true`
- `ENABLE_DEMO_SEEDS=true`

`ENABLE_DEMO_DATA` es la bandera recomendada para ambientes de demo. `ENABLE_DEMO_SEEDS` se mantiene por compatibilidad con configuraciones previas.

## Uso local sugerido

Desde `v2/backend`:

```powershell
$env:ENABLE_DEMO_DATA='true'
.\.venv\Scripts\python.exe -c "from app.db.session import SessionLocal; from app.services.bootstrap_service import bootstrap_platform; db=SessionLocal(); bootstrap_platform(db); db.close()"
```

No es necesario editar `.env` para una ejecucion puntual.

## Datos ficticios creados

- Tenants demo.
- Planes y suscripciones.
- Modulos activos por tenant.
- Usuarios demo.
- Proyectos/carteras.
- Clientes/deudores demo.
- Terceros maestros.
- Gestiones.
- Promesas.
- Pagos.
- Acuerdos y cuotas.
- Casos juridicos, actuaciones, audiencias y vencimientos.
- Documentos como metadatos ficticios.
- Leads y oportunidades.

## Perfiles especializados Fase 6

El bootstrap demo tambien configura roles especializados por tenant para que la demo muestre permisos mas realistas:

- `abogado.andina@demo.icodeup.local`: rol especializado `lawyer`.
- `comercial.andina@demo.icodeup.local`: rol especializado `sales_advisor`.
- `coord.cobranzas.andina@demo.icodeup.local`: rol especializado `collections_leader`.
- `gestor1.andina@demo.icodeup.local` y `gestor2.andina@demo.icodeup.local`: rol especializado `collections_agent`.
- `calidad.andina@demo.icodeup.local`: rol especializado `tenant_auditor`.

`User.role` se mantiene como fallback tecnico, pero el acceso real de estos usuarios se controla con `UserProfile.role_id` y `RolePermission`.

## Idempotencia

El bootstrap evita duplicados usando:

- slug de tenant.
- email de usuario.
- codigo de proyecto.
- documento demo de cliente.
- storage path documental.
- numero de caso juridico.
- referencia de pago.

Ejecutarlo varias veces actualiza la historia demo sin duplicar datos masivamente.

## Produccion

En produccion se recomienda:

- `ENABLE_DEMO_DATA=false`.
- `ENABLE_DEMO_SEEDS=false`, salvo que exista un proceso controlado de inicializacion.
- No cargar usuarios demo.
- No exponer la contrasena demo.
- No versionar bases locales, logs, `.env` ni archivos documentales reales.

## Advertencia

Los documentos creados son solo metadatos. Las rutas como `tenants/demo/andina/documentos/pagare_demo_001.pdf` no representan archivos reales versionados.
