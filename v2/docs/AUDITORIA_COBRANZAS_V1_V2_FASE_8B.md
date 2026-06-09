# Auditoria Cobranzas V1/V2 - Fase 8B

## 1. Funcionalidades actuales V2

V2 cuenta con login, tenants, proyectos/carteras, usuarios, roles/permisos, menu dinamico, clientes, cola de gestion, promesas, pagos, acuerdos, juridico, documentos, ventas, BI, auditoria, alertas, configuracion funcional y data demo.

## 2. Funcionalidades contempladas en V1

La V1 tenia una experiencia operativa de cobranzas mas directa: cola de gestion, perfil de cliente, acciones de WhatsApp/email/click to call, tipificaciones, tablero ejecutivo, reportes y administracion basica. Tambien estaban contemplados canales, carga de cartera y parametrizacion.

## 3. Brechas frente a CRM vendible

- Gestion debia quedar garantizada para gestores asignados.
- Tipificaciones requerian arboles administrables por tenant/proyecto.
- Faltaban grabaciones metadata, demograficos y cargas operativas.
- Faltaba una consulta funcional tipo Excel Web.
- Integraciones/canales necesitaban administracion mas clara y logs.

## 4. Brechas frente a Soluciones Reales al Instante

Se requerian mas herramientas de operacion diaria: tareas, alertas, formularios, consulta por filtros, administracion funcional, roles por perfil y trazabilidad por usuario/cartera.

## 5. Brechas frente a App Pagos

Se necesitaba fortalecer cargas, soportes, exportes, auditoria de operaciones y control por usuario/cartera.

## 6. Brechas frente a Mi Excel Web

La plataforma necesitaba fuentes seguras, filtros, vistas guardadas y exportes auditados sin permitir SQL libre.

## 7. Riesgos funcionales actuales

- Frontend sigue siendo monolitico.
- Formularios avanzados de configuracion aun pueden ampliarse.
- Integraciones reales requieren proveedores, credenciales y storage seguro.

## 8. Prioridades de implementacion

1. Corregir registro de gestion.
2. Activar permisos especificos de actividades.
3. Crear arboles de tipificacion y combinaciones.
4. Agregar grabaciones, cargas, demograficos, Excel Web e integraciones.
5. Sembrar data demo idempotente.

## 9. Backlog recomendado

- Editor visual drag and drop de arboles.
- Wizard real de mapeo CSV/XLSX.
- Persistencia de estado de alertas.
- Integracion PBX/WebRTC real.
- WhatsApp Cloud API y SMTP productivo con secretos cifrados.
