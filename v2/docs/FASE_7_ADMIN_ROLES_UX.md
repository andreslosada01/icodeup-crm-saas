# Fase 7 Admin Roles UX

## 1. Resumen de cambios

Fase 7 mejora la experiencia administrativa para usuarios, roles, permisos, modulos y perfiles efectivos. El objetivo es que Admin Empresa y SuperAdmin entiendan que puede hacer cada usuario sin depender del equipo tecnico.

## 2. Problema resuelto

La aplicacion ya tenia permisos granulares y roles especializados, pero la UI no explicaba:

- `User.role` legacy.
- Rol especializado activo.
- Permisos efectivos.
- Modulos visibles.
- Restricciones operativas.
- Riesgos de configuracion.

## 3. Pantallas intervenidas

- Usuarios de empresa.
- Roles y permisos.
- Modulos contratados.
- Gobierno SaaS, cuando SuperAdmin consulta modulos por tenant.

## 4. Endpoints creados o modificados

Nuevos:

- `GET /api/governance/users/{user_id}/effective-access`
- `GET /api/governance/users/{user_id}/access-explanation`
- `GET /api/governance/security-insights`

Modificados:

- `GET /api/governance/users`
- `GET /api/governance/modules`

## 5. Componentes visuales agregados

- Tarjetas de usuarios con perfil efectivo.
- Panel de detalle de acceso efectivo.
- Matriz visual de roles y permisos.
- Filtros de roles por modulo y tipo de permiso.
- Alertas de configuracion de seguridad.
- Insights de modulos contratados con impacto y recomendacion.

## 6. User.role vs rol especializado

`User.role` se muestra como rol tecnico heredado. Se conserva por compatibilidad con modulos antiguos.

El rol especializado viene de `UserProfile.role_id` y define permisos reales cuando existe un rol activo. Ejemplos:

- `agent + lawyer`: Abogado.
- `agent + sales_advisor`: Asesor Comercial.
- `agent + collections_agent`: Gestor de Cobranzas.

## 7. Permisos efectivos

El panel efectivo agrupa permisos por modulo y marca permisos criticos. Los permisos efectivos consideran:

- rol especializado activo,
- fallback legacy,
- permisos reservados ocultos para Admin Empresa,
- modulos activos por tenant.

## 8. Modulos visibles

Cada modulo muestra:

- activo/inactivo,
- contratado/configurado,
- visible para el usuario,
- permisos relacionados,
- usuarios con acceso,
- razon de visibilidad u ocultamiento.

## 9. Alertas de seguridad

Las alertas cubren:

- usuarios con rol legacy amplio,
- usuarios con exportes,
- roles administrativos,
- modulos activos sin usuarios,
- usuarios inactivos con permisos criticos,
- tenant sin plan activo,
- data demo activa.

## 10. Riesgos pendientes

- La UI sigue siendo HTML/CSS/JS monolitico.
- La validacion visual completa debe hacerse tras reiniciar el servicio local.
- A futuro conviene separar componentes frontend o migrar a una arquitectura mas modular.

## 11. Recomendaciones para Fase 8

- Crear flujo visual para editar permisos de rol con agrupacion por modulo.
- Agregar historial de cambios por usuario.
- Mejorar dashboard de auditoria tenant.
- Preparar QA visual automatizado por perfil.
