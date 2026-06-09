# Guia Admin - Grabaciones de Llamadas

## Objetivo

Consultar metadata de grabaciones asociadas a clientes, gestiones, usuarios y proveedores de telefonia.

## Permisos

- `recordings.view`
- `recordings.playback`
- `recordings.download`
- `recordings.manage`
- `recordings.audit.view`

## Endpoints

- `GET /api/recordings`
- `POST /api/recordings`
- `GET /api/recordings/{id}`
- `GET /api/recordings/{id}/playback`
- `GET /api/recordings/{id}/download`
- `POST /api/recordings/link-activity`
- `GET /api/recordings/access-logs`

## Notas

La demo usa rutas placeholder. Produccion debe usar URLs firmadas o storage seguro y auditoria de cada reproduccion/descarga.
