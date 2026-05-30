param(
    [switch]$Training
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$requiredInference = @(
    "GPT_weights_v2ProPlus\talkflower_zh_v2pp_strict-e18.ckpt",
    "SoVITS_weights_v2ProPlus\talkflower_zh_v2pp_strict_e10_s2120.pth",
    "GPT_SoVITS\pretrained_models\chinese-roberta-wwm-ext-large\config.json",
    "GPT_SoVITS\pretrained_models\chinese-roberta-wwm-ext-large\pytorch_model.bin",
    "GPT_SoVITS\pretrained_models\chinese-hubert-base\config.json",
    "GPT_SoVITS\pretrained_models\chinese-hubert-base\pytorch_model.bin",
    "GPT_SoVITS\text\G2PWModel\config.json",
    "GPT_SoVITS\text\G2PWModel\pytorch_model.bin",
    "data\smbw_zh_train\audio\TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3"
)

$requiredTraining = @(
    "data\smbw_zh_train\metadata\smbw_zh_strict_v2pp.list",
    "logs\talkflower_zh_v2pp_strict\2-name2text.txt",
    "logs\talkflower_zh_v2pp_strict\6-name2semantic.tsv",
    "GPT_SoVITS\pretrained_models\s1v3.ckpt",
    "GPT_SoVITS\pretrained_models\v2Pro\s2Gv2ProPlus.pth",
    "GPT_SoVITS\pretrained_models\v2Pro\s2Dv2ProPlus.pth"
)

$paths = @()
$paths += $requiredInference
if ($Training) {
    $paths += $requiredTraining
}

$missing = @()
foreach ($path in $paths) {
    if (-not (Test-Path (Join-Path $RepoRoot $path))) {
        $missing += $path
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Missing required assets:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  $_" }
    Write-Host ""
    Write-Host "See docs\ASSETS.md for how to restore assets after clone."
    exit 1
}

Write-Host "All required assets are present." -ForegroundColor Green
if ($Training) {
    Write-Host "Training asset check: OK"
} else {
    Write-Host "Inference asset check: OK"
}
