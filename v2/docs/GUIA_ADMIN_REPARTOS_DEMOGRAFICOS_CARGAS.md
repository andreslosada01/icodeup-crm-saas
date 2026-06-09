# Guia Admin - Repartos, Demograficos y Cargas

## Objetivo

Controlar cargas operativas desde UI con previsualizacion, validacion, confirmacion y auditoria.

## Tipos soportados

- `reparto_cartera`
- `demograficos`
- `pagos`
- `documentos`
- `grabaciones`
- `generico_excel_web`

## Endpoints

- `POST /api/uploads/preview`
- `POST /api/uploads/confirm`
- `GET /api/uploads/batches`
- `GET /api/uploads/batches/{id}`
- `GET /api/uploads/batches/{id}/errors`
- `GET /api/uploads/batches/{id}/result`
- `GET /api/uploads/demographics`
- `POST /api/uploads/demographics`

## Seguridad

Las cargas se guardan como metadata y resumen. No se versionan archivos reales. Todo lote respeta tenant y permisos.
