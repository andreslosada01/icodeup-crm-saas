# Revision Pre-Merge Fase 5 - Demo Comercial

## 1. Resumen ejecutivo

La Fase 5 fue revisada sobre la rama `feature/phase-5-demo-commercial-data`. El objetivo de la fase se cumple: Icodeup 360 cuenta con una historia demo comercial end-to-end, datos ficticios consistentes, bootstrap idempotente, usuarios demo, tenants demo, documentacion comercial y una senal visual de entorno demo.

No se encontraron riesgos criticos ni evidencia de datos reales en la data creada por Fase 5. La rama queda lista para abrir PR hacia `main` con observaciones menores no bloqueantes.

## 2. Estado de rama

- Rama activa: `feature/phase-5-demo-commercial-data`.
- Rama destino: `main`.
- Commit principal revisado: `e39295d feat: add commercial demo data scenario`.
- Diferencia contra `origin/main`: `0 1`; la rama esta 1 commit por delante.
- Diferencia contra `origin/feature/phase-5-demo-commercial-data`: `0 0`; rama sincronizada con remoto.
- Cambios locales pendientes al iniciar revision: ninguno.

Archivos de Fase 5 contra `origin/main`:

- `v2/backend/app/core/config.py`
- `v2/backend/app/services/bootstrap_service.py`
- `v2/frontend/static/index.html`
- `v2/frontend/static/assets/app.js`
- `v2/frontend/static/assets/styles.css`
- `v2/docs/CONFIGURACION_DATA_DEMO_V2.md`
- `v2/docs/DIAGNOSTICO_DATA_DEMO_FASE_5.md`
- `v2/docs/ESCENARIO_DEMO_COMERCIAL_FASE_5.md`
- `v2/docs/FLUJOS_END_TO_END_DEMO_FASE_5.md`
- `v2/docs/GUION_DEMO_COMERCIAL_ICODEUP_360.md`
- `v2/docs/REVISION_FASE_5_DEMO_COMERCIAL.md`

## 3. Validaciones ejecutadas

- `git status --short --branch --untracked-files=all`: limpio.
- `git fetch origin`: OK.
- `git rev-list --left-right --count origin/main...feature/phase-5-demo-commercial-data`: `0 1`.
- `python -m compileall .\v2\backend\app` usando el Python del entorno virtual: OK.
- `node --check .\v2\frontend\static\assets\app.js` usando runtime Node disponible: OK.
- `alembic current`: OK, revision `20260528_0001 (head)`.
- `pytest`: OK en modo seguro; 23 pruebas omitidas por requerir `ICODEUP_RUN_INTEGRATION_TESTS=1` y base segura.
- `GET http://127.0.0.1:8020/api/health`: OK.

## 4. Resultado de pruebas

Las pruebas automatizadas no fallaron. El modo seguro de `pytest` omite las pruebas de integracion por diseno, segun la configuracion actual del proyecto.

Smoke HTTP con la app FastAPI:

- Login demo SuperAdmin: OK.
- Login demo Admin Andina: OK.
- Login demo Coordinador: OK.
- Login demo Gestor 1 y Gestor 2: OK.
- Login demo Supervisor Calidad: OK.
- Login demo Abogado: OK.
- Login demo Comercial: OK.
- Menu dinamico por rol: OK.
- Dashboard por rol: OK.
- Clientes, promesas, pagos, acuerdos, documentos y ventas: OK.
- Juridico para admin/abogado: OK.
- BI para admin: OK.

## 5. Validacion de data demo

Conteos verificados para `andina-servicios-financieros`:

- Clientes: 60.
- Gestiones: 90.
- Promesas: 32.
- Pagos: 15.
- Acuerdos: 10.
- Casos juridicos: 10.
- Documentos metadata: 38.
- Leads: 6.
- Oportunidades: 6.

Tenants demo revisados:

- `andina-servicios-financieros`: 7 usuarios, 4 proyectos, 9 modulos activos, 1 suscripcion.
- `legal-recovery-group-demo`: 1 usuario, 2 proyectos, 5 modulos activos, 1 suscripcion.
- `cooperativa-horizonte-demo`: 1 usuario, 1 proyecto, 5 modulos activos, 1 suscripcion.

Idempotencia:

- Ejecutar bootstrap con `ENABLE_DEMO_DATA=true` dos veces mantiene los conteos sin duplicacion masiva.
- Ejecutar bootstrap con `ENABLE_DEMO_DATA=false` y `ENABLE_DEMO_SEEDS=false` mantiene los conteos sin crear data demo adicional.

## 6. Validacion de usuarios demo

Usuarios validados con login exitoso:

- `superadmin@demo.icodeup.local`
- `admin.andina@demo.icodeup.local`
- `coord.cobranzas.andina@demo.icodeup.local`
- `gestor1.andina@demo.icodeup.local`
- `gestor2.andina@demo.icodeup.local`
- `calidad.andina@demo.icodeup.local`
- `abogado.andina@demo.icodeup.local`
- `comercial.andina@demo.icodeup.local`

Contrasena demo documentada: `Demo360!2026`.

## 7. Validacion por rol

SuperAdmin Icodeup:

- Ve Gobierno SaaS, empresas, planes, suscripciones, modulos, usuarios, proyectos, tipificaciones, auditoria y salud del sistema.
- Puede consultar governance, tenants, exportes y modulos globales.

Admin Andina:

