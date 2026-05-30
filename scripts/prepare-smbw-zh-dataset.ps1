param(
    [string]$ZipPath = "C:\Users\richard\Downloads\smbw_voice.zip",
    [string]$OutputRoot = ".\data\smbw_zh_train",
    [string]$SpeakerName = "talkflower_zh",
    [switch]$RunAsr
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$RawRoot = Join-Path $RepoRoot "data\smbw_voice_raw"
$NormalizedAudioDir = Join-Path $OutputRoot "audio"
$MetadataDir = Join-Path $OutputRoot "metadata"
$FinalListPath = Join-Path $MetadataDir "smbw_zh.list"
$ActivateScript = Join-Path $RepoRoot ".venv\Scripts\Activate.ps1"

function Expand-ChineseAudio {
    param(
        [string]$ArchivePath,
        [string]$Destination
    )

    Add-Type -AssemblyName System.IO.Compression.FileSystem

    if (-not (Test-Path $ArchivePath)) {
        throw "Zip not found: $ArchivePath"
    }

    if (Test-Path $Destination) {
        Remove-Item $Destination -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Destination | Out-Null

    $archive = [System.IO.Compression.ZipFile]::OpenRead($ArchivePath)
    try {
        foreach ($entry in $archive.Entries) {
            if ($entry.FullName -match '^Resource/(CNzh|TWzh)/') {
                $dest = Join-Path $Destination $entry.FullName
                $destDir = Split-Path $dest -Parent
                if (-not (Test-Path $destDir)) {
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }
                if (-not [string]::IsNullOrEmpty($entry.Name)) {
                    [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $dest, $true)
                }
            }
        }
    }
    finally {
        $archive.Dispose()
    }
}

function Copy-NormalizedAudio {
    param(
        [string]$SourceRoot,
        [string]$DestinationRoot
    )

    if (Test-Path $DestinationRoot) {
        Remove-Item $DestinationRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $DestinationRoot -Force | Out-Null

    $sources = @(
        @{ Lang = "CNzh"; Relative = "Resource\CNzh\Voice\TalkFlower_Placement_Stream" },
        @{ Lang = "TWzh"; Relative = "Resource\TWzh\Voice\TalkFlower_Placement_Stream" },
        @{ Lang = "TWzh"; Relative = "Resource\TWzh\Voice\TalkFlower_VoiceOnly_Stream" }
    )

    foreach ($source in $sources) {
        $fullSource = Join-Path $SourceRoot $source.Relative
        if (-not (Test-Path $fullSource)) {
            continue
        }

        Get-ChildItem $fullSource -File | ForEach-Object {
            $prefix = "{0}__{1}" -f $source.Lang, (Split-Path $fullSource -Leaf)
            $destName = "{0}__{1}" -f $prefix, $_.Name
            Copy-Item $_.FullName (Join-Path $DestinationRoot $destName) -Force
        }
    }
}

Set-Location $RepoRoot

Expand-ChineseAudio -ArchivePath $ZipPath -Destination $RawRoot

if (-not [System.IO.Path]::IsPathRooted($OutputRoot)) {
    $OutputRoot = Join-Path $RepoRoot $OutputRoot
    $NormalizedAudioDir = Join-Path $OutputRoot "audio"
    $MetadataDir = Join-Path $OutputRoot "metadata"
    $FinalListPath = Join-Path $MetadataDir "smbw_zh.list"
}

Copy-NormalizedAudio -SourceRoot $RawRoot -DestinationRoot $NormalizedAudioDir
New-Item -ItemType Directory -Path $MetadataDir -Force | Out-Null

if ($RunAsr) {
    if (-not (Test-Path $ActivateScript)) {
        throw "Virtual environment not found. Run scripts\init-venv.ps1 first."
    }

    . $ActivateScript

    python .\tools\asr\funasr_asr.py -i $NormalizedAudioDir -o $MetadataDir -l zh

    $rawListPath = Join-Path $MetadataDir "audio.list"
    if (-not (Test-Path $rawListPath)) {
        throw "ASR output not found: $rawListPath"
    }

    $normalizedLines = Get-Content $rawListPath -Encoding UTF8 | ForEach-Object {
        $parts = $_ -split '\|', 4
        if ($parts.Count -ne 4) {
            throw "Invalid ASR line: $_"
        }
        "{0}|{1}|zh|{2}" -f $parts[0], $SpeakerName, $parts[3]
    }

    Set-Content -Path $FinalListPath -Value $normalizedLines -Encoding UTF8
}

Write-Host ""
Write-Host "Dataset prepared at:" -ForegroundColor Green
Write-Host "  $OutputRoot"
Write-Host "Audio clips:" -ForegroundColor Green
Write-Host "  $NormalizedAudioDir"
if ($RunAsr) {
    Write-Host "Training list:" -ForegroundColor Green
    Write-Host "  $FinalListPath"
}
