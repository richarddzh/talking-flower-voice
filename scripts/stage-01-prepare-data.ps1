param(
    [string]$ZipPath = "C:\Users\richard\Downloads\smbw_voice.zip",
    [string]$OutputRoot = ".\data\smbw_zh_train",
    [string]$SpeakerName = "talkflower_zh",
    [switch]$SkipModelDownload
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not found. Run scripts\init-venv.ps1 first."
}

Set-Location $RepoRoot
& ".\scripts\prepare-smbw-training.ps1" -ZipPath $ZipPath -OutputRoot $OutputRoot -SpeakerName $SpeakerName -SkipModelDownload:$SkipModelDownload
if ($LASTEXITCODE -ne 0) {
    throw "Base SMBW dataset preparation failed."
}

$MetadataDir = Join-Path $OutputRoot "metadata"
$RawList = Join-Path $MetadataDir "smbw_zh.list"
$CleanList = Join-Path $MetadataDir "smbw_zh_clean_v2pp.list"
$CleanDropped = Join-Path $MetadataDir "smbw_zh_clean_v2pp_dropped.json"
$StrictList = Join-Path $MetadataDir "smbw_zh_strict_v2pp.list"
$StrictDropped = Join-Path $MetadataDir "smbw_zh_strict_v2pp_dropped.json"

& $PythonExe ".\scripts\filter-gpt-sovits-list.py" --input $RawList --output $CleanList --dropped $CleanDropped --min-cjk 4 --exclude-name-regex "VoiceOnly"
if ($LASTEXITCODE -ne 0) {
    throw "Clean list filtering failed."
}

& $PythonExe ".\scripts\filter-gpt-sovits-list.py" --input $CleanList --output $StrictList --dropped $StrictDropped --min-cjk 4 --exclude-name-regex "CommonBC"
if ($LASTEXITCODE -ne 0) {
    throw "Strict list filtering failed."
}

Write-Host ""
Write-Host "Stage 01 complete:" -ForegroundColor Green
Write-Host "  $StrictList"