- Ve dashboard, Mi Empresa, usuarios, roles/permisos, modulos contratados, branding, clientes, terceros, cola, promesas, pagos, acuerdos, juridico, documentos, ventas, reportes, canales y auditoria tenant.
- No accede a endpoints globales `admin/tenants` ni `tenants`.

Gestor:

- Ve dashboard, cola, clientes, tareas, promesas, pagos, acuerdos y documentos.
- Ve 30 clientes asignados de los 60 de Andina.
- Puede consultar acuerdos en lectura.
- No puede exportar clientes ni pagos.
- No accede a gobierno SaaS, auditoria ni tenants.
- No puede consultar actividades de clientes asignados a otro gestor.

Abogado:

- Login OK.
- Accede a juridico y vencimientos.
- No accede a gobierno SaaS.
- Observacion: usa rol legacy `coordinator` por compatibilidad, por lo que conserva visibilidad operacional amplia.

Comercial:

- Login OK.
- Accede a ventas, leads y oportunidades.
- No accede a gobierno SaaS.
- Observacion: usa rol legacy `coordinator` por compatibilidad, por lo que conserva visibilidad operacional amplia.

## 8. Validacion multi-tenant

Controles verificados:

- Admin Andina lista 60 clientes de Andina.
- Gestor 1 lista 30 clientes asignados.
- Gestor 1 recibe 403 al consultar actividades de un cliente asignado a Gestor 2.
- Admin Legal Recovery recibe 403 en clientes por no tener modulo CRM/collections habilitado.
- Admin Cooperativa lista 0 clientes propios y no ve clientes de Andina.
- Admin Legal Recovery y Cooperativa reciben 403 al intentar acceder a un caso juridico de Andina por ID.
- Admin Legal Recovery recibe 403 al intentar acceder a un documento de Andina por ID.
- Exportes de clientes y pagos requieren permisos; agente recibe 403.

Resultado: no se detecto fuga multi-tenant en los flujos revisados.

## 9. Validacion de dashboards

Validado por endpoint y data disponible:

- Dashboard general responde para usuarios demo.
- Clientes, cartera, promesas, pagos y acuerdos tienen datos.
- BI responde para Admin Empresa.
- Juridico responde para Admin Empresa y Abogado.
- Documentos responde con metadatos demo.
- Ventas responde con leads y oportunidades.
- Planes, suscripciones y modulos estan poblados para la demo.

La validacion visual en navegador no se pudo automatizar mediante el plugin de navegador por una falla de runtime local, pero se confirmo que:

- `index.html` contiene `demoModeBadge`.
- `app.js` contiene `isDemoContext()` y alterna la visibilidad del badge.
- `styles.css` define `demo-mode-badge`.
- El asset servido en `http://127.0.0.1:8020/assets/app.js` contiene el codigo de Fase 5.

## 10. Riesgos criticos

No se encontraron riesgos criticos.

## 11. Riesgos medios

- El entorno local revisado carga `ENABLE_DEMO_SEEDS=true`; aunque el codigo permite apagar la demo, en produccion se debe asegurar `ENABLE_DEMO_DATA=false` y `ENABLE_DEMO_SEEDS=false`.
- Los perfiles Abogado y Comercial usan rol legacy `coordinator`, por compatibilidad con la arquitectura actual. Esto les da mas visibilidad operacional de la ideal para una segmentacion comercial final, aunque no les da acceso a Gobierno SaaS.
- `pytest` en modo seguro omite pruebas de integracion; antes de produccion conviene correr suite con `ICODEUP_RUN_INTEGRATION_TESTS=1` sobre base aislada.

## 12. Riesgos bajos

- El badge usa texto ASCII `Data ficticia de demostracion`; es claro, pero se podria ajustar ortografia visual en una fase de copy/pulido si se permite Unicode en frontend.
- Documentos son metadatos ficticios, no archivos reales. Correcto para esta fase, pero debe explicarse durante demos.
- Algunos modulos base siguen siendo MVP/placeholder visual-operativo.

## 13. Correcciones aplicadas

Durante esta revision no se aplicaron correcciones de codigo. La revision confirma el commit `e39295d` tal como fue subido.

## 14. Decision final

**Listo para PR** hacia `main`, con observaciones no bloqueantes.

No se recomienda hacer merge directo sin PR si se quiere conservar trazabilidad de revision, pero tecnicamente la rama esta en condiciones de integrarse.

## 15. Recomendacion para merge a main

Abrir PR desde:

`feature/phase-5-demo-commercial-data`

hacia:

`main`

Checklist previo al merge:

- Confirmar que `.env` productivo tenga `ENABLE_DEMO_DATA=false` y `ENABLE_DEMO_SEEDS=false`.
- Confirmar que no se suben bases locales, logs, media ni documentos reales.
- Revisar visualmente el badge demo en navegador antes de presentar a cliente.
- Mantener la contrasena demo solo para ambientes demo/controlados.

## 16. Recomendacion para siguiente fase

Fase 6 sugerida: pulido comercial final y empaquetamiento de demo.

Prioridades:

- Crear script/guia operativa para levantar ambiente demo con `ENABLE_DEMO_DATA=true`.
- Agregar screenshots de demo comercial.
- Refinar permisos especificos para perfiles juridico y comercial sin depender de `coordinator`.
- Preparar dataset adicional para Legal Recovery y Cooperativa si se quieren demos por vertical.
- Ejecutar pruebas de integracion en base aislada antes del merge final a produccion.
