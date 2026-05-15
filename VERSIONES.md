# Versiones del Proyecto

## V1 - Prototipo funcional

Ubicacion congelada:

`versions/v1-prototipo-funcional`

La V1 mantiene la aplicacion actual funcionando con:

- HTML, CSS y JavaScript monoliticos.
- Backend Python monolitico.
- SQLite local.
- Datos demo y configuracion inicial dentro del codigo.

Esta version sirve como referencia funcional y demo operativa.

## V2 - Arquitectura corporativa

Ubicacion:

`v2`

La V2 se construira con:

- Frontend modular.
- Backend modular.
- Configuracion por `.env`.
- PostgreSQL.
- Servicios por dominio.
- Parametrizacion desde superusuarios IcodeUp.
- Preparacion para test, staging y produccion.

## Regla de trabajo

La V1 no se rompe. La V2 se migra por modulos, validando cada parte antes de reemplazar funcionalidades.

