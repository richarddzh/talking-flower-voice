param(
    [string]$Python = "python",
    [switch]$SkipTorch,
    [switch]$SkipProjectInstall
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $RepoRoot ".venv"
$ActivateScript = Join-Path $VenvPath "Scripts\\Activate.ps1"
$AliyunIndex = "https://mirrors.aliyun.com/pypi/simple/"
$TorchWheel = "https://mirrors.aliyun.com/pytorch-wheels/cu128/torch-2.10.0+cu128-cp312-cp312-win_amd64.whl"
$TorchVisionWheel = "https://mirrors.aliyun.com/pytorch-wheels/cu128/torchvision-0.25.0+cu128-cp312-cp312-win_amd64.whl"
$TorchAudioWheel = "https://mirrors.aliyun.com/pytorch-wheels/cu128/torchaudio-2.10.0+cu128-cp312-cp312-win_amd64.whl"

Set-Location $RepoRoot

if (-not (Test-Path $VenvPath)) {
    & $Python -m venv $VenvPath
}

. $ActivateScript

python -m pip install --disable-pip-version-check --upgrade pip setuptools wheel -i $AliyunIndex

if (-not $SkipTorch) {
    python -m pip install --no-cache-dir $TorchWheel $TorchVisionWheel
    python -m pip install --no-cache-dir $TorchAudioWheel
}

python -m pip install --disable-pip-version-check -r extra-req.txt --no-deps -i $AliyunIndex
python -m pip install --disable-pip-version-check -r requirements.txt -i $AliyunIndex

if (-not $SkipProjectInstall) {
    python -m pip install --disable-pip-version-check --no-deps -e . -i $AliyunIndex
}

Write-Host ""
Write-Host "Virtual environment is ready:" -ForegroundColor Green
Write-Host "  $VenvPath"
Write-Host ""
Write-Host "Activate it with:" -ForegroundColor Green
Write-Host "  .\\.venv\\Scripts\\Activate.ps1"


