$ErrorActionPreference = 'Stop'

$agentRoot = 'E:/AI/Hades'
$venvPath = 'E:/AI/venvs/hades'

if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

& "$venvPath/Scripts/Activate.ps1"

Set-Location $agentRoot

python .\main.py @args
