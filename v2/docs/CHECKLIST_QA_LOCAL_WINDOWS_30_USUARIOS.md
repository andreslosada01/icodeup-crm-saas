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
