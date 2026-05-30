param(
    [string]$ZipPath = "C:\Users\richard\Downloads\smbw_voice.zip",
    [string]$OutputRoot = ".\data\smbw_zh_train",
    [string]$SpeakerName = "talkflower_zh",
    [switch]$SkipModelDownload
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not $SkipModelDownload) {
    & ".\scripts\download-modelscope-model.ps1" -DownloadChineseAsr
    if ($LASTEXITCODE -ne 0) {
        throw "ModelScope asset preparation failed."
    }
}

& ".\scripts\prepare-smbw-zh-dataset.ps1" -ZipPath $ZipPath -OutputRoot $OutputRoot -SpeakerName $SpeakerName -RunAsr
if ($LASTEXITCODE -ne 0) {
    throw "Chinese dataset preparation failed."
}

Write-Host ""
Write-Host "SMBW Chinese training assets are ready." -ForegroundColor Green
Write-Host "Dataset root: $OutputRoot" -ForegroundColor Green
