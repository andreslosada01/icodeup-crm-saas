$ErrorActionPreference = "Stop"

$V2Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$PgBin = Join-Path $V2Root "runtime\pgsql\bin"
$DataDir = Join-Path $V2Root "postgres-data"

if (Test-Path (Join-Path $PgBin "pg_ctl.exe")) {
    & (Join-Path $PgBin "pg_ctl.exe") -D $DataDir stop -m fast
}
