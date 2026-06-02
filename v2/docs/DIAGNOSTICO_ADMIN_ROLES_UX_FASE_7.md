# Diagnostico Admin Roles UX Fase 7

## 1. Estado actual de la UI de usuarios

La UI mostraba usuarios visibles por tenant con nombre, email, rol actual, estado y selector para asignar rol. Era funcional, pero no explicaba claramente la diferencia entre `User.role` legacy y el rol efectivo de `UserProfile.role_id`.

## 2. Estado actual de la UI de roles

La seccion de roles permitia crear roles y ver una tabla basica con tipo, cantidad de permisos, usuarios y estado. No destacaba permisos criticos, exportes, modulos asociados ni riesgos administrativos.

## 3. Estado actual de permisos

Los permisos existen por codigo granular y se filtran para Admin Empresa evitando permisos reservados de Icodeup. La UI no agrupaba permisos por modulo ni explicaba el impacto operativo.

## 4. Estado actual de modulos por tenant

La UI mostraba modulos activos/inactivos y permitia al SuperAdmin activar o desactivar. No explicaba usuarios con acceso, roles asociados, impacto de desactivar ni recomendacion comercial.

## 5. Brechas para Admin Empresa

- Dificultad para entender que rol real tiene cada usuario.
- Poca visibilidad de permisos efectivos.
- Falta de alertas de configuracion.
- Falta de explicacion sobre por que un modulo aparece u oculta.
- Falta de diferenciacion visual entre perfiles como Abogado, Comercial, Gestor y Auditor.

## 6. Brechas para SuperAdmin Icodeup

- Auditoria visual limitada de perfiles efectivos por tenant.
- Falta de resumen de usuarios con permisos de exportacion.
- Falta de alertas sobre tenants sin plan, modulos activos sin usuarios o roles administrativos.

## 7. Riesgos User.role vs rol especializado

`User.role` sigue siendo necesario por compatibilidad legacy. El riesgo es que el administrador interprete `agent` o `coordinator` como el perfil funcional real, cuando los permisos efectivos pueden venir de un rol especializado como `lawyer` o `sales_advisor`.

## 8. Recomendaciones visuales

- Mostrar `User.role` como rol tecnico heredado.
- Mostrar `Role.code` especializado como perfil funcional.
- Agrupar permisos efectivos por modulo.
- Mostrar modulos visibles y razones de visibilidad.
- Mostrar alertas de seguridad operativa.
- Diferenciar permisos criticos, exportes y administracion.

## 9. Recomendaciones backend minimas

- Crear `GET /api/governance/users/{user_id}/effective-access`.
- Crear `GET /api/governance/users/{user_id}/access-explanation`.
- Crear `GET /api/governance/security-insights`.
- Enriquecer `/api/governance/users` con rol legacy, rol especializado, modulos visibles y conteos.
- Enriquecer `/api/governance/modules` con usuarios, permisos, roles e impacto.
