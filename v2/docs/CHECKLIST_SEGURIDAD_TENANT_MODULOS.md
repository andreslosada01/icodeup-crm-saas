# Checklist Seguridad Tenant y Modulos

## Autenticacion

- Login exitoso retorna token y datos de tenant.
- Login fallido retorna 401.
- Usuario inactivo no puede iniciar sesion.
- Token invalido no permite acceder a APIs protegidas.

## Tenant

- Usuario cliente solo consulta registros de su `tenant_id`.
- Admin empresa no puede consultar datos de otra empresa usando parametros por URL.
- Agent solo ve clientes asignados cuando aplica.
- Platform admin puede ver gobierno global.
- Admin empresa no puede acceder a `/api/admin/tenants`.

## Modulos

- Modulo activo aparece en `/api/menu/me`.
- Modulo inactivo no aparece en `/api/menu/me`.
- Acceso por URL a modulo inactivo retorna 403.
- Rutas de CRM validan modulo `crm`.
- Rutas juridicas validan modulo `legal`.
- Rutas documentales validan modulo `documents`.
- Rutas comerciales validan modulo `sales`.

## Permisos

- Menu respeta `required_permission_code`.
- Platform admin tiene permisos globales.
- Admin empresa ve solo menu de empresa.
- Lider ve menu operativo autorizado.
- Usuario operativo ve solo su operacion.

## Auditoria

- Crear usuario registra auditoria.
- Crear cliente registra auditoria.
- Importar clientes registra auditoria.
- Crear promesa registra auditoria.
- Crear pago registra auditoria.
- Crear acuerdo registra auditoria.
- Crear documento registra auditoria.
- Crear lead registra auditoria.
- Crear oportunidad registra auditoria.

## Frontend

- Menu lateral se construye desde `/api/menu/me`.
- No se muestran modulos no autorizados.
- Dashboard inicial cambia por tipo de usuario.
- Login usa posicionamiento Icodeup 360 y no textos de cobranzas.
- Branding aplica colores de tenant cuando existen.

## Regresion

- Dashboard CRM existente carga.
- Cola de gestion carga.
- Clientes carga.
- Promesas carga.
- Pagos carga.
- Acuerdos responde.
- Juridico responde.
- Documentos responde.
- Ventas responde.
- Reportes BI responde.
