# Diagnostico Modelo Operativo Cobranzas

## 1. Tenant -> Proyecto -> Usuario -> Cliente

El modelo actual ya soporta la estructura SaaS base:

- `Tenant`: empresa cliente o plataforma Icodeup.
- `Project`: cartera/proyecto dentro del tenant.
- `User`: usuario del tenant con rol legacy y relacion `leader_id`.
- `UserProfile`: perfil SaaS con rol configurable.
- `UserProjectAssignment`: asociacion usuario-proyecto.
- `Customer`: cliente/deudor operativo con `tenant_id`, `project_id` y `assigned_user_id`.

## 2. Entidad obligacion

Antes del ajuste no existia una entidad funcional de obligacion. Solo existia el campo texto `Customer.obligation`.

Brecha: un cliente no podia tener varias obligaciones reales.

## 3. Asignacion de clientes a gestores

Los clientes se asignan por `Customer.assigned_user_id`. El acceso de agente usa `customer_query()` y `customer_for_access()` para limitar al gestor a sus clientes.

## 4. Relacion lider -> agentes

Existe mediante `User.leader_id`. Los usuarios gestores pueden apuntar al coordinador/lider.

## 5. Relacion lider -> proyectos/carteras

Existe `UserProjectAssignment`, reutilizable para lideres, agentes, calidad, abogados o comerciales. No se duplica modelo.

## 6. Relacion usuario -> proyecto/cartera

Existe `UserProjectAssignment` con unicidad usuario/proyecto.

## 7. Filtrado actual de Excel Web

Antes del ajuste, Excel Web filtraba por `tenant_id` para usuarios cliente, pero no tenia alcance fino para gestor/lider. Eso permitia dos riesgos de producto: ocultarlo al gestor o mostrar mas datos de los necesarios.

## 8. Visibilidad por rol antes del ajuste

- SuperAdmin: gobierno global.
- Admin empresa: tenant completo.
- Lider/coordinador: operacion amplia.
- Gestor: clientes asignados en CRM, pero Excel Web no estaba correctamente modelado por alcance.

## 9. Brechas frente a CRM/ERP de cobranzas real

- Falta obligacion como entidad normalizada.
- Excel Web necesitaba alcance por rol, equipo y asignacion.
- Las vistas demo debian diferenciar gestor, lider y admin.
- El menu del gestor debia incluir Excel Web sin abrir grabaciones, integraciones o configuracion.

## 10. Plan de correccion

1. Restaurar Excel Web para gestor.
2. Aplicar scope por rol en `/api/excel-web/query`.
3. Crear `CustomerObligation` aditivo.
4. Crear endpoints minimos de obligaciones.
5. Reutilizar `User.leader_id` y `UserProjectAssignment`.
6. Actualizar bootstrap demo con obligaciones y vistas por rol.
7. Mantener `Customer.balance/dpd/obligation` como resumen legacy.
