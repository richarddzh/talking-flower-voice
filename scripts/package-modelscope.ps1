$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not found. Run scripts\init-venv.ps1 first."
}

Set-Location $RepoRoot
& $PythonExe ".\scripts\package-modelscope.py" --force
if ($LASTEXITCODE -ne 0) {
    throw "ModelScope package build failed."
}
