$ErrorActionPreference = "Stop"

$V2Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$PgBin = Join-Path $V2Root "runtime\pgsql\bin"
$DataDir = Join-Path $V2Root "postgres-data"
$LogFile = Join-Path $V2Root "postgres.log"
$PassFile = Join-Path $V2Root "runtime\pgpass.tmp"
$EnvFile = Join-Path $V2Root ".env"

if (-not (Test-Path (Join-Path $PgBin "pg_ctl.exe"))) {
    throw "No se encontro PostgreSQL portable en $PgBin. Revisa docs/ARRANQUE_LOCAL.md."
}

if (-not (Test-Path $EnvFile)) {
    throw "No se encontro $EnvFile. Crea v2/.env desde v2/.env.example."
}

$DatabaseUrl = (Get-Content -LiteralPath $EnvFile | Where-Object { $_ -match "^DATABASE_URL=" } | Select-Object -First 1) -replace "^DATABASE_URL=", ""
if ($DatabaseUrl -notmatch "^postgresql\+psycopg://([^:]+):([^@]+)@([^:/]+):?([0-9]+)?/([^?]+)") {
    throw "DATABASE_URL no tiene el formato esperado para desarrollo local."
}

$DbUser = $Matches[1]
$DbPassword = $Matches[2]
$DbHost = $Matches[3]
$DbPort = if ($Matches[4]) { [int]$Matches[4] } else { 5432 }
$DbName = $Matches[5]

if (-not (Test-Path (Join-Path $DataDir "PG_VERSION"))) {
    New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
    Set-Content -LiteralPath $PassFile -Value $DbPassword -NoNewline
    & (Join-Path $PgBin "initdb.exe") -D $DataDir -U $DbUser -A scram-sha-256 --pwfile=$PassFile -E UTF8 --locale=C
    Remove-Item -LiteralPath $PassFile -Force
}

$isListening = (Test-NetConnection $DbHost -Port $DbPort -WarningAction SilentlyContinue).TcpTestSucceeded
if (-not $isListening) {
    & (Join-Path $PgBin "pg_ctl.exe") -D $DataDir -l $LogFile -o "`"-h`" `"$DbHost`" `"-p`" `"$DbPort`"" start
    Start-Sleep -Seconds 3
}

$env:PGPASSWORD = $DbPassword
$databaseExists = & (Join-Path $PgBin "psql.exe") -h $DbHost -p $DbPort -U $DbUser -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DbName'"
if (($databaseExists | Out-String).Trim() -ne "1") {
    & (Join-Path $PgBin "createdb.exe") -h $DbHost -p $DbPort -U $DbUser $DbName
}

Write-Host "PostgreSQL listo en $DbHost`:$DbPort / base $DbName"
