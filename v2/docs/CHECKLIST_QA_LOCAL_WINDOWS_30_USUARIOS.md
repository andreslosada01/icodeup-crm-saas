# Checklist QA Local Windows - Piloto 30 Usuarios

## 1. Preparacion

- PostgreSQL local activo.
- Base `icodeup_crm_local` creada.
- `v2/.env` configurado desde `v2/backend/.env.local.windows.example`.
- `alembic upgrade head` ejecutado.
- App disponible en `http://127.0.0.1:8020/`.
- Datos demo/piloto ficticios cargados.

## 2. Admin empresa

- Login exitoso.
- Dashboard de empresa carga.
- Puede ver usuarios de su tenant.
- Puede crear/editar usuarios permitidos.
- Puede consultar roles/permisos.
- Puede ver equipos y carteras.
- Puede consultar cargas y repartos.
- Puede abrir Excel Web.
- Puede exportar solo si tiene permiso.
- No ve Gobierno SaaS global.
- No ve datos de otros tenants.

## 3. Lider cobranzas

- Login exitoso.
- Dashboard equipo carga.
- Ve clientes de su equipo/carteras asignadas.
- Ve obligaciones de su equipo/carteras asignadas.
- Ve promesas de su equipo.
- Ve pagos de su equipo si tiene permiso.
- Puede consultar Excel Web de su alcance.
- No ve equipos de otros lideres por URL.
- No ve otros tenants.

## 4. Gestor

- Login exitoso.
- Ve clientes asignados.
- Ve obligaciones asignadas.
- Puede crear gestion.
- Puede crear promesa si tiene permiso.
- Puede crear acuerdo si tiene permiso.
- Puede consultar soporte/documentos autorizados.
- Puede editar Excel Web dentro de su alcance.
- No ve administracion.
- No exporta sin permiso.

## 5. Seguridad

- Gestor no ve menu administrativo.
- Gestor no exporta clientes/pagos.
- Lider no ve otros tenants.
- Lider no consulta otro lider por URL.
- Admin tenant no ve tenants ajenos.
- Admin tenant no modifica modulos globales.
- Abogado solo ve juridico/documentos/clientes autorizados.
- Comercial solo ve ventas/clientes autorizados.
- Modulos desactivados no aparecen ni responden por URL.

## 6. Performance manual basica

Escenario sugerido:

- 10 usuarios concurrentes navegando.
- 5 gestores guardando gestion.
- 1 admin cargando CSV.
- 1 lider consultando dashboard.
- 1 abogado consultando caso juridico.
- 1 comercial consultando pipeline.

Observaciones a registrar:

- tiempo de login
- tiempo de carga dashboard
- tiempo de listado clientes
- tiempo de guardado gestion
- errores 500/403 inesperados
- uso de CPU/RAM local

## 7. Evidencia minima

- Captura health OK.
- Captura dashboard admin.
- Captura dashboard lider.
- Captura cola gestor.
- Captura Excel Web.
- Captura carga CSV.
- Captura juridico.
- Captura ventas.
- Resultado `pytest` modo seguro.
- Resultado `alembic current`.

## 8. QA Especifico Icodeup Advisors

Activar previamente:

```env
ENABLE_PILOT_ICODEUP_SEED=true
```

Reiniciar la app y validar usuarios con contrasena demo local `Demo360!2026`.

### Admin Icodeup Advisors

- Login `admin.icodeup@demo.icodeup.local`.
- Ver usuarios del tenant Icodeup Advisors.
- Ver equipos y carteras piloto.
- Ver cargas y repartos metadata.
- Ver clientes piloto.
- Ver obligaciones piloto.
- Abrir Excel Web.
- Exportar solo si el rol tiene permiso.
- No ver tenant Andina aunque manipule `tenant_id` por URL.

### Lider Cobranzas

- Login `lider.cobranzas.icodeup@demo.icodeup.local`.
- Dashboard equipo carga con datos.
- Ver agentes asignados.
- Ver clientes del equipo.
- Ver obligaciones del equipo.
- Ver promesas del equipo.
- Consultar Excel Web equipo.
- No ver otro tenant.

### Gestor

- Login `gestor1.icodeup@demo.icodeup.local`.
- Ver clientes asignados.
- Ver obligaciones asignadas.
- Guardar gestion.
- Crear promesa.
- Crear acuerdo si tiene permiso.
- Consultar soporte/documentos metadata autorizados.
- Editar Excel Web dentro de su alcance.
- No ver otros gestores fuera de su alcance.
- No ver administracion.

### Seguridad Icodeup Advisors

- Gestor no ve admin.
- Gestor no exporta sin permiso.
- Gestor no ve clientes de otros gestores.
- Lider no ve otro tenant.
- Admin tenant no ve otro tenant.
- Abogado solo ve juridico/documentos/clientes autorizados.
- Comercial solo ve ventas/clientes autorizados.

### Prueba automatizada sugerida

```powershell
cd .\v2\backend
$env:ICODEUP_RUN_INTEGRATION_TESTS="1"
$env:ICODEUP_TEST_PLATFORM_PASSWORD="<password-demo-local>"
$env:ICODEUP_TEST_TENANT_PASSWORD="Demo360!2026"
$env:ICODEUP_TEST_PILOT_PASSWORD="Demo360!2026"
.\.venv\Scripts\python.exe -m pytest tests\test_pilot_icodeup_advisors_seed.py
```

No registrar esas variables en archivos versionados.
