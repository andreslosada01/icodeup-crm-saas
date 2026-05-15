# Configuracion Segura

## Regla

La V2 no debe tener secretos, contrasenas, hosts, puertos ni proveedores quemados en codigo.

## Donde va cada cosa

- `.env`: valores reales por ambiente.
- `.env.example`: plantilla sin secretos.
- Migraciones: estructura de base de datos.
- Seeders controlados: datos demo opcionales.
- Panel IcodeUp plataforma: parametrizacion operativa.

## Variables que salen del codigo

- `HOST`
- `PORT`
- `SECRET_KEY`
- `SESSION_COOKIE_NAME`
- `SESSION_HOURS`
- `DATABASE_URL`
- credenciales demo
- numeros WhatsApp iniciales
- cuentas SMTP
- proveedores de telefonia
- rutas fisicas de almacenamiento

## Produccion

En produccion los secretos deben vivir en el gestor del servidor o del proveedor cloud, no en archivos versionados.

