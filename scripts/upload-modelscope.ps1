param(
    [Parameter(Mandatory = $true)]
    [string]$RepoId,
    [switch]$Private,
    [switch]$Create
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not found. Run scripts\init-venv.ps1 first."
}

Set-Location $RepoRoot
$argsList = @(".\scripts\upload-modelscope.py", "--repo-id", $RepoId)
if ($Private) {
    $argsList += "--private"
}
if ($Create) {
    $argsList += "--create"
}

& $PythonExe @argsList
if ($LASTEXITCODE -ne 0) {
    throw "ModelScope upload failed."
}
