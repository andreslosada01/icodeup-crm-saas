$ErrorActionPreference = "Stop"

$V2Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$BackendRoot = Join-Path $V2Root "backend"
$Python = Join-Path $BackendRoot ".venv\Scripts\python.exe"

& (Join-Path $PSScriptRoot "start-postgres.ps1")

if (-not (Test-Path $Python)) {
    throw "No se encontro el entorno Python en $Python. Instala dependencias antes de iniciar V2."
}

$backendListening = (Test-NetConnection 127.0.0.1 -Port 8020 -WarningAction SilentlyContinue).TcpTestSucceeded
if (-not $backendListening) {
    Start-Process -FilePath $Python -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8020" -WorkingDirectory $BackendRoot -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8020/api/health" | Select-Object -ExpandProperty Content
