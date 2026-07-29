# Publicacion futura dominio y SSL Icodeup 360

## 1. Estado actual

Por ahora Icodeup 360 queda publicado solo en red interna:

```text
http://10.201.16.53
```

La exposicion publica por dominio, DNS y SSL se realizara en una fase posterior.

## 2. Dominio principal recomendado

Para la plataforma empresarial Icodeup se recomienda:

```text
app.icodeup.com
```

Nombre comercial sugerido:

```text
Icodeup Enterprise Platform
```

## 3. Subdominios por producto

- `collects.icodeup.com` para Collects 360.
- `paycontrol.icodeup.com` para PayControl 360.
- `foodflow.icodeup.com` para FoodFlow 360.
- `prodline.icodeup.com` para ProdLine 360.

Estos productos deben convivir bajo la estrategia Icodeup, sin exponer puertos internos.

## 4. DNS

En GoDaddy crear registros tipo A apuntando a:

```text
181.49.137.178
```

Ejemplos:

```text
app.icodeup.com        A    181.49.137.178
collects.icodeup.com   A    181.49.137.178
paycontrol.icodeup.com A    181.49.137.178
foodflow.icodeup.com   A    181.49.137.178
prodline.icodeup.com   A    181.49.137.178
```

## 5. Nginx como reverse proxy

Nginx debe recibir trafico publico en puertos estandar:

- `80` HTTP
- `443` HTTPS

Y reenviar internamente a servicios privados, por ejemplo:

- Icodeup 360 backend: `127.0.0.1:8020`
- Otros productos futuros: `127.0.0.1:8030`, `127.0.0.1:8040`

No publicar los puertos internos directamente.

## 6. HTTPS

Opciones:

- Certbot con Let's Encrypt.
- Certificado administrado por proveedor.
- Certificado corporativo equivalente.

Ejemplo futuro:

```bash
sudo certbot --nginx -d app.icodeup.com
```

Antes de ejecutar Certbot, DNS debe resolver correctamente hacia el servidor publico.

## 7. SSH administrativo

SSH puede usar un puerto externo alterno con NAT hacia el puerto `22` interno si la politica de red lo requiere.

La app web no debe depender de puertos alternos para usuarios finales. Para usuarios finales usar siempre `80/443`.

## 8. Reglas de seguridad

- No publicar `8020`, `8030`, `8040`.
- No subir `.env`.
- No subir certificados privados.
- No subir dumps.
- No activar data demo en produccion publica.
- Usar secretos fuertes.
- Validar backups y restore antes de abrir al publico.
- Activar logs y monitoreo antes de salida comercial.
