# Flujo de roles y menu CRM de cobranzas en IEP

IEP - Icodeup Enterprise Platform separa dos contextos: Gobierno SaaS y Operacion tenant. El SuperAdmin administra la plataforma por defecto; para probar o asistir una empresa debe entrar de forma explicita a soporte operativo seleccionando una empresa y una vista operativa.

## Contextos

### Gobierno SaaS

Rol principal: SuperAdmin / Platform Admin.

Vista esperada:
- Gobierno SaaS IEP.
- Empresas, planes, suscripciones y modulos.
- Usuarios, proyectos, tipificaciones globales, auditoria, configuracion, alertas, salud del sistema y Telefonia.

No debe mostrar por defecto:
- Cola de gestion.
- Clientes operativos.
- Pagos, promesas, acuerdos, cargas o repartos operativos.

### Soporte operativo tenant

Rol principal: SuperAdmin actuando sobre una empresa cliente.

Entrada esperada:
- Selector Empresa operativa.
- Selector de vista: Admin empresa, Lider cobranzas o Gestor.
- Boton Entrar a operacion / Aplicar.
- Boton Gobierno SaaS para salir.

Regla:
- El menu cambia a la audiencia elegida.
- Las cargas del frontend incluyen el tenant operativo cuando el endpoint lo soporta.
- El topbar muestra empresa activa y modo Soporte operativo.
- No se mezcla Gobierno SaaS con operacion tenant en el mismo menu.

## Menu esperado por rol

### SuperAdmin / Platform Admin

Por defecto ve Gobierno SaaS:
- Gobierno SaaS.
- Empresas.
- Planes.
- Suscripciones.
- Modulos.
- Usuarios y proyectos globales.
- Tipificaciones.
- Auditoria.
- Configuracion.
- Alertas.
- Telefonia.
- Salud del sistema.

Para QA operativo:
1. Iniciar sesion como SuperAdmin.
2. Seleccionar Empresa operativa en el topbar.
3. Seleccionar vista Admin empresa, Lider cobranzas o Gestor.
4. Usar Entrar a operacion.
5. Confirmar que el topbar muestre la empresa y Soporte operativo.

### Admin empresa / Tenant Admin

Debe ver:
- Dashboard / Inicio empresa.
- Mi empresa.
- Usuarios de empresa.
- Roles y permisos.
- Modulos contratados.
- Branding.
- Equipos y carteras.
- Clientes / terceros.
- Tercero maestro.
- Cola de gestion.
- Promesas.
- Pagos / PayControl 360.
- Acuerdos.
- Arboles de gestion.
- Grabaciones.
- Telefonia.
- Cargas y repartos.
- Analytics 360 / Reportes BI.
- Auditoria si tiene permiso.

Puede hacer:
- Administrar usuarios y roles de su empresa.
- Gestionar equipos, carteras, cargas, clientes, promesas, pagos y acuerdos segun permisos.
- Configurar Telefonia del tenant si tiene permiso.

No puede:
- Ver Gobierno SaaS global.
- Ver datos de otros tenants.
- Activar modulos globales o consultar inventario comercial global.

### Lider / Coordinador de cobranzas

Debe ver:
- Dashboard operativo.
- Cola de gestion.
- Clientes de su alcance operativo.
- Tercero maestro si tiene permiso.
- Promesas.
- Pagos.
- Acuerdos.
- Equipos y carteras.
- Grabaciones.
- Telefonia.
- Cargas y repartos si tiene permiso.
- Analytics 360 operativo.
- Alertas.

Puede hacer:
- Gestionar clientes de su equipo o cartera asignada.
- Registrar gestiones, promesas, pagos y acuerdos segun permisos.
- Consultar llamadas del equipo cuando el endpoint lo permita.
- Ver indicadores operativos.

No puede:
- Ver Gobierno SaaS.
- Ver tenants ajenos.
- Administrar configuracion global.

### Gestor / Agente de cobranzas

