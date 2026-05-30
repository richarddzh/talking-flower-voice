$ErrorActionPreference = "SilentlyContinue"
chcp 65001
Set-Location $PSScriptRoot
$runtimePath = Join-Path $PSScriptRoot "runtime"
$runtimePython = Join-Path $runtimePath "python.exe"
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    & $venvPython -I "$PSScriptRoot\webui.py" zh_CN
}
elseif (Test-Path $runtimePython) {
    $env:PATH = "$runtimePath;$env:PATH"
    & $runtimePython -I "$PSScriptRoot\webui.py" zh_CN
}
else {
    Write-Host "No Python runtime found. Run .\\scripts\\init-venv.ps1 first." -ForegroundColor Red
}
pause
