$ErrorActionPreference = 'Stop'

$agentRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path (Split-Path $agentRoot) "venvs/hades"

if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

& "$venvPath/Scripts/Activate.ps1"

Set-Location $agentRoot

python .\main.py @args
