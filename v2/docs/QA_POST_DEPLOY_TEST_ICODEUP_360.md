# QA post deploy test Icodeup 360

## Objetivo

Validar que Icodeup 360 funciona en servidor test antes de considerar cualquier paso a produccion.

## SuperAdmin

Usuario sugerido: `superadmin@demo.icodeup.local`

- [ ] Login exitoso.
- [ ] Ve Gobierno SaaS.
- [ ] Ve empresas/tenants.
- [ ] Ve planes.
- [ ] Ve suscripciones.
- [ ] Ve modulos.
- [ ] Ve salud del sistema.
- [ ] Ve auditoria global.
- [ ] No se observan errores JavaScript severos.

## Admin Empresa

Usuario sugerido: `admin.andina@demo.icodeup.local`

- [ ] Login exitoso.
- [ ] Ve Mi Empresa.
- [ ] Ve usuarios.
- [ ] Ve roles/permisos.
- [ ] Ve equipos y carteras.
- [ ] Puede consultar cargas y repartos.
- [ ] Puede descargar plantilla CSV.
- [ ] Puede hacer preview de CSV ficticio.
- [ ] Ve Excel Web.
- [ ] Ve configuracion.
- [ ] Ve integraciones.
- [ ] Ve auditoria tenant.
- [ ] No ve gobierno global indebido.

## Lider

Usuario sugerido: `coord.cobranzas.andina@demo.icodeup.local`

- [ ] Login exitoso.
- [ ] Ve dashboard de equipo.
- [ ] Ve clientes del equipo.
- [ ] Ve obligaciones del equipo.
- [ ] Ve promesas del equipo.
- [ ] Ve pagos del equipo.
- [ ] Ve acuerdos del equipo.
- [ ] Ve Excel Web de su alcance.
- [ ] No ve datos de otros tenants.

## Gestor

Usuario sugerido: `gestor1.andina@demo.icodeup.local`

- [ ] Login exitoso.
- [ ] Ve clientes asignados.
- [ ] Ve obligaciones asignadas.
- [ ] Puede abrir cliente.
- [ ] Puede registrar gestion.
- [ ] Ve gestion en actividad reciente.
- [ ] Puede crear promesa si tiene permiso.
- [ ] Puede consultar acuerdos.
- [ ] Puede registrar soporte metadata si aplica.
- [ ] Ve Excel Web con alcance operativo.
- [ ] No ve administracion.
- [ ] No puede exportar sin permiso.

## Abogado

Usuario sugerido: `abogado.andina@demo.icodeup.local`

- [ ] Login exitoso.
- [ ] Ve juridico.
- [ ] Ve casos juridicos demo.
- [ ] Ve vencimientos.
- [ ] Ve documentos si tiene permiso.
- [ ] No ve gobierno SaaS.
- [ ] No ve ventas si no tiene permiso.

## Comercial

Usuario sugerido: `comercial.andina@demo.icodeup.local`

- [ ] Login exitoso.
- [ ] Ve ventas.
- [ ] Ve leads.
- [ ] Ve oportunidades.
- [ ] Ve pipeline.
- [ ] No ve juridico si no tiene permiso.
- [ ] No ve gobierno SaaS.

## Seguridad

- [ ] Gestor no ve administracion.
- [ ] Lider no ve otros tenants.
- [ ] Admin tenant no ve otros tenants.
- [ ] Parametros `tenant_id` manipulados no fugan datos.
- [ ] Exportes requieren permiso.
- [ ] Modulos no contratados no aparecen.
- [ ] Health no expone secretos.

## Cargas y Excel Web

- [ ] Preview CSV ficticio funciona.
- [ ] Confirmacion CSV ficticio funciona en test si se autoriza.
- [ ] Descarga de errores/resultado funciona.
- [ ] Excel Web consulta clientes.
- [ ] Excel Web guarda fila operativa.
- [ ] Paginacion maxima 20 visible en tablas principales.

## Criterio de aprobacion

El servidor test puede considerarse aprobado si:

- Todos los roles criticos pasan.
- No hay fugas de tenant.
- No hay errores 500 en flujos principales.
- No hay secretos en logs.
- Backups y restore fueron probados.
- La operacion demo es presentable para validacion comercial/tecnica.
