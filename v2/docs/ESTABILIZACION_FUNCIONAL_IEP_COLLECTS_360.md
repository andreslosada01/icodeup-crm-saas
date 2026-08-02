# Estabilizacion funcional IEP / Collects 360

## Alcance de esta iteracion

Esta iteracion deja alineada la regla transversal de paginacion visible a 10 registros por pagina y agrega una prueba estatica para evitar regresiones. No incluye cambios de datos, seeds, modelos ni migraciones.

## Diagnostico de brechas

1. Paginacion global: corregida en frontend y endurecida en endpoints de listados visibles con `limit` o `page_size`. Los calculos agregados pueden seguir usando ventanas internas mayores, siempre que no rendericen tablas completas.
2. Fuente principal por entidad: el cliente debe mantenerse como ficha principal. Obligaciones, pagos, promesas, acuerdos y gestiones pueden existir en vistas especializadas, pero deben enlazar de vuelta al cliente y a la obligacion cuando aplique.
3. Telefonia: existe base para proveedores, extensiones, CallLog y click-to-call seguro/simulado. Falta completar la activacion operativa con IpCom TEST/prod, AMI real, consulta externa de grabaciones y auditoria de acceso sobre reproducciones.
4. Obligaciones multiples: la estructura ya contempla obligacion asociable a cliente. Falta reforzar flujos de seleccion de obligacion en pagos, promesas, acuerdos, gestiones y reportes con pruebas por rol.
5. Cargas flexibles: existe flujo de batches, preview, mapeo y errores. Faltan completar XLSX, sinonimos amplios por tipo de archivo, idempotencia por fuente externa y soporte completo para campanas, tareas y repartos.
6. Aislamiento multiempresa: hay pruebas y filtros por tenant/rol en modulos criticos. Falta matriz E2E completa por SuperAdmin, Admin empresa, Lider, Gestor y Auditor para pagos, grabaciones, cargas, reportes y exportes.
7. Repartos y campanas: existen asignaciones por cartera/equipo. Falta flujo masivo de campana con seleccion de gestores, distribucion balanceada, trazabilidad y seguimiento por coordinador.
8. Productividad y efectividad: hay tableros base. Falta consolidar metricas hora a hora, comparativo de equipo, cumplimiento por cartera y filtros avanzados por campana/asesor/fecha.
9. PayControl 360: la vista local debe evolucionar a integracion API con App Pagos. Falta adapter, idempotencia por referencia externa, sincronizacion, soportes y fallback.
10. QAudit 360: pendiente adapter/API para enviar llamadas o gestiones a auditoria, consultar resultados y asociar evaluacion a asesor, llamada, cliente, obligacion y gestion.
11. Grabaciones: existe modulo base. Falta integracion con PBX/almacenamiento externo, filtros completos, permisos finos y auditoria de reproduccion/descarga.
12. Branding corporativo: IEP e Icodeup Advisors deben permanecer como marca madre, permitiendo branding por tenant sin ocultar la identidad base cuando aplique.

## Plan por fases

### Fase 0 - Control de rendimiento visible

- Mantener todas las tablas y listados visibles en 10 registros por pagina.
- Validar `table()` en frontend y defaults/caps backend de listados visibles.
- Ejecutar pruebas `safe_static` en cada entrega.

### Fase 1 - Arquitectura de informacion operativa

- Definir la ficha de cliente como fuente principal.
- Enlazar obligaciones, pagos, promesas, acuerdos y gestiones desde la ficha.
- Evitar duplicados visuales sin contexto y conservar accesos especializados para reporteria.

### Fase 2 - Obligaciones y gestion diaria

- Hacer obligatoria la seleccion de obligacion cuando el flujo lo requiera.
- Asociar actividades, pagos, promesas y acuerdos a cliente completo u obligacion especifica.
- Agregar pruebas de tenant, proyecto, lider, gestor y cartera.

### Fase 3 - Cargas, repartos, campanas y tareas

- Completar CSV/XLSX con preview, sinonimos, mapeo flexible, errores descargables e idempotencia.
- Agregar campanas con seleccion de gestores, distribucion balanceada y trazabilidad.
- Medir avance, cumplimiento y tareas por coordinador.

