param(
    [string]$ExpName = "talkflower_zh_v2pp_strict",
    [ValidateSet("v1", "v2", "v3", "v4", "v2Pro", "v2ProPlus")]
    [string]$Version = "v2ProPlus",
    [string]$GpuNumbers = "0",
    [int]$BatchSize = 2,
    [int]$Epochs = 18,
    [int]$SaveEveryEpoch = 6,
    [switch]$Half
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$TempDir = Join-Path $RepoRoot "TEMP"
$ConfigPath = Join-Path $TempDir ("tmp_s1_" + $ExpName + ".yaml")

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not found. Run scripts\init-venv.ps1 first."
}

New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
Set-Location $RepoRoot
$env:_CUDA_VISIBLE_DEVICES = $GpuNumbers.Replace("-", ",")
$env:hz = "25hz"

& $PythonExe ".\scripts\build-train-config.py" gpt --exp-name $ExpName --version $Version --batch-size $BatchSize --epochs $Epochs --save-every-epoch $SaveEveryEpoch --is-half ([string]$Half.IsPresent) --output $ConfigPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to build GPT training config."
}

& $PythonExe -s ".\GPT_SoVITS\s1_train.py" --config_file $ConfigPath
if ($LASTEXITCODE -ne 0) {
    throw "GPT training failed."
}
