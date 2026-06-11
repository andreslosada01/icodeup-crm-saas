# Data Local Piloto Icodeup Advisors

## 1. Objetivo

Definir la data recomendada para probar Icodeup 360 localmente con PostgreSQL Windows antes de migrar al servidor test. La data debe ser ficticia, idempotente y separada de la demo Andina existente.

## 2. Tenant piloto

Tenant sugerido:

- Nombre: `Icodeup Advisors`
- Slug: `icodeup-advisors-piloto`
- Uso: piloto interno de CRM Collection y preparacion comercial

## 3. Usuarios sugeridos

| Perfil | Cantidad | Proposito |
|---|---:|---|
| SuperAdmin | 1 | Gobierno SaaS global |
| Admin empresa | 1 | Administracion tenant |
| Lider cobranzas | 1 | Equipo, carteras y dashboard |
| Gestores | 5 | Gestion diaria |
| Calidad | 1 | Revision y auditoria operativa |
| Auditor | 1 | Control y trazabilidad |
| Abogado | 1 | Casos juridicos |
| Comercial | 1 | Leads y oportunidades |

Correos recomendados:

- usar dominio `@piloto.local`
- no usar correos reales
- no usar nombres de clientes reales

## 4. Carteras sugeridas

- Cartera Consumo Piloto
- Cartera Preventiva Piloto
- Cartera Juridica Piloto

## 5. Volumen sugerido

| Entidad | Volumen |
|---|---:|
| Clientes | 300 |
| Obligaciones | 500 |
| Gestiones | 300 |
| Promesas | 50 |
| Pagos | 30 |
| Acuerdos | 20 |
| Demograficos | 100 |
| Cargas demo | 3 |
| Repartos demo | 2 |

## 6. Reglas de datos

- documentos ficticios consecutivos, por ejemplo `990000001`
- telefonos ficticios, por ejemplo `3000000001`
- correos `cliente001@piloto.local`
- nombres ficticios o sinteticos
- no cargar cedulas, telefonos, correos ni documentos reales
- no subir soportes reales
- documentos solo como metadata local si se requieren

## 7. Estado actual

El proyecto ya tiene seed demo comercial para tenants como Andina y otros tenants demo. No se debe romper ni duplicar esa demo.

Para el piloto Icodeup Advisors se recomienda crear una funcion separada e idempotente en una fase posterior, por ejemplo:

- `seed_local_pilot_icodeup_advisors(db)`
- activada solo con variable explicita como `ENABLE_LOCAL_PILOT_DATA=true`
- nunca activa por defecto en produccion

## 8. Siguiente paso

Crear seed piloto solo despues de validar PostgreSQL local, migraciones, login demo y flujo de CRM Collection. La funcion debe verificar codigos, slugs, documentos y correos antes de crear registros.
