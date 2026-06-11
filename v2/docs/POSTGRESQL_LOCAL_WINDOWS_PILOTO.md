# PostgreSQL Local Windows Para Piloto

Fecha: 2026-06-11  
Rama: `feature/deploy-test-server`  
Producto: Icodeup 360 ERP/CRM SaaS

## 1. Decision

Mientras se consigue el servidor definitivo, Icodeup 360 se podra ejecutar temporalmente en una maquina Windows con PostgreSQL local para QA funcional, pruebas internas y preparacion del piloto de hasta 30 usuarios.

Esta decision no cambia la arquitectura SaaS: el producto sigue usando **shared database / shared schema** con aislamiento por `tenant_id`. No se implementa base por empresa ni PostgreSQL RLS en esta fase.

## 2. Alcance

El ambiente local Windows sirve para:

- validar migraciones Alembic
- probar login, menu dinamico, roles y permisos
- validar CRM Collection, cargas, repartos, Excel Web, cobranzas, pagos, acuerdos, juridico, documentos, ventas y BI
- ejecutar QA interno antes de mover la app a servidor test
- preparar datos demo/piloto sin usar informacion real

No sirve como produccion. No debe exponerse publicamente ni usarse como base contractual de clientes reales.

## 3. Bases por ambiente

| Ambiente | Base sugerida | Uso |
|---|---|---|
| Local Windows | `icodeup_crm_local` | QA funcional y piloto temporal |
| Servidor test futuro | `icodeup_crm_test` | Validacion tecnica/preproductiva |
| Produccion futura | `icodeup_crm_prod` | Operacion real controlada |

Cada ambiente debe tener su propia base. No se deben mezclar datos demo/locales con test ni produccion.

## 4. Configuracion local

El ejemplo local esta en:

- `v2/backend/.env.local.windows.example`

La app lee el archivo activo desde:

- `v2/.env`

Por eso, para correr localmente se debe copiar el ejemplo a `v2/.env` y editar los valores locales. El archivo `v2/.env` esta ignorado por Git y no debe versionarse.

## 5. Seguridad

Reglas obligatorias:

- no subir `.env`
- no subir dumps
- no subir backups
- no subir logs
- no subir archivos reales
- no usar datos personales reales en local
- cambiar `SECRET_KEY`, password de base y password demo local
- mantener `TENANT_MODE=shared_schema` hasta implementar RLS real

## 6. Migracion posterior a servidor test

Cuando el servidor test este listo, se debe:

1. Crear `icodeup_crm_test` en el servidor.
2. Configurar un `.env` especifico de test.
3. Ejecutar `alembic upgrade head`.
4. Cargar datos demo/test seguros.
5. Ejecutar checklist QA.
6. Validar backups, logs, CORS, storage y monitoreo.

No se recomienda mover una base local completa a test sin revision previa de datos, secretos y archivos.