Debe ver:
- Inicio.
- Mi operacion / Cola de gestion.
- Mis clientes asignados.
- Detalle de cliente.
- Obligaciones.
- Demograficos.
- Telefonos, emails y direcciones disponibles.
- Crear gestion.
- Crear promesa.
- Ver pagos.
- Crear pagos si tiene permiso.
- Click-to-call.
- Historial de llamadas propio.
- Documentos de su alcance.
- Alertas de su alcance.

No debe ver:
- Gobierno SaaS.
- Configuracion global.
- Roles y permisos.
- Usuarios de empresa.
- Equipos globales.
- Clientes de otros gestores.
- Datos de otros tenants.

### Calidad / Auditor

Debe ver:
- Clientes y gestiones en modo consulta.
- Historial de llamadas.
- Auditoria operativa o reportes segun permisos.
- Analytics 360 si esta habilitado.

Puede hacer:
- Revisar actividades, llamadas y reportes.
- Consultar trazabilidad operativa.

No debe:
- Modificar clientes, pagos, acuerdos o configuracion salvo permisos especificos.

## QA por rol

### Validar SuperAdmin

1. Iniciar sesion como SuperAdmin.
2. Confirmar que el menu muestre Gobierno SaaS y no muestre Cola de gestion.
3. Seleccionar una empresa cliente en Empresa operativa.
4. Entrar como Admin empresa.
5. Confirmar menu operativo: Dashboard, Clientes, Cola, Promesas, Pagos, Acuerdos, Telefonia y Analytics si aplica.
6. Confirmar que el topbar muestre la empresa activa y Soporte operativo.
7. Usar Gobierno SaaS para salir.
8. Confirmar que vuelve el menu de Gobierno SaaS.

### Validar Admin empresa

1. Iniciar sesion como usuario tenant admin.
2. Confirmar que no aparece Gobierno SaaS.
3. Abrir Usuarios de empresa, Equipos y carteras, Clientes, Promesas, Pagos y Telefonia.
4. Confirmar que los listados pertenecen a su tenant.
5. Intentar consultar un tenant ajeno desde URL o filtros manuales y esperar 403, lista vacia o bloqueo por aislamiento.

### Validar Lider

1. Iniciar sesion como lider o coordinador.
2. Confirmar que aparecen Cola de gestion, Clientes, Equipos y carteras, Pagos, Promesas, Telefonia y Analytics.
3. Revisar que la cartera corresponda a su equipo/proyectos.
4. Validar que no puede acceder a Gobierno SaaS ni configuracion global.

### Validar Gestor

1. Iniciar sesion como gestor.
2. Confirmar que aparecen Mi operacion, Clientes, Promesas, Pagos, Acuerdos y Mi telefono.
3. Abrir un cliente asignado.
4. Registrar gestion y promesa si tiene permiso.
5. Ejecutar click-to-call con extension configurada.
6. Confirmar que no ve clientes de otros gestores ni menus administrativos.

### Validar Telefonia / click-to-call

1. Como Admin empresa o SuperAdmin en soporte operativo, abrir Telefonia.
2. Confirmar que Proveedores y Extensiones cargan para la empresa activa.
3. Si no hay proveedor, crear uno seleccionando empresa valida o usando el tenant operativo.
4. Crear extension para un usuario del tenant.
5. Como gestor, abrir cliente asignado y usar click-to-call.
6. Confirmar que se registra historial de llamada sin abrir protocolos externos del navegador.

### Validar aislamiento tenant

1. Elegir dos tenants con datos.
2. Como Admin empresa A, consultar clientes, pagos, promesas, cargas y telefonia.
3. Intentar usar filtros `tenant_id` de empresa B manualmente.
4. Confirmar bloqueo o ausencia de datos ajenos.
5. Como SuperAdmin en soporte empresa A, confirmar que las consultas operativas usan empresa A.
6. Cambiar soporte a empresa B y confirmar que cambian datos, menu contextual y Telefonia.

## Notas de seguridad

- No usar datos reales en QA local si no han sido anonimizados.
- No versionar `.env`, backups, dumps, logs ni archivos runtime.
- `v2/scripts/run_local_windows.ps1` debe permanecer sin versionar.
- Las acciones ejecutadas como soporte se autentican con el usuario SuperAdmin; cuando el endpoint audita, queda registrado ese usuario y el tenant objetivo.
