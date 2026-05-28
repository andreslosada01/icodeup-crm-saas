# Cambios Base de Datos V2 Product Hardening

Fecha: 2026-05-28  
Rama: `feature/product-hardening-collection-legal-crm`

## Politica aplicada

- No se eliminaron tablas.
- No se eliminaron columnas existentes.
- No se hicieron migraciones destructivas.
- Los modelos nuevos son aditivos.
- Los tenants sin plan o modulos configurados conservan comportamiento permisivo.
- Para produccion se recomienda convertir estos cambios a migraciones Alembic versionadas antes de desplegar.

## Tablas nuevas

### SaaS comercial

- `saas_plans`
- `tenant_subscriptions`
- `tenant_modules`

### Cobranzas

- `payment_agreements`
- `payment_agreement_installments`

### Juridico

- `legal_cases`
- `legal_actions`
- `legal_hearings`
- `legal_deadlines`

### Documentos

- `documents`

### Ventas

- `leads`
- `opportunities`

### Auditoria

- `audit_logs`

## Impacto operativo esperado

- La operacion actual de clientes, promesas, pagos, cola, BI, canales y tipificaciones no cambia.
- `Base.metadata.create_all` crea las tablas nuevas en desarrollo local.
- No hay restricciones duras de plan/modulo todavia.
- Los endpoints nuevos validan tenant y rol para evitar acceso cruzado.

## Recomendacion para test y produccion

1. Crear revision Alembic con estas tablas.
2. Probar migracion en base de test con copia anonima.
3. Ejecutar checklist de regresion.
4. Habilitar modulos por tenant gradualmente.
5. Agregar indices adicionales si el volumen real supera la data demo.
