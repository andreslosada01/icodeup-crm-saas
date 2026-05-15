$ErrorActionPreference = "Stop"

$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (Test-Path $BundledPython) {
  & $BundledPython server.py
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  python server.py
} else {
  Write-Error "No se encontro Python. Instala Python 3.11+ o usa el runtime incluido de Codex."
}
