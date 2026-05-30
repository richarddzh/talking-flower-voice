param(
    [string]$Text = "你好，我是闲聊花花。今天也一起开心地冒险吧。",
    [int]$Warmup = 1,
    [int]$Runs = 3,
    [switch]$SkipGpu,
    [switch]$SkipCpu
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$ReportDir = Join-Path $RepoRoot "outputs\benchmark"

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not found. Run scripts\init-venv.ps1 first."
}

New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
Set-Location $RepoRoot

if (-not $SkipGpu) {
    & $PythonExe ".\scripts\talkflower-tts.py" --benchmark --device cuda --text $Text --warmup $Warmup --runs $Runs --report ".\outputs\benchmark\talkflower_cuda.json"
    if ($LASTEXITCODE -ne 0) {
        throw "CUDA benchmark failed."
    }
}

if (-not $SkipCpu) {
    & $PythonExe ".\scripts\talkflower-tts.py" --benchmark --device cpu --text $Text --warmup $Warmup --runs $Runs --report ".\outputs\benchmark\talkflower_cpu.json"
    if ($LASTEXITCODE -ne 0) {
        throw "CPU benchmark failed."
    }
}

Write-Host ""
Write-Host "Benchmark reports:" -ForegroundColor Green
Get-ChildItem $ReportDir -Filter "talkflower_*.json" | ForEach-Object {
    Write-Host "  $($_.FullName)"
}
