# Checklist QA interno servidor Icodeup 360

## 1. Alcance

Validacion por red interna antes de publicacion externa por dominio y SSL.

URL interna:

```text
http://10.201.16.53
```

## 2. Salud tecnica

- `systemctl status icodeup360` activo.
- `systemctl status nginx` activo.
- `systemctl status postgresql` activo.
- `curl http://127.0.0.1:8020/api/health` OK.
- `curl http://127.0.0.1/api/health` OK.
- `curl http://10.201.16.53/api/health` OK.
- Logs de systemd sin errores criticos.
- Logs de Nginx sin errores criticos.
- `/favicon.ico` no genera 404 recurrente.

## 3. Acceso interno

- La app carga por `http://10.201.16.53`.
- No se expone `127.0.0.1:8020` fuera del servidor.
- No se publican puertos internos `8020`, `8030`, `8040`.
- No hay HTTPS publico todavia; se mantiene alcance interno.

## 4. Login admin

- Login con admin interno actual OK.
- Login con admin corporativo OK si ya fue creado.
- Login fallido muestra error controlado.
- No se muestran trazas tecnicas al usuario.

## 5. Dashboard y navegacion

- Dashboard carga.
- Sidebar muestra modulos segun permisos.
- No hay secciones duplicadas.
- No hay scroll horizontal.
- Menu de Gobierno SaaS solo para plataforma.
- Admin empresa no ve Gobierno SaaS global.
- Usuario operativo no ve administracion indebida.

## 6. Telefonia simulada

- Modulo Telefonia visible para roles autorizados.
- Extension configurada para gestor piloto.
- Boton `Llamar` ejecuta `POST /api/telephony/click-to-call`.
- No abre `tel:`, `sip:`, `callto:` ni selector externo de aplicaciones.
- Call log se registra.
- Historial de llamadas carga.

## 7. Operacion CRM/cobranzas

- Clientes cargan.
- Cola de gestion carga.
- Perfil de cliente abre.
- Gestion se guarda.
- Promesas cargan y se pueden consultar.
- Pagos cargan y se pueden consultar.
- Acuerdos cargan y se pueden consultar.
- Tipificaciones cargan.

## 8. Usuarios y permisos

- Admin puede ver usuarios autorizados.
- Roles/permisos cargan.
- Usuario sin permiso recibe bloqueo controlado.
- Agente no puede exportar si no tiene permiso.
- Abogado no ve ventas si no tiene permiso.
- Comercial no ve juridico si no tiene permiso.

## 9. Cargas, Excel Web y exportes

- Cargas/repartos muestran pantalla.
- Excel Web carga sin error.
- Exportes autorizados funcionan.
- Exportes no autorizados devuelven 403 controlado.
- Exportes respetan tenant.

## 10. Multi-tenant basico

- Tenant A no ve clientes de Tenant B.
- Documentos no cruzan tenants.
- Juridico no cruza tenants.
- Ventas no cruza tenants.
- Reportes/exportes no fugan datos entre empresas.

## 11. Backup manual

- Script real de backup existe fuera del repo.
- Backup manual ejecuta sin pedir contrasena interactiva.
- Backup resultante no esta vacio.
- Ruta y tamano se reportan sin imprimir secretos.
- No hay dumps dentro del repositorio.

## 12. Criterio de aprobacion interna

- Health OK por backend y Nginx.
- Login admin OK.
- Operacion principal OK.
- Telefonia simulada OK.
- Backup manual OK.
- Logs sin errores criticos.
- Acceso solo interno confirmado por `10.201.16.53`.
