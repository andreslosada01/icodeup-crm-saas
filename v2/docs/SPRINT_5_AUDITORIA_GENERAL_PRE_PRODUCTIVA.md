# Sprint 5 - Auditoria general pre-productiva

## Resumen ejecutivo

Icodeup 360 se encuentra en una etapa avanzada de SaaS pre-productivo. El producto tiene core multiempresa, autenticacion, roles/permisos, menu dinamico, modulos de cobranza, juridico, documentos, ventas, Excel Web, cargas, repartos, equipos, alertas, integraciones demo, auditoria y datos demo comerciales. El objetivo de este sprint fue estabilizar lo existente para una primera salida controlada a servidor de test, sin agregar modulos grandes ni romper compatibilidad legacy.

## Estado funcional actual

| Area | Estado | Observacion |
| --- | --- | --- |
| Login y sesiones | Funcional | Requiere rotacion de secretos y passwords fuera de demo antes de produccion. |
| Menu dinamico | Funcional | Filtra por audiencia, modulo activo y permiso. |
| Gobierno SaaS | Funcional | Visible para platform admin. |
| Administracion empresa | Funcional | Usuarios, roles, permisos, modulos, equipos, branding y auditoria tenant. |
| Cobranzas | Funcional | Clientes, cola, gestiones, promesas, pagos y acuerdos. |
| Obligaciones | Funcional | Listados, asignaciones y alcance por rol/equipo. |
| Cargas/repartos | Funcional | Preview, confirmacion, lotes y descargas de resultado/error. |
| Demograficos | Funcional | Registro y consulta acotada a 20 filas por pagina. |
| Excel Web | Funcional | Query, edicion de hoja operativa y vistas guardadas. |
| Juridico | Base funcional | Casos, actuaciones, deadlines, hearings y dashboard. |
| Documentos | Base funcional | Metadata documental, no binarios reales. |
| Ventas | Base funcional | Leads, oportunidades, dashboard y pipeline. |
| Alertas/integraciones | Base funcional | Parametrizacion y eventos con alcance tenant. |
| Auditoria | Funcional | Cobertura amplia, aun requiere politicas de retencion. |
| Alembic | Funcional | Baseline y migraciones incrementales no destructivas. |

## Modulos terminados para produccion controlada

- Core SaaS multiempresa.
- Autenticacion y perfiles por rol.
- Administracion de usuarios, roles, permisos y equipos.
- CRM/cobranzas operativo.
- Promesas, pagos y acuerdos.
- Cargas CSV/repartos/demograficos.
- Excel Web operativo.
- Auditoria y gobierno SaaS basico.
- Data demo idempotente.

## Modulos parcialmente funcionales

- Juridico: base operativa lista para piloto, falta calendario juridico avanzado, adjuntos binarios y flujos procesales profundos.
- Documentos: metadata lista, falta storage productivo, antivirus, versionado y firmas.
- Ventas: base CRM comercial, falta automatizacion, scoring y forecast avanzado.
- Integraciones: configuracion demo lista, falta conexion productiva WhatsApp/email/telefonia.
- BI: dashboards ejecutivos listos para demo, falta motor configurable por tenant.

## Modulos que no deben venderse como completos aun

- RH, finanzas e industrial: solo deben presentarse como roadmap modular futuro.
- IA avanzada: no debe prometerse como motor productivo hasta tener modelos, trazabilidad y evaluacion.
- Telefonia embebida/WebRTC productiva: requiere PBX/SIP, seguridad y proveedores reales.
- Storage documental productivo: requiere configuracion externa y politicas de retencion.

## Riesgos criticos

- Produccion no debe cargar data demo ni usar credenciales demo.
- Se debe configurar SECRET_KEY fuerte y CORS restrictivo.
- Los uploads no deben persistir archivos reales dentro del repositorio.
- Se requiere backup/restore probado antes de clientes reales.

## Riesgos medios

- Frontend sigue siendo HTML/CSS/JS monolitico; mantenible para piloto, pero conviene modularizar en una fase posterior.
- Juridico/documentos/ventas son MVP funcionales; deben venderse con alcance claro.
- Auditoria requiere politica de retencion y exportes controlados.
- Algunos endpoints historicos mantienen fallback legacy de User.role.

## Riesgos bajos

- Algunos textos pueden pulirse para verticales fuera de cobranzas.
- Hay placeholders de producto en modulos futuros.
- Los reportes BI deben tener mas configurabilidad por tenant en siguientes fases.

## Recomendaciones de estabilizacion

1. Ejecutar QA visual por rol despues de reiniciar el servicio local o servidor de test.
2. Mantener tablas operativas con maximo 20 filas por pagina.
3. No activar modulos futuros en tenants productivos hasta completar su alcance.
4. Bloquear data demo en produccion con ENABLE_DEMO_DATA=false y ENABLE_DEMO_SEEDS=false.
5. Configurar backups diarios y restore semanal hacia test.
6. Revisar logs y auditoria antes de abrir acceso a clientes reales.

## Checklist para pasar a main

- `compileall` backend OK.
- `node --check` frontend OK.
- `alembic upgrade head` OK.
- `alembic current` en head.
- `pytest` seguro OK.
- Integracion con demo OK si el servicio local esta activo.
- Health OK.
- Sin `.env`, bases locales, logs ni archivos reales versionados.
- Rama limpia y commit creado.

## Checklist para desplegar en servidor

- Crear servidor test primero.
- Instalar Python, PostgreSQL, Nginx y certificados TLS.
- Crear usuario Linux no root para la app.
- Configurar variables de entorno.
- Ejecutar Alembic.
- Desactivar seeds demo en produccion.
- Configurar systemd.
- Configurar Nginx y HTTPS.
- Ejecutar healthcheck.
- Crear backup inicial.
- Ejecutar smoke test por rol.
