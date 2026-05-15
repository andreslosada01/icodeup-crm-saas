# IcodeUp CRM

Primera version funcional de un CRM de cobranzas corporativo, multiempresa y preparado para evolucionar a SaaS.

## Como usarlo con base de datos y login

Ejecuta en PowerShell:

```powershell
.\run-crm.ps1
```

Luego abre:

```text
http://127.0.0.1:8010
```

Las bases SQLite se crean automaticamente asi:

- Plataforma IcodeUp: `data/platform.sqlite3`.
- Empresas cliente: `data/tenants/<empresa>.sqlite3`.
- Base anterior de trabajo local: `data/icodeup_crm.sqlite3`, conservada como origen de migracion.

Usuarios demo:

- Plataforma IcodeUp: `platform@icodeup.com` / `Platform123!`
- `super@pepeperez.com` / `Super123!`
- `admin@pepeperez.com` / `Admin123!`
- `lider@pepeperez.com` / `Lider123!`
- `gestor@pepeperez.com` / `Gestor123!`
- `calidad@pepeperez.com` / `Calidad123!`
- `super@martinez.com` / `Super123!`
- `admin@martinez.com` / `Admin123!`
- `lider@martinez.com` / `Lider123!`
- `gestor@martinez.com` / `Gestor123!`
- `calidad@martinez.com` / `Calidad123!`

## Modulos incluidos

- Tablero ejecutivo con saldo vencido, recuperado, promesas y riesgo.
- Cola de gestion con filtros por agente, estado y riesgo.
- Expediente 360 del cliente con bitacora, acciones rapidas y seguimiento.
- Registro de promesas de pago y cambio automatico de vencidas.
- Registro de pagos con actualizacion de saldo.
- Campanas multicanal por segmento.
- Reportes de recuperacion por agente, embudo e insights gerenciales.
- Modulo BI ejecutivo con graficos de recuperacion, riesgo, carteras, equipo y aging.
- Configuracion de meta mensual, alertas y mora critica.
- Exportacion CSV de cartera.
- Persistencia local usando `localStorage`.
- Backend local con SQLite, sesiones, empresas y roles.
- Arquitectura SaaS local con base de plataforma y una base tenant por empresa cliente.
- Acceso SaaS: la empresa se autodetecta por el usuario y cada cliente ve solo su entorno.
- Modulo Empresas para que IcodeUp plataforma cree empresas contratantes, proyectos y usuarios tenant.
- Inventario general para IcodeUp plataforma con usuarios, proyectos y clientes por empresa.
- Arbol de tipificaciones por empresa.
- Omnicanalidad inicial con click to call, WhatsApp y email.
- Configuracion administrativa de lineas WhatsApp, correos y telefonia futura por empresa.
- Carga de repartos por CSV con cartera, lider y gestor.
- Modulo Usuarios para crear usuarios, asignar lideres y asociarlos a carteras/proyectos.

## Siguiente evolucion recomendada

- Backend con usuarios, roles, permisos y auditoria inmutable.
- Base de datos relacional para clientes, obligaciones, pagos, gestiones y promesas.
- Integracion con telefonia, WhatsApp Business, email, SMS y pasarelas de pago.
- Carga masiva de cartera por Excel/CSV.
- Motor de reglas para segmentacion, prioridad y asignacion de gestores.
- Cumplimiento: habeas data, consentimiento, horarios permitidos y trazabilidad legal.

Ver tambien `PLAN_PRODUCCION.md`.

Ver estructura tecnica en `ARQUITECTURA.md`.

Ver criterios corporativos en `ESTANDARES_CORPORATIVOS.md`.

Ver modelo SaaS multiempresa en `SAAS_MULTIEMPRESA.md`.
