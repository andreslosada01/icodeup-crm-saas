# Guia Admin - Integraciones y Canales

## Objetivo

Administrar canales de comunicacion e integraciones de forma segura.

## Componentes

- proveedores
- canales
- plantillas
- webhooks
- logs de eventos

## Canales

Telefonia, WhatsApp, email, SMS y webhooks.

## Seguridad

Los secretos se enmascaran. Las pruebas son simuladas. Produccion debe usar cifrado y vault/secret manager.

## Endpoints

- `/api/integrations/providers`
- `/api/integrations/channels`
- `/api/integrations/templates`
- `/api/integrations/webhooks`
- `/api/integrations/events`
