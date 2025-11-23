# Apex Agent Task Runner
param(
    [Parameter(Position = 0)]
    [ValidateSet('launch', 'test', 'lint', 'clean', 'smoke', 'unit', 'eval', 'check-env')]
    [string]$Task = 'launch'
)

$ErrorActionPreference = "Stop"
$ApexRoot = Split-Path -Parent $PSScriptRoot

function Invoke-Launch {
    Write-Host "Launching Apex Agent..." -ForegroundColor Cyan
    & "$ApexRoot\scripts\launch_hades.ps1"
}

function Invoke-Test {
    Write-Host "Running all tests..." -ForegroundColor Cyan
    Push-Location $ApexRoot
    try {
        python -m pytest tests/
    }
    finally {
        Pop-Location
    }
}

function Invoke-Smoke {
    Write-Host "Running smoke tests..." -ForegroundColor Cyan
    Push-Location $ApexRoot
    try {
        python -m pytest tests/smoke/
    }
    finally {
        Pop-Location
    }
}

function Invoke-Unit {
    Write-Host "Running unit tests..." -ForegroundColor Cyan
    Push-Location $ApexRoot
    try {
        python -m pytest tests/unit/
    }
    finally {
        Pop-Location
    }
}

function Invoke-Eval {
    Write-Host "Running evaluation tests..." -ForegroundColor Cyan
    Push-Location $ApexRoot
    try {
        python -m pytest tests/eval/
    }
    finally {
        Pop-Location
    }
}

function Invoke-Lint {
    Write-Host "Running linters..." -ForegroundColor Cyan
    Push-Location $ApexRoot
    try {
        python -m ruff check agent_app/ tests/
    }
    finally {
        Pop-Location
    }
}

function Invoke-Clean {
    Write-Host "Cleaning workspace..." -ForegroundColor Cyan
    & "$ApexRoot\scripts\clean.ps1"
}

function Invoke-CheckEnv {
    Write-Host "Checking environment..." -ForegroundColor Cyan
    & "$ApexRoot\scripts\check-env.ps1"
}

switch ($Task) {
    'launch' { Invoke-Launch }
    'test' { Invoke-Test }
    'smoke' { Invoke-Smoke }
    'unit' { Invoke-Unit }
    'eval' { Invoke-Eval }
    'lint' { Invoke-Lint }
    'clean' { Invoke-Clean }
    'check-env' { Invoke-CheckEnv }
}
