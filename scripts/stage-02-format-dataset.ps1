param(
    [string]$ListPath = ".\data\smbw_zh_train\metadata\smbw_zh_strict_v2pp.list",
    [string]$AudioDir = ".\data\smbw_zh_train\audio",
    [string]$ExpName = "talkflower_zh_v2pp_strict",
    [ValidateSet("v1", "v2", "v3", "v4", "v2Pro", "v2ProPlus")]
    [string]$Version = "v2ProPlus",
    [string]$GpuNumbers = "0",
    [string]$BertPretrainedDir = ".\GPT_SoVITS\pretrained_models\chinese-roberta-wwm-ext-large",
    [string]$HubertPretrainedDir = ".\GPT_SoVITS\pretrained_models\chinese-hubert-base",
    [string]$PretrainedS2G = ".\GPT_SoVITS\pretrained_models\v2Pro\s2Gv2ProPlus.pth"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$OptDir = Join-Path $RepoRoot ("logs\" + $ExpName)

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not found. Run scripts\init-venv.ps1 first."
}

function Resolve-RepoPath {
    param([string]$PathValue)
    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return $PathValue
    }
    return (Join-Path $RepoRoot $PathValue)
}

function Invoke-PartitionedScript {
    param(
        [string]$ScriptPath,
        [string]$GpuList
    )
    $parts = $GpuList -split "-"
    $allParts = $parts.Count
    for ($i = 0; $i -lt $allParts; $i++) {
        $env:i_part = [string]$i
        $env:all_parts = [string]$allParts
        $env:_CUDA_VISIBLE_DEVICES = [string]$parts[$i]
        & $PythonExe -s $ScriptPath
        if ($LASTEXITCODE -ne 0) {
            throw "Dataset formatting step failed: $ScriptPath part $i"
        }
    }
}

Set-Location $RepoRoot
New-Item -ItemType Directory -Path $OptDir -Force | Out-Null

$env:inp_text = Resolve-RepoPath $ListPath
$env:inp_wav_dir = Resolve-RepoPath $AudioDir
$env:exp_name = $ExpName
$env:opt_dir = $OptDir
$env:bert_pretrained_dir = Resolve-RepoPath $BertPretrainedDir
$env:cnhubert_base_dir = Resolve-RepoPath $HubertPretrainedDir
$env:pretrained_s2G = Resolve-RepoPath $PretrainedS2G
$env:s2config_path = if ($Version -in @("v2Pro", "v2ProPlus")) { "GPT_SoVITS/configs/s2$Version.json" } else { "GPT_SoVITS/configs/s2.json" }
$env:is_half = "False"

Invoke-PartitionedScript ".\GPT_SoVITS\prepare_datasets\1-get-text.py" $GpuNumbers
$mergedText = Join-Path $OptDir "2-name2text.txt"
$textRows = New-Object System.Collections.Generic.List[string]
$parts = $GpuNumbers -split "-"
for ($i = 0; $i -lt $parts.Count; $i++) {
    $partPath = Join-Path $OptDir ("2-name2text-" + $i + ".txt")
    if (Test-Path $partPath) {
        Get-Content $partPath -Encoding UTF8 | ForEach-Object { if ($_ -ne "") { $textRows.Add($_) } }
        Remove-Item $partPath -Force
    }
}
Set-Content -Path $mergedText -Value $textRows -Encoding UTF8

Invoke-PartitionedScript ".\GPT_SoVITS\prepare_datasets\2-get-hubert-wav32k.py" $GpuNumbers
if ($Version -like "*Pro*") {
    Invoke-PartitionedScript ".\GPT_SoVITS\prepare_datasets\2-get-sv.py" $GpuNumbers
}
Invoke-PartitionedScript ".\GPT_SoVITS\prepare_datasets\3-get-semantic.py" $GpuNumbers

$semanticRows = New-Object System.Collections.Generic.List[string]
$semanticRows.Add("item_name`tsemantic_audio")
for ($i = 0; $i -lt $parts.Count; $i++) {
    $partPath = Join-Path $OptDir ("6-name2semantic-" + $i + ".tsv")
    if (Test-Path $partPath) {
        Get-Content $partPath -Encoding UTF8 | ForEach-Object { if ($_ -ne "") { $semanticRows.Add($_) } }
        Remove-Item $partPath -Force
    }
}
Set-Content -Path (Join-Path $OptDir "6-name2semantic.tsv") -Value $semanticRows -Encoding UTF8

Write-Host ""
Write-Host "Stage 02 complete:" -ForegroundColor Green
Write-Host "  $OptDir"
