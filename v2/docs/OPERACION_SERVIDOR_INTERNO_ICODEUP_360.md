# Operacion servidor interno Icodeup 360

## 1. Estado actual del servidor interno

Icodeup 360 queda preparado para operar en el servidor fisico interno de Icodeup antes de publicar dominio externo.

- IP interna: `10.201.16.53`
- Acceso interno actual: `http://10.201.16.53`
- Servicio systemd: `icodeup360.service`
- Backend interno: `127.0.0.1:8020`
- Nginx interno: puerto `80`
- PostgreSQL local en el mismo servidor
- Base: `icodeup360_prod`
- Usuario BD: `icodeup360_user`
- Alembic esperado: `20260611_0006 (head)`

No publicar directamente puertos internos como `8020`, `8030` o `8040`. El acceso de usuarios debe entrar por Nginx en puertos estandar.

## 2. Validar servicios

```bash
systemctl status icodeup360
systemctl status nginx
systemctl status postgresql
```

Los tres servicios deben aparecer activos. Si `icodeup360` esta caido, revisar logs antes de reiniciar.

## 3. Validar health

```bash
curl http://127.0.0.1:8020/api/health
curl http://127.0.0.1/api/health
curl http://10.201.16.53/api/health
```

Respuesta esperada:

```json
{"ok":true,"app":"Icodeup 360","environment":"production","port":8020}
```

El campo de base de datos debe indicar PostgreSQL conectado.

## 4. Revisar logs

```bash
journalctl -u icodeup360 -n 100 --no-pager
tail -n 100 /var/log/nginx/error.log
```

Los logs no deben mostrar contrasenas, tokens, URLs completas con credenciales, dumps SQL, CSV completos ni datos sensibles.

## 5. Reiniciar servicio de aplicacion

```bash
sudo systemctl restart icodeup360
systemctl status icodeup360
curl http://127.0.0.1:8020/api/health
```

Reiniciar solo despues de validar configuracion, migraciones y logs.

## 6. Validar Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
curl http://127.0.0.1/api/health
curl http://10.201.16.53/api/health
```

Si `nginx -t` falla, no hacer reload. Corregir configuracion primero.

## 7. Variables productivas internas

En ambiente interno productivo mantener desactivado:

```bash
ENABLE_DEMO_DATA=false
ENABLE_DEMO_SEEDS=false
ENABLE_PILOT_ICODEUP_SEED=false
```

No guardar `.env` en Git. El archivo real debe vivir en el servidor con permisos restringidos.

## 8. Checklist rapido post reinicio

- `systemctl status icodeup360` activo.
- `systemctl status nginx` activo.
- `systemctl status postgresql` activo.
- Health OK por backend directo.
- Health OK por Nginx local.
- Health OK por IP interna.
- Login admin OK.
- Logs sin errores criticos.
- No hay 404 recurrente de `/favicon.ico`.
- Puertos internos no publicados hacia Internet.
