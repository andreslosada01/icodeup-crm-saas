# Backup Local Windows PostgreSQL

## 1. Objetivo

Respaldar la base local `icodeup_crm_local` usada para QA funcional y piloto interno de Icodeup 360 en Windows.

Este backup es local. No debe subirse al repositorio.

## 2. Script

Ejemplo versionado:

```text
v2/scripts/backup_local_windows_postgres.ps1.example
```

No se versiona un `.ps1` con secretos. Si se crea una copia local ejecutable, debe permanecer fuera de Git.

## 3. Destino

```text
C:\icodeup360-local\backups
```

Formato:

```text
icodeup_crm_local_YYYYMMDD_HHMMSS.dump
```

## 4. Ejecucion

Desde la raiz del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\scripts\backup_local_windows_postgres.ps1.example
```

Si PostgreSQL requiere password y no se quiere usar prompt interactivo:

```powershell
$env:PGPASSWORD="password-local-temporal"
powershell -ExecutionPolicy Bypass -File .\v2\scripts\backup_local_windows_postgres.ps1.example
Remove-Item Env:PGPASSWORD
```

No guardar `PGPASSWORD` en archivos del repositorio.

## 5. Validacion

Despues del backup:

- confirmar que el `.dump` exista en `C:\icodeup360-local\backups`
- confirmar que el tamano sea mayor a 0 bytes
- no mover el backup al repositorio
- no subir `.dump` a GitHub

## 6. Restore

Existe ejemplo seguro:

```text
v2/scripts/restore_local_windows_postgres.ps1.example
```

Ese script exige escribir `RESTAURAR_LOCAL` para evitar restauraciones accidentales. Restaurar puede eliminar/reemplazar datos locales.
