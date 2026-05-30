param(
    [string]$Text = "你好，我是闲聊花花。今天也一起开心地冒险吧。",
    [string]$Output = ".\outputs\talkflower_latest.wav",
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda",
    [switch]$Half
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not found. Run scripts\init-venv.ps1 first."
}

Set-Location $RepoRoot
$argsList = @(
    ".\scripts\talkflower-tts.py",
    "--text", $Text,
    "--output", $Output,
    "--device", $Device
)
if ($Half) {
    $argsList += "--is-half"
}

& $PythonExe @argsList
if ($LASTEXITCODE -ne 0) {
    throw "TalkFlower inference failed."
}
