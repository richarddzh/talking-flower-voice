param(
    [string]$Language = "zh_CN"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\\Scripts\\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not found. Run scripts\\init-venv.ps1 first."
}

chcp 65001 | Out-Null
Set-Location $RepoRoot
& $PythonExe -I ".\\webui.py" $Language
