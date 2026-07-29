# Admin corporativo Icodeup 360

## 1. Contexto

En el servidor interno se identifico que el login funciona con:

```text
admin@icodeup.local
```

Ese usuario no debe eliminarse ni modificarse de forma destructiva. Para operar con un correo corporativo se recomienda crear o resetear un segundo admin de plataforma, por ejemplo:

```text
admin@icodeupadvisors.com
```

## 2. Script example disponible

```bash
v2/scripts/create_or_reset_platform_admin.py.example
```

El script:

- lee `.env`
- usa `SessionLocal`
- usa los modelos reales `User`, `Tenant`, `Role` y `UserProfile`
- crea o resetea un admin de plataforma
- no imprime la contrasena
- mantiene `admin@icodeup.local`

## 3. Copiar script real no versionado

En el servidor:

```bash
cd /opt/icodeup360/app/v2
cp scripts/create_or_reset_platform_admin.py.example scripts/create_or_reset_platform_admin.py
chmod 700 scripts/create_or_reset_platform_admin.py
```

No subir el script real si llega a contener ajustes locales.

## 4. Generar contrasena segura

```bash
openssl rand -base64 18
```

Copiar el resultado en un gestor de contrasenas. No pegarlo en chats, tickets, docs ni historiales visibles.

## 5. Ejecutar creacion o reset

Opcion recomendada con prompt temporal:

```bash
cd /opt/icodeup360/app/v2
read -s NEW_ADMIN_PASSWORD
export NEW_ADMIN_PASSWORD
export PLATFORM_ADMIN_EMAIL="admin@icodeupadvisors.com"
python scripts/create_or_reset_platform_admin.py
unset NEW_ADMIN_PASSWORD
```

Alternativa con argumento de correo:

```bash
cd /opt/icodeup360/app/v2
read -s NEW_ADMIN_PASSWORD
export NEW_ADMIN_PASSWORD
python scripts/create_or_reset_platform_admin.py --email admin@icodeupadvisors.com
unset NEW_ADMIN_PASSWORD
```

El script no imprime la contrasena.

## 6. Reiniciar y probar

```bash
sudo systemctl restart icodeup360
curl http://127.0.0.1:8020/api/health
```

Luego probar login en:

```text
http://10.201.16.53
```

## 7. Reglas

- No registrar contrasenas en documentacion.
- No versionar `.env`.
- No eliminar `admin@icodeup.local` hasta tener procedimiento formal de rotacion.
- No crear admins de plataforma para usuarios cliente.
- Revisar auditoria despues del primer login del nuevo admin.
