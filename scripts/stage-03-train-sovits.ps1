param(
    [string]$ExpName = "talkflower_zh_v2pp_strict",
    [ValidateSet("v1", "v2", "v3", "v4", "v2Pro", "v2ProPlus")]
    [string]$Version = "v2ProPlus",
    [string]$GpuNumbers = "0",
    [int]$BatchSize = 4,
    [int]$Epochs = 10,
    [int]$SaveEveryEpoch = 5,
    [switch]$Half
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$TempDir = Join-Path $RepoRoot "TEMP"
$ConfigPath = Join-Path $TempDir ("tmp_s2_" + $ExpName + ".json")

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not found. Run scripts\init-venv.ps1 first."
}

New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
Set-Location $RepoRoot

& $PythonExe ".\scripts\build-train-config.py" sovits --exp-name $ExpName --version $Version --gpu-numbers $GpuNumbers --batch-size $BatchSize --epochs $Epochs --save-every-epoch $SaveEveryEpoch --is-half ([string]$Half.IsPresent) --output $ConfigPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to build SoVITS training config."
}

& $PythonExe -s ".\GPT_SoVITS\s2_train.py" --config $ConfigPath
if ($LASTEXITCODE -ne 0) {
    throw "SoVITS training failed."
}
