# Data Local Piloto Icodeup Advisors

Fecha: 2026-06-11
Ambiente objetivo: Windows local con PostgreSQL `icodeup_crm_local`

## 1. Objetivo

El seed piloto de Icodeup Advisors permite probar Icodeup 360 como CRM Collection funcional en una maquina Windows local antes de migrar al servidor test. La data es ficticia, idempotente, separada de la demo Andina y no debe mezclarse con produccion.

## 2. Activacion

El seed esta apagado por defecto.

Para activarlo en local/test:

```env
ENABLE_PILOT_ICODEUP_SEED=true
```

La variable vive en `v2/.env`. El ejemplo seguro esta en:

```text
v2/backend/.env.local.windows.example
```

No se debe activar este seed en produccion.

## 3. Tenant creado

| Campo | Valor |
|---|---|
| Nombre | `Icodeup Advisors` |
| Slug | `icodeup-advisors` |
| Base local | `icodeup_crm_local` |
| Arquitectura | Shared schema con `tenant_id` |
| Plan | `business` |

## 4. Usuarios piloto

Todos usan contrasena demo local:

```text
Demo360!2026
```

| Perfil | Email |
|---|---|
| Admin empresa | `admin.icodeup@demo.icodeup.local` |
| Lider cobranzas | `lider.cobranzas.icodeup@demo.icodeup.local` |
| Gestor 1 | `gestor1.icodeup@demo.icodeup.local` |
| Gestor 2 | `gestor2.icodeup@demo.icodeup.local` |
| Gestor 3 | `gestor3.icodeup@demo.icodeup.local` |
| Gestor 4 | `gestor4.icodeup@demo.icodeup.local` |
| Gestor 5 | `gestor5.icodeup@demo.icodeup.local` |
| Calidad | `calidad.icodeup@demo.icodeup.local` |
| Auditor | `auditor.icodeup@demo.icodeup.local` |
| Abogado | `abogado.icodeup@demo.icodeup.local` |
| Comercial | `comercial.icodeup@demo.icodeup.local` |

## 5. Carteras

| Codigo | Nombre |
|---|---|
| `PILOTO-CONSUMO` | Cartera Consumo Piloto |
| `PILOTO-PREVENTIVA` | Cartera Preventiva Piloto |
| `PILOTO-JURIDICA` | Cartera Juridica Piloto |

El lider y los 5 gestores quedan asignados a las carteras. Los usuarios de calidad, auditor, abogado y comercial tambien quedan relacionados segun su rol operativo.

## 6. Volumen generado

| Entidad | Volumen minimo |
|---|---:|
| Clientes | 300 |
| Obligaciones | 500 |
| Gestiones | 300 |
| Promesas | 50 |
| Pagos | 30 |
| Acuerdos | 20 |
| Demograficos | 100 |
| Lotes de carga demo | 3 |
| Repartos demo | 2 dentro de los lotes |

## 7. Reglas de datos ficticios

- Documentos sinteticos: `990300001`, `990300002`, etc.
- Telefonos sinteticos: `3009000001`, `3019000001`, etc.
- Correos demo: `@demo.icodeup.local`.
- Nombres sinteticos: `Cliente Piloto Icodeup 001`, etc.
- Saldos, mora, riesgo y estados variados.
- Clientes distribuidos entre 5 gestores.
- Obligaciones con `assigned_user_id` y `assigned_leader_id`.
- Cargas registradas como metadata; no hay archivos reales.
- No se crean cedulas, telefonos, correos ni soportes reales.

## 8. Idempotencia

El seed busca registros por claves naturales:

- tenant por `slug`
- usuarios por `email`
- proyectos por `tenant_id + code`
- clientes por `tenant_id + document`
- obligaciones por `tenant_id + obligation_number`
- cargas por `tenant_id + original_filename`

Puede ejecutarse varias veces sin duplicar masivamente la data piloto.

## 9. Validacion rapida

Despues de activar el seed y reiniciar la app:

```powershell
cd .\v2\backend
.\.venv\Scripts\python.exe -m pytest tests\test_pilot_icodeup_advisors_seed.py
```

Para ejecutar las pruebas de integracion se requieren variables seguras:

```powershell
$env:ICODEUP_RUN_INTEGRATION_TESTS="1"
$env:ICODEUP_TEST_PLATFORM_PASSWORD="..."
$env:ICODEUP_TEST_TENANT_PASSWORD="Demo360!2026"
$env:ICODEUP_TEST_PILOT_PASSWORD="Demo360!2026"
```

No registrar ni subir esas variables al repositorio.
