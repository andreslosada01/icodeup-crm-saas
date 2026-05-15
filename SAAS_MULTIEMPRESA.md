# IcodeUp CRM - Modelo SaaS multiempresa

Este documento responde como debe funcionar el CRM cuando IcodeUp lo rente a varias empresas, cada una con sus propios proyectos, repartos, clientes, lideres, supervisores y gestores.

## Objetivo

La URL puede ser unica:

```text
https://crm.icodeup.com
```

El cliente no debe escoger ni ver otras empresas. Al iniciar sesion, el sistema identifica a que empresa pertenece el usuario y carga solo su entorno.

## Arquitectura recomendada

Para una solucion corporativa la recomendacion es separar plataforma y operacion:

- `platform_db`: base central de IcodeUp. Guarda empresas contratantes, usuarios de acceso, planes, estado del servicio, dominios, auditoria global y datos de conexion de cada tenant.
- `tenant_db_<empresa>`: base independiente por empresa. Guarda proyectos, repartos, clientes, usuarios operativos, gestiones, promesas, pagos, canales, tipificaciones y reportes.
- Aplicacion compartida: el codigo del CRM es uno solo. Si se mejora una pantalla, una regla o un reporte, se despliega una sola version y luego se ejecutan migraciones sobre cada base tenant.

Esta arquitectura permite:

- Aislamiento fuerte de datos.
- Backups y restauraciones por empresa.
- Baja de una empresa sin afectar a las demas.
- Escalamiento individual cuando una empresa crece.
- Mayor confianza comercial para clientes corporativos.

## Flujo de login

1. Usuario entra a `https://crm.icodeup.com`.
2. Ingresa email y contrasena.
3. El backend valida credenciales en `platform_db`.
4. El backend obtiene el `tenant_id` y la conexion de su empresa.
5. Desde ese momento, todas las consultas operativas van a la base de esa empresa.
6. El frontend recibe solo datos de su empresa y sus permisos.

Los usuarios de una empresa nunca reciben listado de empresas. Ese modulo solo existe para el rol `IcodeUp plataforma`.

## Super administrador IcodeUp

El rol `IcodeUp plataforma` es el administrador general del CRM. Tiene visibilidad y gobierno sobre todo el SaaS:

- Inventario de empresas contratantes.
- Usuarios de cada empresa.
- Proyectos/carteras de cada empresa.
- Conteo de clientes por tenant y por proyecto.
- Alta de empresas cliente.
- Alta de proyectos para cualquier empresa.
- Alta de usuarios tenant para cualquier empresa.
- Activacion o inactivacion de usuarios.
- Activacion o pausa de proyectos.

Los clientes no ven este modulo. Para ellos el CRM se comporta como si fuera una aplicacion propia de su empresa.

## Estructura por empresa

Cada empresa puede tener muchos proyectos o carteras:

```text
Empresa 1
  Proyecto 1
    Reparto
    Clientes
    Lideres
    Supervisores de calidad
    Gestores
  Proyecto 2
  ...

Empresa 2
  Proyecto 1
  Proyecto 2
  ...
```

Dentro de cada proyecto se administran:

- Repartos cargados por CSV/Excel.
- Clientes y obligaciones.
- Lider o coordinador responsable.
- Gestores asignados.
- Supervisores de calidad.
- Tipificaciones propias.
- Canales de WhatsApp, correo y telefonia.
- Reportes y tableros.

## Como agregar una empresa

En el CRM local ya existe el camino funcional:

1. Iniciar sesion como plataforma IcodeUp:

```text
platform@icodeup.com
Platform123!
```

2. Entrar al modulo `Empresas`.
3. Diligenciar `Nueva empresa cliente`.
4. Definir:
   - Nombre de empresa.
   - Slug o identificador interno.
   - NIT.
   - Administrador inicial.
   - Contrasena inicial.
   - Proyecto base.
5. Guardar.

En produccion, este paso tambien debe crear la base tenant independiente, ejecutar migraciones y registrar su conexion en `platform_db`.

## Como agregar proyectos dentro de una empresa

1. Ingresar como `IcodeUp plataforma` o como administrador autorizado de la empresa, segun la regla que se defina.
2. Entrar a `Empresas` o `Repartos`.
3. Crear el proyecto/cartera.
4. Asignar lideres, supervisores y gestores desde `Usuarios`.
5. Cargar el reparto desde `Repartos`.

## Reglas de seguridad obligatorias

- Todo usuario debe quedar asociado a una sola empresa o a rol plataforma.
- Toda consulta operativa debe resolverse con el tenant autenticado.
- Un usuario cliente no puede consultar `/empresas`, ni recibir datos de otros tenants en respuestas API.
- Los reportes de BI deben calcularse solo sobre la base tenant activa.
- Las migraciones deben ejecutarse de forma controlada en todas las bases tenant.
- Las acciones sensibles deben quedar en auditoria: login, creacion de usuarios, carga de reparto, cambios de tipificacion, cambios de canal, pagos y promesas.

## Estado actual del prototipo

La version local ya implementa el modelo base con:

- Login con autodeteccion de empresa por usuario.
- Rol `IcodeUp plataforma`.
- Modulo `Empresas` visible solo para plataforma.
- Creacion de empresas y proyectos iniciales.
- Inventario completo de usuarios y proyectos por empresa.
- Administracion de usuarios y proyectos desde IcodeUp plataforma.
- Base de plataforma en `data/platform.sqlite3`.
- Base independiente por empresa en `data/tenants/<empresa>.sqlite3`.
- `company_id` como control adicional dentro de cada base tenant.

La siguiente evolucion tecnica es migrar estos mismos conceptos de SQLite a PostgreSQL, con migraciones versionadas, entornos de test/staging/produccion y aprovisionamiento automatizado.
