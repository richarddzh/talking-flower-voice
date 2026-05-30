param(
    [string]$ZipPath = "C:\Users\richard\Downloads\smbw_voice.zip",
    [string]$ExpName = "talkflower_zh_v2pp_strict",
    [string]$GpuNumbers = "0",
    [switch]$SkipModelDownload,
    [switch]$SkipData,
    [switch]$SkipFormat,
    [switch]$SkipSoVITS,
    [switch]$SkipGPT,
    [switch]$SkipTest
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not $SkipData) {
    & ".\scripts\stage-01-prepare-data.ps1" -ZipPath $ZipPath -SkipModelDownload:$SkipModelDownload
    if ($LASTEXITCODE -ne 0) { throw "Stage 01 failed." }
}

if (-not $SkipFormat) {
    & ".\scripts\stage-02-format-dataset.ps1" -ExpName $ExpName -GpuNumbers $GpuNumbers
    if ($LASTEXITCODE -ne 0) { throw "Stage 02 failed." }
}

if (-not $SkipSoVITS) {
    & ".\scripts\stage-03-train-sovits.ps1" -ExpName $ExpName -GpuNumbers $GpuNumbers
    if ($LASTEXITCODE -ne 0) { throw "Stage 03 failed." }
}

if (-not $SkipGPT) {
    & ".\scripts\stage-04-train-gpt.ps1" -ExpName $ExpName -GpuNumbers $GpuNumbers
    if ($LASTEXITCODE -ne 0) { throw "Stage 04 failed." }
}

if (-not $SkipTest) {
    & ".\scripts\stage-05-test-model.ps1"
    if ($LASTEXITCODE -ne 0) { throw "Stage 05 failed." }
}

Write-Host ""
Write-Host "All requested stages completed." -ForegroundColor Green
