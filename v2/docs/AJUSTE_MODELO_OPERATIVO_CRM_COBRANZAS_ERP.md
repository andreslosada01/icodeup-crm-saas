# Ajuste Modelo Operativo CRM Cobranzas ERP

## 1. Modelo SaaS correcto

Icodeup Advisors opera como propietario del SaaS. Cada empresa cliente es un tenant y cada tenant puede tener proyectos/carteras, usuarios, roles, permisos, modulos y datos operativos aislados.

## 2. Empresa -> proyecto/cartera -> lideres/agentes

El ajuste reutiliza:

- `Project` para carteras/proyectos.
- `User.leader_id` para relacion lider -> agente.
- `UserProjectAssignment` para asociar usuarios a carteras.

No se duplicaron modelos ya existentes.

## 3. Cliente -> obligaciones

Se agrego el modelo aditivo `CustomerObligation`.

Un cliente puede tener muchas obligaciones con:

- numero de obligacion,
- producto,
- cartera,
- saldo actual,
- capital/intereses/gastos,
- mora,
- riesgo,
- gestor asignado,
- lider asignado,
- metadata.

`Customer.balance`, `Customer.dpd` y `Customer.obligation` se mantienen como resumen legacy compatible.

## 4. Alcance por rol

Excel Web ahora aplica alcance por rol:

- SuperAdmin: vista plataforma.
- Admin empresa: datos del tenant.
- Lider/coordinador: datos del equipo y carteras asignadas.
- Gestor: solo clientes, obligaciones, gestiones, promesas, pagos, acuerdos, documentos y alertas propias/asignadas.
- Abogado: casos/clientes juridicos asignados.
- Comercial: leads/oportunidades asignadas.

## 5. Excel Web por rol

El gestor vuelve a ver `Mi Excel Web`, pero sin acceso administrativo ni exportacion masiva.

Fuentes de gestor:

- Mis clientes
- Mis obligaciones
- Mis gestiones
- Mis promesas
- Mis pagos
- Mis acuerdos
- Mis alertas
- Mis documentos

Fuentes de lider:

- Clientes del equipo
- Obligaciones del equipo
- Gestiones del equipo
- Promesas del equipo
- Pagos del equipo
- Acuerdos del equipo
- Alertas del equipo

Fuentes de admin empresa:

- Tenant completo
- Cargas
- Demograficos
- Grabaciones si tiene permiso
- Reportes operativos

## 6. Permisos corregidos

Gestor `collections_agent`:

- `excel_web.view`
- `excel_web.query`
- `excel_web.views.manage`
- sin `excel_web.export`
- sin `recordings.view`
- sin integraciones/configuracion/gobierno

## 7. Flujos de cartera/reparto

El bootstrap demo crea clientes, asignaciones, demograficos, promesas, pagos, acuerdos y obligaciones por cliente. Las cargas/repartos quedan preparadas para evolucionar hacia creacion masiva de obligaciones.

## 8. Que puede ver gestor

- Inicio
- Mi operacion
- Clientes asignados
- Promesas
- Pagos
- Acuerdos
- Documentos operativos
- Mi Excel Web limitado
- Alertas

No ve gobierno, integraciones, configuracion, grabaciones, auditoria global, usuarios ni roles.

## 9. Que puede ver lider

- Dashboard equipo
- Clientes y obligaciones del equipo
- Promesas/pagos/acuerdos del equipo
- Excel Web de equipo
- Reportes permitidos
- Alertas del equipo

## 10. Que puede ver admin empresa

- Administracion del tenant
- Usuarios/proyectos/roles
- Cargas/repartos
- Configuracion
- Mi Excel Web tenant
- Integraciones y grabaciones si el modulo y permiso estan activos

## 11. Riesgos pendientes

- Las cargas CSV todavia deben evolucionar para crear obligaciones desde archivo.
- ManagementActivity aun no tiene `obligation_id`; la gestion sigue a nivel cliente.
- Export CSV real para gestor queda deshabilitado por seguridad.
- Las pruebas integradas completas siguen protegidas por variables de entorno.

## 12. Proximos pasos

1. Agregar `obligation_id` nullable en gestiones, promesas, pagos y acuerdos.
2. Mapear cargas/repartos a obligaciones.
3. Crear UI especifica de obligaciones en el drawer del cliente.
4. Agregar reportes de productividad por lider/equipo.
5. Habilitar export limitado por alcance con auditoria reforzada.
