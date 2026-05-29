# Diagnostico Data Demo Fase 5 - Icodeup 360

## 1. Datos demo existentes hoy

El proyecto ya tiene dos mecanismos relacionados con demo:

- `v2/backend/app/services/bootstrap_service.py`: inicializa el core SaaS, modulos, planes, permisos, menu, tenant plataforma, configuracion por tenant y perfiles de usuario.
- `v2/backend/app/seeds/scale_demo.py`: script independiente para generar tenants, proyectos, usuarios, clientes, gestiones, promesas y pagos de prueba.

En la base local revisada existen datos demo operativos: tenants, proyectos, usuarios, clientes, gestiones, promesas y pagos. No existe aun data consistente para acuerdos, juridico, documentos, ventas ni suscripciones SaaS.

## 2. Usuarios demo existentes hoy

El script `scale_demo.py` crea usuarios por proyecto con patrones:

- `admin.<tenant>@demo.icodeup.local`
- `coord.<tenant>.<project>@demo.icodeup.local`
- `calidad.<tenant>.<project>@demo.icodeup.local`
- `agente<n>.<tenant>.<project>@demo.icodeup.local`

El bootstrap principal crea o sincroniza el usuario plataforma configurado por entorno, pero no crea un set comercial de usuarios demo end-to-end.

## 3. Tenants demo existentes hoy

En la base local hay tenants demo o de prueba como:

- `icodeup-platform`
- `andina-servicios`
- `inversiones-horizonte`
- `grupo-atlas-financiero`
- `empresa-piloto-v2`

Para la demo comercial se recomienda crear un escenario principal mas claro: `Andina Servicios Financieros S.A.S.`.

## 4. Modulos demo existentes hoy

El core ya registra modulos:

- core
- administration
- crm
- collections
- legal
- documents
- sales
- bi
- integrations
- hr
- finance
- industrial

Tambien existen `TenantModule`, pero el bootstrap anterior habilita un conjunto amplio por defecto. La demo comercial necesita estados de modulos por tenant mas intencionales.

## 5. Gaps para demo comercial

- No hay suscripciones demo consistentes por tenant.
- No hay acuerdos de pago con cuotas demo.
- No hay casos juridicos, actuaciones, audiencias ni vencimientos demo.
- No hay documentos demo asociados a clientes, acuerdos o casos.
- No hay leads ni oportunidades demo.
- No hay un escenario comercial end-to-end claramente documentado.
- No hay indicador visual de que la informacion es ficticia/demo.
- Los datos masivos existentes no cuentan una historia comercial unica.

## 6. Riesgos de datos sensibles

- No se deben usar nombres, documentos, telefonos, correos o documentos reales.
- No se deben subir archivos fisicos de soporte.
- No se debe versionar base local, logs ni `.env`.
- La carga demo debe poder desactivarse en produccion.

## 7. Recomendaciones de data demo

- Usar `ENABLE_DEMO_SEEDS=true` solo en ambientes locales/demo.
- Crear datos idempotentes por slug, email, documento, codigo de proyecto y rutas documentales ficticias.
- Usar documentos secuenciales tipo `900100001`.
- Usar telefonos ficticios tipo `3000000001`.
- Usar correos `@demo.icodeup.local` para usuarios y `@demo.local` para clientes.
- Mantener storage documental como metadato ficticio, sin archivos reales.

## 8. Escenarios comerciales sugeridos

Escenario principal:

- Tenant: `Andina Servicios Financieros S.A.S.`
- Vertical: Collection & Legal CRM.
- Proyectos: consumo castigado, microcredito, tarjeta privada y cartera judicializada.
- Usuarios: SuperAdmin, Admin Empresa, Coordinador, Gestores, Supervisor Calidad, Abogado y Analista Comercial.
- Recorrido: gobierno SaaS, administracion tenant, operacion de cobranza, acuerdo, pago, juridico, documentos, ventas y BI.

Escenarios secundarios:

- `Legal Recovery Group Demo`: firma legal con juridico, documentos y BI.
- `Cooperativa Horizonte Demo`: cooperativa con cobranzas y BI en plan Starter.
