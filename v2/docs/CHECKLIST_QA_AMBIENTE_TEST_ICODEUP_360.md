# Checklist QA ambiente TEST Icodeup 360

## 1. Health TEST

- `curl http://127.0.0.1:8021/api/health` responde OK.
- `curl http://10.201.16.53:8081/api/health` responde OK.
- El campo `environment` indica `test`.
- La base conectada corresponde a `icodeup360_test`.
- `alembic current` indica head vigente.

## 2. Produccion no afectada

- `curl http://127.0.0.1:8020/api/health` sigue OK.
- `curl http://10.201.16.53/api/health` sigue OK.
- `systemctl status icodeup360` sigue activo.
- `systemctl status icodeup360-test` activo solo para TEST.
- No se modifico `/opt/icodeup360/app`.

## 3. Login admin TEST

- Login con admin TEST OK.
- Login fallido muestra error controlado.
- No se usan passwords productivos.
- Si se creo admin temporal, queda documentada su rotacion fuera del repo.

## 4. Dashboard y menus

- Dashboard carga.
- Sidebar y topbar cargan.
- Gobierno SaaS visible solo para plataforma.
- Admin empresa no ve gobierno global indebido.
- Operativo no ve administracion indebida.
- Modulos desactivados no aparecen.

## 5. Telefonia simulada

- Modulo Telefonia visible solo si el tenant/rol lo permite.
- Extension del usuario de prueba configurada si aplica.
- Click-to-call usa `POST /api/telephony/click-to-call`.
- No abre selector de apps externas.
- No usa `tel:`, `sip:` ni `callto:`.
- Historial de llamadas registra el intento simulado.

## 6. Operacion principal

- Clientes cargan.
- Cola de gestion carga.
- Perfil de cliente abre.
- Gestiones se guardan si el usuario tiene permiso.
- Promesas cargan.
- Pagos cargan.
- Acuerdos cargan.
- Juridico carga.
- Documentos cargan.
- Ventas carga si el modulo esta activo.

## 7. Excel web, cargas y exportes

- Excel Web carga.
- Cargas/repartos cargan.
- Exportes autorizados funcionan.
- Exportes no autorizados devuelven 403 controlado.
- No hay fuga entre tenants.

## 8. Logs

- `journalctl -u icodeup360-test -n 100 --no-pager` sin errores criticos.
- `/var/log/icodeup360_test/app.err.log` sin trazas repetitivas.
- Nginx en puerto `8081` sin errores criticos.
- No aparecen passwords, tokens, dumps, CSV completos ni datos sensibles.

## 9. Backups TEST

- Backup TEST apunta a `icodeup360_test`.
- Backup se guarda en `/var/backups/icodeup360_test`.
- El archivo no esta vacio.
- No se crean dumps dentro del repositorio.

## 10. Criterio de aprobacion

- TEST responde por `10.201.16.53:8081`.
- Produccion interna sigue respondiendo por `10.201.16.53`.
- DB TEST confirmada como `icodeup360_test`.
- Logs sin errores criticos.
- Click-to-call no abre apps externas.
- No se versionaron secretos ni runtime.
