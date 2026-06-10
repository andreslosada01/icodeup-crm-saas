# Checklist despliegue servidor test

## 1. Crear servidor Ubuntu

- Usar Ubuntu Server LTS.
- Abrir solo puertos necesarios: 22, 80, 443.
- Configurar acceso SSH seguro.

## 2. Crear usuario y carpetas

Revisar y ejecutar manualmente:

```bash
v2/scripts/server_test_setup_ubuntu.sh.example
```

Carpetas esperadas:

- `/opt/icodeup360-test`
- `/opt/icodeup360-test/app`
- `/etc/icodeup360-test`
- `/var/log/icodeup360-test`
- `/var/lib/icodeup360-test/uploads`
- `/var/backups/icodeup360-test`

## 3. Instalar dependencias

El script ejemplo instala:

- Python 3
- venv/pip
- git
- postgresql-client
- nginx
- certbot
- curl

## 4. Crear base PostgreSQL test

Ejemplo manual:

```bash
sudo -u postgres createuser icodeup_test_user
sudo -u postgres createdb icodeup_crm_test -O icodeup_test_user
sudo -u postgres psql -c "ALTER USER icodeup_test_user WITH PASSWORD 'change-me';"
```

Usar password real fuerte y no guardarla en el repo.

## 5. Clonar repo

```bash
sudo -u icodeup git clone https://github.com/andreslosada01/icodeup-crm-saas.git /opt/icodeup360-test/app
```

## 6. Crear `.env` real

```bash
sudo cp /opt/icodeup360-test/app/v2/backend/.env.example /etc/icodeup360-test/.env
sudo nano /etc/icodeup360-test/.env
sudo chown root:icodeup /etc/icodeup360-test/.env
sudo chmod 640 /etc/icodeup360-test/.env
```

Valores minimos:

- `SECRET_KEY` real.
- `DATABASE_URL` real.
- `FRONTEND_DIR=/opt/icodeup360-test/app/v2/frontend/static`.
- `APP_ENV=test`.
- `ENABLE_DEMO_DATA=true` solo para ambiente demo/test.
- `ENABLE_DEMO_SEEDS=true` solo para ambiente demo/test.

## 7. Ejecutar migraciones

```bash
cd /opt/icodeup360-test/app
python3 -m venv .venv
. .venv/bin/activate
pip install -r v2/backend/requirements.txt
cd v2/backend
alembic upgrade head
alembic current
```

## 8. Crear servicio systemd

```bash
sudo cp /opt/icodeup360-test/app/v2/deploy/systemd/icodeup360-test.service.example /etc/systemd/system/icodeup360-test.service
sudo systemctl daemon-reload
sudo systemctl enable icodeup360-test
sudo systemctl start icodeup360-test
sudo systemctl status icodeup360-test
```

## 9. Configurar Nginx

```bash
sudo cp /opt/icodeup360-test/app/v2/deploy/nginx/icodeup360-test.nginx.example /etc/nginx/sites-available/icodeup360-test
sudo ln -s /etc/nginx/sites-available/icodeup360-test /etc/nginx/sites-enabled/icodeup360-test
sudo nginx -t
sudo systemctl reload nginx
```

## 10. Configurar dominio test

- Crear DNS tipo A/CNAME hacia el servidor.
- Editar `server_name` en Nginx si no se usa `test.icodeup.com`.

## 11. Configurar HTTPS

```bash
sudo certbot --nginx -d test.icodeup.com
```

## 12. Ejecutar health

```bash
curl -fsS http://127.0.0.1:8020/api/health
curl -fsS http://test.icodeup.com/api/health
```

## 13. Login con usuarios demo

Validar solo en test:

- `superadmin@demo.icodeup.local`
- `admin.andina@demo.icodeup.local`
- `coord.cobranzas.andina@demo.icodeup.local`
- `gestor1.andina@demo.icodeup.local`
- `abogado.andina@demo.icodeup.local`
- `comercial.andina@demo.icodeup.local`

## 14. QA visual por rol

Usar `v2/docs/QA_POST_DEPLOY_TEST_ICODEUP_360.md`.

## 15. Validar backups

```bash
PGDATABASE=icodeup_crm_test PGUSER=icodeup_test_user v2/scripts/backup_postgres.sh.example
```

## 16. Validar restore

```bash
BACKUP_FILE=/var/backups/icodeup360-test/<archivo>.dump.gz \
TARGET_DB=icodeup_crm_test_restore \
CONFIRM_RESTORE=RESTORE_TEST_DB \
v2/scripts/restore_backup_to_test.sh.example
```

## 17. Validar logs

```bash
journalctl -u icodeup360-test -n 100
tail -n 100 /var/log/nginx/icodeup360-test.error.log
```

No deben aparecer passwords, tokens, CSV completos ni datos sensibles.

## 18. Criterio para aprobar paso a produccion

- Health OK por 24 horas.
- QA por rol sin bloqueantes.
- Backups y restore probados.
- Logs sin errores criticos.
- `.env` productivo preparado con demo desactivada.
- Passwords demo rotados o inexistentes.
- Dominio/HTTPS definitivo validado.
- Plan de rollback aprobado.