### Fase 4 - Telefonia y grabaciones

- Registrar proveedor IpCom demo en TEST y proveedor IpCom productivo en produccion desde configuracion segura.
- Mantener click-to-call simulado en TEST.
- Mantener produccion en modo seguro hasta tener credenciales AMI fuera del repo.
- Integrar grabaciones por llamada, cliente, asesor, campana, cartera y fecha.

### Fase 5 - Integraciones IEP

- PayControl 360: adapter con App Pagos, idempotencia, estados, soportes, auditoria y fallback.
- QAudit 360: adapter de auditoria, envio de gestiones/llamadas, consulta de resultados e indicadores.

### Fase 6 - Analytics 360 y QA funcional

- Construir reportes configurables por recaudo, promesas, efectividad, mora, riesgo, cartera, campana, asesor y contactabilidad.
- Validar aislamiento tenant y permisos con pruebas automatizadas e inspeccion manual por rol.

## Comandos para TEST

Ejecutar desde el servidor TEST, sin seeds productivos:

```bash
cd /opt/icodeup360_test/app
git fetch origin
git checkout feature/deploy-test-server
git pull --ff-only
cd v2/backend
python -m compileall app
alembic upgrade head
pytest -m safe_static
cd ..
node --check frontend/static/assets/app.js
```

Reiniciar solo el servicio TEST configurado en el servidor, usando el nombre real del servicio:

```bash
sudo systemctl restart icodeup360-test
sudo systemctl status icodeup360-test --no-pager
```

## Comandos para produccion

Antes de aplicar, tomar backup operativo y confirmar ventana de despliegue. No ejecutar seeds automaticamente:

```bash
cd /opt/icodeup360/app
git fetch origin
git checkout feature/deploy-test-server
git pull --ff-only
cd v2/backend
python -m compileall app
alembic upgrade head
pytest -m safe_static
cd ..
node --check frontend/static/assets/app.js
```

Reiniciar solo el servicio productivo configurado en el servidor, usando el nombre real del servicio:

```bash
sudo systemctl restart icodeup360
sudo systemctl status icodeup360 --no-pager
```

## Checklist QA

- SuperAdmin: ingresa a Gobierno SaaS IEP, ve empresas, usuarios, roles, modulos, auditoria y salud del sistema.
- SuperAdmin soporte operativo: cambia alcance operativo sin perder menu ni aislamiento.
- Admin empresa: solo ve su tenant, configura usuarios, carteras, telefonia, cargas y reportes permitidos.
- Lider/coordinador: ve equipo, cartera asignada, ranking, productividad, cola y seguimiento.
- Gestor: ve solo su cola, clientes asignados, gestiones, promesas, acuerdos y click-to-call permitido.
- Calidad/auditor: accede a grabaciones/evaluaciones permitidas sin ver otros tenants.
- Carga clientes: preview, mapeo, confirmacion, errores descargables y auditoria.
- Carga obligaciones: asociacion a tenant, cartera, cliente y saldo correcto.
- Carga demograficos: telefonos, emails, direcciones y score sin duplicidad confusa.
- Carga pagos: idempotencia, referencia, soporte y asociacion a cliente/obligacion.
- Reparto: asignacion activa unica, trazabilidad y balance por gestor.
- Campana/tarea: carga N registros, selecciona gestores, distribuye, mide avance y cumplimiento.
- Cola de gestion: maximo 10 registros visibles por pagina y filtros por rol.
- Cliente: ficha principal con obligaciones, historial, pagos, promesas, acuerdos y actividades.
- Promesa: creacion, estado, cumplimiento y asociacion a obligacion cuando aplique.
- Pago: registro/consulta por PayControl 360 y validacion de tenant/proyecto.
- Acuerdo: cuotas, estado y trazabilidad de gestion.
- Telefonia: proveedor, extension, click-to-call simulado en TEST, CallLog y bloqueo seguro si falta configuracion.
- Grabaciones: filtros, permisos, auditoria de acceso y no cruce de tenants.
- Reportes/Analytics 360: filtros por fecha, cartera, campana, asesor, estado y exportes permitidos.
- Exportes: solo roles autorizados, con auditoria y limites seguros.

## Migraciones

No se requieren migraciones en esta iteracion.
