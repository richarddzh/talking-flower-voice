param(
    [Parameter(Mandatory = $true)]
    [string]$ModelRepoId,
    [Parameter(Mandatory = $true)]
    [string]$SpaceRepoId,
    [switch]$PrivateModel,
    [switch]$PrivateSpace,
    [switch]$Create
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$arguments = @(
    ".\scripts\upload-huggingface.py",
    "--model-repo-id", $ModelRepoId,
    "--space-repo-id", $SpaceRepoId
)
if ($PrivateModel) {
    $arguments += "--private-model"
}
if ($PrivateSpace) {
    $arguments += "--private-space"
}
if ($Create) {
    $arguments += "--create"
}

Set-Location $RepoRoot
& $PythonExe @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Hugging Face upload failed."
}
