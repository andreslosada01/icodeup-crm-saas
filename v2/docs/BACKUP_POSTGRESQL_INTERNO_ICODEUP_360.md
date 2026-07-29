# Backup PostgreSQL interno Icodeup 360

## 1. Objetivo

Estandarizar backups manuales y diarios de PostgreSQL en el servidor interno sin imprimir contrasenas ni subir dumps al repositorio.

El script example disponible es:

```bash
v2/scripts/backup_postgres_from_env.sh.example
```

Lee `DATABASE_URL` desde el `.env` del servidor y ejecuta `pg_dump` con formato custom.

## 2. Crear script real no versionado

En el servidor:

```bash
cd /opt/icodeup360/app
sudo cp v2/scripts/backup_postgres_from_env.sh.example /usr/local/sbin/backup_icodeup360_postgres.sh
sudo chown root:root /usr/local/sbin/backup_icodeup360_postgres.sh
sudo chmod 700 /usr/local/sbin/backup_icodeup360_postgres.sh
```

No editar el archivo `.example` dentro del repo con rutas o secretos reales.

## 3. Probar backup manual

```bash
sudo ENV_FILE=/opt/icodeup360/app/v2/.env \
  BACKUP_DIR=/var/backups/icodeup360/manual \
  /usr/local/sbin/backup_icodeup360_postgres.sh
```

El comando debe mostrar solo:

- ruta del backup
- tamano en bytes

No debe imprimir `DATABASE_URL`.

## 4. Programar cron diario

Crear archivo:

```bash
sudo nano /etc/cron.d/icodeup360-backup
```

Contenido sugerido:

```cron
15 2 * * * root ENV_FILE=/opt/icodeup360/app/v2/.env BACKUP_DIR=/var/backups/icodeup360/daily /usr/local/sbin/backup_icodeup360_postgres.sh >> /var/log/icodeup360_backup.log 2>&1
```

Proteger logs:

```bash
sudo touch /var/log/icodeup360_backup.log
sudo chown root:root /var/log/icodeup360_backup.log
sudo chmod 600 /var/log/icodeup360_backup.log
```

## 5. Listar backups

```bash
sudo ls -lh /var/backups/icodeup360/manual
sudo ls -lh /var/backups/icodeup360/daily
```

Los archivos esperados terminan en `.dump`.

## 6. Restaurar en ambiente de prueba

Nunca restaurar directamente en produccion sin backup previo y ventana aprobada.

Ejemplo hacia una base de prueba:

```bash
sudo -u postgres createdb icodeup360_restore_test
pg_restore --no-owner --no-acl \
  --dbname=postgresql://icodeup360_user@127.0.0.1:5432/icodeup360_restore_test \
  /var/backups/icodeup360/manual/icodeup360_YYYYMMDD_HHMMSS.dump
```

Si el usuario requiere password, usar `.pgpass` seguro o una variable temporal local al shell, nunca registrar la contrasena en docs, chats ni scripts versionados.

## 7. Validaciones post restore

```bash
psql postgresql://icodeup360_user@127.0.0.1:5432/icodeup360_restore_test -c "select count(*) from tenants;"
psql postgresql://icodeup360_user@127.0.0.1:5432/icodeup360_restore_test -c "select count(*) from users;"
```

## 8. Reglas de seguridad

- No subir dumps al repo.
- No subir backups a GitHub.
- No copiar `.env` a tickets, chats o documentos.
- No imprimir `DATABASE_URL`.
- No guardar passwords en scripts versionados.
- Probar restore de forma periodica, no solo backup.
