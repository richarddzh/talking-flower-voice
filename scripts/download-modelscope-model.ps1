param(
    [string]$PretrainedRepoId = "XXXXRT/GPT-SoVITS-Pretrained",
    [string]$StagingDir = ".\\_src_tmp\\modelscope-downloads",
    [switch]$DownloadChineseAsr
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$PretrainedTarget = Join-Path $RepoRoot "GPT_SoVITS"
$G2pwTarget = Join-Path $RepoRoot "GPT_SoVITS\\text"
$AsrTarget = Join-Path $RepoRoot "tools\\asr\\models"

if (-not (Get-Command modelscope -ErrorAction SilentlyContinue)) {
    throw "ModelScope CLI not found in PATH."
}

function Resolve-PathInRepo {
    param([string]$PathValue)

    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return $PathValue
    }

    return (Join-Path $RepoRoot $PathValue)
}

function Invoke-ModelScopeDownload {
    param(
        [string]$ModelId,
        [string]$LocalDir,
        [string[]]$Files
    )

    $args = @("download", "--model", $ModelId, "--local_dir", $LocalDir)
    if ($Files) {
        $args += $Files
    }

    & modelscope @args
    if ($LASTEXITCODE -ne 0) {
        throw "ModelScope download failed for $ModelId"
    }
}

$StagingDir = Resolve-PathInRepo -PathValue $StagingDir
New-Item -ItemType Directory -Path $StagingDir -Force | Out-Null
Set-Location $RepoRoot

$pretrainedZip = Join-Path $StagingDir "pretrained_models.zip"
$g2pwZip = Join-Path $StagingDir "G2PWModel.zip"

Invoke-ModelScopeDownload -ModelId $PretrainedRepoId -LocalDir $StagingDir -Files @("pretrained_models.zip", "G2PWModel.zip")

if (-not (Test-Path $pretrainedZip)) {
    throw "Missing downloaded file: $pretrainedZip"
}
if (-not (Test-Path $g2pwZip)) {
    throw "Missing downloaded file: $g2pwZip"
}

Expand-Archive -Path $pretrainedZip -DestinationPath $PretrainedTarget -Force
Expand-Archive -Path $g2pwZip -DestinationPath $G2pwTarget -Force

if ($DownloadChineseAsr) {
    New-Item -ItemType Directory -Path $AsrTarget -Force | Out-Null

    $asrModels = @(
        @{ Id = "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch"; Dir = "speech_fsmn_vad_zh-cn-16k-common-pytorch" },
        @{ Id = "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch"; Dir = "punc_ct-transformer_zh-cn-common-vocab272727-pytorch" },
        @{ Id = "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"; Dir = "speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch" }
    )

    foreach ($model in $asrModels) {
        $localDir = Join-Path $AsrTarget $model.Dir
        Invoke-ModelScopeDownload -ModelId $model.Id -LocalDir $localDir
    }
}

Write-Host ""
Write-Host "ModelScope assets downloaded:" -ForegroundColor Green
Write-Host "  GPT_SoVITS\\pretrained_models" -ForegroundColor Green
Write-Host "  GPT_SoVITS\\text\\G2PWModel" -ForegroundColor Green
if ($DownloadChineseAsr) {
    Write-Host "  tools\\asr\\models" -ForegroundColor Green
}
