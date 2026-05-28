# Roadmap Producto SaaS

## 1. Nombre del producto

**Icodeup Collection & Legal CRM**

## 2. Propuesta de valor

Plataforma SaaS para controlar cartera, cobranza, recaudo, promesas de pago, acuerdos, pagos, documentos, escalamiento juridico, expedientes, vencimientos y analitica ejecutiva en una sola solucion multiempresa.

## 3. Cliente objetivo

- BPO de cobranzas.
- Call centers.
- Empresas de recuperacion de cartera.
- Firmas juridicas.
- Fintechs.
- Cooperativas.
- Empresas con cartera propia.
- Areas legales y de cartera.

## 4. Modulos actuales

- Autenticacion.
- Administracion multiempresa.
- Proyectos/carteras.
- Usuarios, roles, lideres y asignaciones.
- Clientes/deudores.
- Cola de gestion.
- Actividades de gestion.
- Promesas de pago.
- Pagos.
- Canales configurables.
- Tipificaciones.
- Tablero ejecutivo.
- Reportes BI.
- Carga CSV.

## 5. Modulos nuevos

- Planes SaaS.
- Suscripciones por tenant.
- Modulos activables por tenant.
- Acuerdos de pago.
- Juridico minimo.
- Gestion documental metadata.
- Ventas basico.
- Auditoria transversal.

## 6. Roadmap

- V2 actual: cobranzas operativas.
- V2.1: refactor y hardening SaaS.
- V2.2: acuerdos y documentos.
- V2.3: juridico.
- V2.4: ventas basico.
- V3: React/Vite.
- V4: IA, scoring avanzado e integraciones WhatsApp/email/telefonia.

## 7. Modelo comercial sugerido

- SaaS mensual.
- Implementacion inicial.
- Bolsa de horas.
- Integraciones como add-on.
- BI/IA como add-on futuro.

## 8. Planes sugeridos

- Starter.
- Professional.
- Business.
- Enterprise.

## 9. Limites por plan

| Plan | Usuarios | Proyectos/carteras | Clientes | Modulos activos | BI | Integraciones | Soporte |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| Starter | 10 | 2 | 5.000 | Core, cobranzas | Basico | No | Estandar |
| Professional | 40 | 8 | 50.000 | Core, cobranzas, documentos | Operativo | Email | Prioritario |
| Business | 120 | 25 | 250.000 | Core, cobranzas, documentos, juridico, BI | Avanzado | WhatsApp/email/telefonia | Prioritario |
| Enterprise | A medida | A medida | A medida | Todos | Avanzado + IA | Todas | Dedicado |

## 10. Recomendaciones para evitar personalizaciones descontroladas

- Parametrizar por tenant antes que crear codigo por cliente.
- Usar tipificaciones, modulos, planes y configuracion por proyecto.
- Separar integraciones por adaptadores.
- Documentar cada excepcion comercial como configuracion o add-on.
- No crear ramas permanentes por cliente.
- Mantener migraciones no destructivas.

## 11. Backlog por fases

### V2.1

- Refactor CRM.
- Planes, suscripciones y modulos.
- Auditoria basica.
- Placeholders frontend.

### V2.2

- Interfaz completa de acuerdos.
- Documentos con carga binaria segura.
- Alertas por cuotas vencidas.

### V2.3

- Expediente juridico completo.
- Agenda legal.
- Reporteria de etapas, juzgados, cuantias y vencimientos.

### V2.4

- Leads.
- Oportunidades.
- Pipeline.
- Conversion a cliente.

### V3

- Migracion frontend a React/Vite.
- Componentes reutilizables.
- Pruebas frontend.

### V4

- Scoring IA avanzado.
- Recomendaciones automaticas.
- Integraciones reales de canales.
- Automatizaciones y orquestacion.

## 12. Riesgos

- Crecimiento del frontend vanilla.
- Ausencia de migraciones formales para produccion.
- Consultas BI en memoria para volumen alto.
- Integraciones con proveedores externos sin capa de secretos.
- Falta de suite automatizada completa.

## 13. Proximos pasos

- Validar regresion completa de cobranzas.
- Convertir modelos nuevos en migraciones Alembic.
- Completar UI de acuerdos y documentos.
- Agregar pruebas de permisos por tenant y rol.
- Definir pricing real y paquete de implementacion.
