# Matriz QA por roles pre-productiva

## Credenciales demo usadas para QA

Todos los usuarios demo usan la clave de entorno controlado `Demo360!2026`. Esta clave no debe existir en produccion.

| Rol | Usuario | Modulos esperados | Modulos prohibidos | Pruebas ejecutadas | Resultado | Correcciones aplicadas |
| --- | --- | --- | --- | --- | --- | --- |
| SuperAdmin Icodeup | superadmin@demo.icodeup.local | Gobierno SaaS, empresas, planes, suscripciones, modulos, salud, auditoria global | Operacion diaria como unico foco | Login, menu, dashboard, governance, health, auditoria | OK por pruebas HTTP; pendiente QA visual final | Ninguna especifica |
| Admin Empresa | admin.andina@demo.icodeup.local | Mi empresa, usuarios, roles, equipos, cargas, clientes, cobranzas, juridico, documentos, ventas, BI, auditoria tenant | Gobierno global Icodeup | Login, menu, equipos, uploads, configuracion, auditoria | OK por pruebas HTTP; pendiente QA visual final | Listados acotados a 20 |
| Lider Cobranzas | coord.cobranzas.andina@demo.icodeup.local | Dashboard equipo, clientes, obligaciones, promesas, pagos, acuerdos, equipos, Excel Web | Gobierno global y configuracion plataforma | Login, menu, dashboard equipos, listados operativos | OK por pruebas HTTP; pendiente QA visual final | Listados acotados a 20 |
| Gestor | gestor1.andina@demo.icodeup.local | Mi operacion, cola, clientes asignados, gestiones, promesas, pagos, acuerdos, Excel Web | Gobierno, admin empresa, uploads, equipos, exportes | Login, menu, clientes, crear gestion, actividad reciente, export bloqueado | OK por pruebas HTTP; pendiente QA visual final | Prueba E2E agregada |
| Gestor | gestor2.andina@demo.icodeup.local | Igual gestor 1 | Igual gestor 1 | Smoke recomendado en navegador | Pendiente manual | Ninguna |
| Supervisor Calidad | calidad.andina@demo.icodeup.local | Lectura operativa, BI, auditoria si tiene permiso | Gestion administrativa y exportes no autorizados | Smoke recomendado | Pendiente manual | Ninguna |
| Abogado | abogado.andina@demo.icodeup.local | Juridico, documentos, clientes lectura | Gobierno, ventas, cola completa, pagos/exportes | Login, menu, legal, documentos, export bloqueado | OK por pruebas HTTP; pendiente QA visual final | Listados juridicos acotados a 20 |
| Comercial | comercial.andina@demo.icodeup.local | Ventas, leads, oportunidades, clientes lectura | Gobierno, juridico, documentos, cola, pagos/exportes | Login, menu, ventas, pipeline, export bloqueado | OK por pruebas HTTP; pendiente QA visual final | Listados ventas acotados a 20 |

## Resultado general

La experiencia por rol esta lista para PR con una validacion visual final en navegador despues de reiniciar el servicio. Los tests agregados verifican menu, dashboards, alcance tenant, bloqueos de exportes y flujo gestor basico. La suite integrada completa ejecuto 75 pruebas y paso correctamente.

## Errores encontrados

- Algunos listados podian mostrar o solicitar mas de 20 registros por defecto.
- Las funciones de dashboard juridico/comercial llamaban listados con default `Query`; se corrigio pasando `limit=20` explicitamente.
- Una prueba nueva apuntaba inicialmente a una ruta inexistente de equipos; se ajusto a `/api/teams/dashboard`.

## Correcciones aplicadas

- Limites backend a 20 en auditoria administrativa, obligaciones, promesas, pagos, acuerdos, documentos, juridico, ventas, grabaciones, integraciones, alertas y demograficos.
- Limites frontend a 20 en configuracion, grabaciones, demograficos, integraciones y preview de cargas.
- Pruebas pre-productivas por rol y multi-tenant.
