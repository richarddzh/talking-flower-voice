param(
    [string]$Text = "你好，我是闲聊花花。今天也一起开心地冒险吧。",
    [string]$Output = ".\outputs\talkflower_zh_v2pp_strict_latest.wav",
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

& ".\scripts\infer-talkflower.ps1" -Text $Text -Output $Output -Device $Device
if ($LASTEXITCODE -ne 0) {
    throw "Model test inference failed."
}

Write-Host ""
Write-Host "Stage 05 complete:" -ForegroundColor Green
Write-Host "  $Output"
