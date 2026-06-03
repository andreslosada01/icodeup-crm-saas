# Diagnostico Funcional Real Fase 8C

## 1. Pantallas solo informativas

En la revision visual de Fase 8B se identificaron pantallas con datos y KPIs, pero sin operacion suficiente para usuarios reales:

- Centro de Configuracion.
- Integraciones y canales.
- Cargas y repartos.
- Mi Excel Web.
- Grabaciones.
- Arboles de gestion.
- Perfil operativo de gestion embebido.

## 2. Botones sin accion real

Los botones principales requerian feedback operativo mas claro:

- Guardar gestion no mostraba loading, toast ni error visible.
- Integraciones no permitia crear/editar/probar desde UI.
- Cargas no guiaba seleccion de archivo, preview y confirmacion.
- Mi Excel Web no permitia armar consulta, guardar vista y exportar desde UI.
- Grabaciones no exponia acciones auditables de detalle, playback o descarga.

## 3. Formularios faltantes

Faltaban formularios conectados para:

- Catalogos funcionales.
- Reglas de negocio.
- Reglas de alertas.
- Workflows y etapas.
- Proveedores, canales, plantillas y webhooks.
- Preview y confirmacion de carga CSV.
- Consultas y vistas de Mi Excel Web.
- Arboles, nodos y combinaciones de tipificacion.

## 4. Endpoints existentes no conectados en UI

La API ya tenia endpoints utiles que no estaban conectados visualmente:

- `POST /api/configuration/catalogs`
- `POST /api/configuration/rules`
- `POST /api/configuration/alert-rules`
- `POST /api/configuration/workflows`
- `POST /api/configuration/workflows/{id}/stages`
- `POST /api/integrations/providers`
- `POST /api/integrations/channels`
- `POST /api/integrations/channels/{id}/test`
- `POST /api/integrations/templates`
- `POST /api/integrations/webhooks`
- `POST /api/integrations/webhooks/{id}/test`
- `POST /api/uploads/preview`
- `POST /api/uploads/confirm`
- `POST /api/excel-web/query`
- `POST /api/excel-web/views`
- `POST /api/excel-web/export`
- `GET /api/recordings/{id}/playback`
- `GET /api/recordings/{id}/download`
- `POST /api/typifications/trees`
- `POST /api/typifications/trees/{id}/nodes`
- `POST /api/typifications/combinations`

## 5. Modulos que cargaban datos pero no permitian operar

Los modulos de configuracion, integraciones, cargas, Excel Web, grabaciones y arboles cargaban informacion demo, pero no ofrecian acciones suficientes de alta, prueba, preview, consulta o exportacion.

## 6. Causa del fallo visual al guardar gestion

El backend guardaba la gestion correctamente, pero la UI no tenia:

- drawer operativo claro,
- loading en boton,
- toast de exito,
- error visible bajo el formulario,
- refresco claro de historial y cola,
- manejo de fallos controlado.

Esto hacia que el usuario percibiera que el boton no hacia nada.

## 7. Problemas de permisos visuales

El rol agente heredaba `recordings.view` y el menu `operational_user` incluia Grabaciones. Esto contradecia la regla de Fase 8C: el gestor no debe ver Grabaciones por defecto.

## 8. Problemas del menu lateral

El menu era dinamico, pero visualmente era plano y sin iconografia corporativa. Se requerian grupos mas claros e iconos SVG monocromaticos.

## 9. Problemas de Cargas y Repartos

La pantalla no guiaba el flujo real de carga:

- seleccionar archivo,
- tipo de carga,
- proyecto,
- preview,
- confirmar,
- ver lotes,
- consultar errores/resultado.

## 10. Problemas del Centro de Configuracion

La pantalla mostraba catalogos, reglas, alertas y workflows, pero no permitia administrarlos desde la UI.

## 11. Problemas de Integraciones

La pantalla mostraba proveedores y canales, pero no permitia crear, editar ni probar canales/webhooks.

## 12. Problemas de Mi Excel Web

La pantalla mostraba fuentes, vistas y resultado inicial, pero no permitia seleccionar fuente, configurar columnas, ejecutar consulta, guardar vista o exportar desde una experiencia clara.

## 13. Plan priorizado

1. Corregir guardar gestion con drawer, loading, toast y error visible.
2. Ocultar Grabaciones para gestor por defecto.
3. Convertir Centro de Configuracion en formularios operativos.
4. Convertir Integraciones en formularios y pruebas simuladas.
5. Convertir Cargas en flujo preview/confirmacion.
6. Convertir Mi Excel Web en consulta real y vistas guardadas.
7. Agregar acciones auditables a Grabaciones.
8. Redisenar menu con SVG corporativo.
9. Documentar QA operativa por rol.
