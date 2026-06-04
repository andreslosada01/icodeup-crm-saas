# Deploy produccion Icodeup 360

## Objetivo

Guia operativa para desplegar Icodeup 360 en un servidor Linux de test o produccion usando FastAPI, Uvicorn, PostgreSQL, systemd, Nginx y HTTPS.

## Requerimientos servidor

- Ubuntu Server LTS o equivalente.
- Python 3.11+.
- PostgreSQL 15+.
- Nginx.
- Certbot o proveedor TLS equivalente.
- Usuario Linux dedicado, por ejemplo `icodeup360`.
- Firewall con puertos 22, 80 y 443 controlados.

## Variables de entorno obligatorias

No versionar `.env`.

```bash
APP_ENV=production
DEBUG=false
SECRET_KEY=change-me-with-secure-random-value
DATABASE_URL=postgresql+psycopg://icodeup360:change-me@127.0.0.1:5432/icodeup360
ALLOWED_ORIGINS=https://crm.tu-dominio.com
ENABLE_DEMO_DATA=false
ENABLE_DEMO_SEEDS=false
```

## Instalacion base

```bash
sudo adduser --system --group --home /opt/icodeup360 icodeup360
sudo mkdir -p /opt/icodeup360/app /var/log/icodeup360 /var/backups/icodeup360
sudo chown -R icodeup360:icodeup360 /opt/icodeup360 /var/log/icodeup360 /var/backups/icodeup360
```

## PostgreSQL

```bash
sudo -u postgres createuser icodeup360
sudo -u postgres createdb icodeup360 -O icodeup360
```

Asignar password fuerte desde consola segura. No dejar passwords en scripts.

## Backend

```bash
cd /opt/icodeup360/app/v2/backend
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .
alembic upgrade head
```

## systemd ejemplo

```ini
[Unit]
Description=Icodeup 360 API
After=network.target postgresql.service

[Service]
User=icodeup360
Group=icodeup360
WorkingDirectory=/opt/icodeup360/app/v2/backend
EnvironmentFile=/opt/icodeup360/.env
ExecStart=/opt/icodeup360/app/v2/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8020
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Nginx ejemplo

```nginx
server {
    listen 80;
    server_name crm.tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8020;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## HTTPS

```bash
sudo certbot --nginx -d crm.tu-dominio.com
```

## Healthcheck

```bash
curl -fsS https://crm.tu-dominio.com/api/health
```

## Backups

- Backup diario PostgreSQL.
- Retencion minima: 7 diarios, 4 semanales, 6 mensuales.
- Restore semanal en ambiente test.
- Backup antes de cada deploy.

## Rollback

1. Detener servicio.
2. Volver al tag/commit anterior.
3. Restaurar backup si hubo migracion incompatible.
4. Ejecutar healthcheck.
5. Revisar logs y auditoria.

## Logs

- systemd: `journalctl -u icodeup360 -f`.
- Nginx: `/var/log/nginx/access.log` y `/var/log/nginx/error.log`.
- No imprimir contrasenas, tokens, CSV completos ni archivos sensibles.

## Checklist antes de clientes reales

- `ENABLE_DEMO_DATA=false`.
- Passwords demo eliminados o rotados.
- SECRET_KEY fuerte.
- CORS restringido.
- HTTPS activo.
- Backup probado.
- Usuarios reales creados por admin autorizado.
- QA por rol ejecutado.
