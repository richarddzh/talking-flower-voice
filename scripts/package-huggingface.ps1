param(
    [string]$ModelRepoId = "richarddzh/talking-flower-voice"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Set-Location $RepoRoot
& $PythonExe ".\scripts\package-huggingface.py" `
    --model-repo-id $ModelRepoId `
    --force
if ($LASTEXITCODE -ne 0) {
    throw "Hugging Face package build failed."
}
