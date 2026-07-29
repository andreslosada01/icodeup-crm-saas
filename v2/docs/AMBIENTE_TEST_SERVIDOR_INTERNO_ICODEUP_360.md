# Ambiente TEST servidor interno Icodeup 360

## 1. Objetivo

Crear un ambiente TEST separado en el mismo servidor fisico interno de Icodeup para validar cambios antes de afectar el ambiente actual.

El ambiente TEST no reemplaza produccion interna. Debe operar con base, servicio, puerto, logs, uploads y backups independientes.

## 2. Arquitectura separada

| Componente | Ambiente actual | Ambiente TEST |
|---|---|---|
| Ruta app | `/opt/icodeup360/app` | `/opt/icodeup360_test/app` |
| Servicio systemd | `icodeup360.service` | `icodeup360-test.service` |
| Backend | `127.0.0.1:8020` | `127.0.0.1:8021` |
| Nginx | `http://10.201.16.53` puerto `80` | `http://10.201.16.53:8081` |
| PostgreSQL DB | `icodeup360_prod` | `icodeup360_test` |
| Usuario DB | `icodeup360_user` | `icodeup360_test_user` |
| Uploads | ruta productiva actual | `/var/uploads/icodeup360_test` |
| Logs app | ruta productiva actual | `/var/log/icodeup360_test` |
| Backups | ruta productiva actual | `/var/backups/icodeup360_test` |

Nunca mezclar las variables `.env` del ambiente actual con las de TEST.

## 3. Crear carpetas

```bash
sudo mkdir -p /opt/icodeup360_test/app
sudo mkdir -p /var/uploads/icodeup360_test
sudo mkdir -p /var/log/icodeup360_test
sudo mkdir -p /var/backups/icodeup360_test
sudo chown -R icodeup:icodeup /opt/icodeup360_test /var/uploads/icodeup360_test /var/log/icodeup360_test /var/backups/icodeup360_test
sudo chmod 750 /opt/icodeup360_test /var/uploads/icodeup360_test /var/log/icodeup360_test /var/backups/icodeup360_test
```

## 4. Clonar repositorio

```bash
sudo -u icodeup git clone https://github.com/andreslosada01/icodeup-crm-saas.git /opt/icodeup360_test/app
cd /opt/icodeup360_test/app
sudo -u icodeup git checkout feature/deploy-test-server
```

Si el repositorio ya existe:

```bash
cd /opt/icodeup360_test/app
sudo -u icodeup git fetch origin
sudo -u icodeup git checkout feature/deploy-test-server
sudo -u icodeup git pull origin feature/deploy-test-server
```

## 5. Crear base y usuario PostgreSQL TEST

Generar un password seguro fuera del repo:

```bash
openssl rand -base64 24
```

Crear usuario y base. Reemplazar el placeholder solo en consola segura del servidor:

```bash
sudo -u postgres psql
```

Dentro de `psql`:

```sql
CREATE USER icodeup360_test_user WITH PASSWORD 'CAMBIAR_PASSWORD';
CREATE DATABASE icodeup360_test OWNER icodeup360_test_user;
GRANT ALL PRIVILEGES ON DATABASE icodeup360_test TO icodeup360_test_user;
\q
```

No usar passwords reales en Git, chats ni documentos.

## 6. Crear `.env` TEST

Copiar el ejemplo:

```bash
cd /opt/icodeup360_test/app
cp v2/backend/.env.test.server.example v2/.env
chmod 640 v2/.env
chown icodeup:icodeup v2/.env
nano v2/.env
```

Valores minimos a reemplazar:

```env
APP_ENV=test
APP_PORT=8021
DATABASE_URL=postgresql+psycopg://icodeup360_test_user:CAMBIAR_PASSWORD@127.0.0.1:5432/icodeup360_test
SECRET_KEY=CAMBIAR_SECRET
ENABLE_DEMO_DATA=false
ENABLE_DEMO_SEEDS=false
ENABLE_PILOT_ICODEUP_SEED=false
UPLOAD_STORAGE_PATH=/var/uploads/icodeup360_test
FRONTEND_DIR=../frontend/static
ALLOWED_ORIGINS=http://10.201.16.53:8081,http://10.201.16.53
```

Si se requiere admin inicial, usar credencial temporal y rotarla despues del primer acceso.

## 7. Crear venv e instalar dependencias

```bash
cd /opt/icodeup360_test/app/v2/backend
sudo -u icodeup python3 -m venv venv
sudo -u icodeup ./venv/bin/pip install --upgrade pip
sudo -u icodeup ./venv/bin/pip install -r requirements.txt
```

## 8. Ejecutar migraciones

```bash
cd /opt/icodeup360_test/app/v2/backend
sudo -u icodeup ./venv/bin/alembic upgrade head
sudo -u icodeup ./venv/bin/alembic current
```

El resultado esperado es `20260611_0006 (head)` o la migracion head vigente del repositorio.

## 9. Levantar manualmente con Uvicorn

Prueba manual antes de systemd:

```bash
cd /opt/icodeup360_test/app/v2/backend
sudo -u icodeup ./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8021
```

En otra terminal:

```bash
curl http://127.0.0.1:8021/api/health
```

Detener con `Ctrl+C` cuando la prueba termine.

## 10. Crear servicio systemd TEST

```bash
sudo cp /opt/icodeup360_test/app/v2/deploy/systemd/icodeup360-test.service.example /etc/systemd/system/icodeup360-test.service
sudo systemctl daemon-reload
sudo systemctl enable icodeup360-test
sudo systemctl start icodeup360-test
systemctl status icodeup360-test
```

Logs:

```bash
journalctl -u icodeup360-test -n 100 --no-pager
tail -n 100 /var/log/icodeup360_test/app.err.log
```

Reinicio:

```bash
sudo systemctl restart icodeup360-test
```

## 11. Configurar Nginx TEST en puerto 8081

```bash
sudo cp /opt/icodeup360_test/app/v2/deploy/nginx/icodeup360-test-internal.nginx.example /etc/nginx/sites-available/icodeup360-test-internal
sudo ln -s /etc/nginx/sites-available/icodeup360-test-internal /etc/nginx/sites-enabled/icodeup360-test-internal
sudo nginx -t
sudo systemctl reload nginx
```

Validar:

```bash
curl http://127.0.0.1:8021/api/health
curl http://10.201.16.53:8081/api/health
```

## 12. No tocar produccion

Antes de ejecutar cualquier comando, confirmar:

```bash
pwd
grep -E '^DATABASE_URL=' /opt/icodeup360_test/app/v2/.env | sed -E 's#://[^:@]+:[^@]+@#://***:***@#'
systemctl status icodeup360
systemctl status icodeup360-test
```

Reglas:

- No modificar `/opt/icodeup360/app` durante pruebas TEST.
- No reiniciar `icodeup360.service` para validar TEST.
- No usar `icodeup360_prod` como base TEST.
- No copiar `.env` productivo al ambiente TEST.
- No exponer `8020` ni `8021` directamente a Internet.
- No subir `.env`, dumps, logs, backups ni archivos runtime al repositorio.
