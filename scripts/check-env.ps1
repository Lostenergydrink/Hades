# Pre-flight environment validator for Apex Agent
# Verifies essential tools and services are available

$ErrorActionPreference = "Stop"
$ApexRoot = Split-Path -Parent $PSScriptRoot

Write-Host "`n=== Apex Agent Environment Check ===" -ForegroundColor Cyan

$AllGreen = $true

# Check Python
Write-Host "`nChecking Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "  $pythonVersion" -ForegroundColor Gray
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        Write-Host "  Python not found or not in PATH" -ForegroundColor Red
        $AllGreen = $false
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "  Python not found or not in PATH" -ForegroundColor Red
    $AllGreen = $false
}

# Check Git
Write-Host "`nChecking Git..." -NoNewline
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "  $gitVersion" -ForegroundColor Gray
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        Write-Host "  Git not found or not in PATH" -ForegroundColor Red
        $AllGreen = $false
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "  Git not found or not in PATH" -ForegroundColor Red
    $AllGreen = $false
}

# Check Ruff
Write-Host "`nChecking Ruff..." -NoNewline
try {
    $ruffVersion = python -m ruff --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "  $ruffVersion" -ForegroundColor Gray
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        Write-Host "  Ruff not installed (pip install ruff)" -ForegroundColor Red
        $AllGreen = $false
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "  Ruff not installed (pip install ruff)" -ForegroundColor Red
    $AllGreen = $false
}

# Check Pytest
Write-Host "`nChecking Pytest..." -NoNewline
try {
    $pytestVersion = python -m pytest --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "  $pytestVersion" -ForegroundColor Gray
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        Write-Host "  Pytest not installed (pip install pytest)" -ForegroundColor Red
        $AllGreen = $false
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "  Pytest not installed (pip install pytest)" -ForegroundColor Red
    $AllGreen = $false
}

# Check Project Structure
Write-Host "`nChecking Project Structure..." -NoNewline
$requiredPaths = @(
    "agent_app",
    "config/hades_config.toml",
    "requirements.txt"
)
$structureOk = $true
foreach ($path in $requiredPaths) {
    $fullPath = Join-Path $ApexRoot $path
    if (-not (Test-Path $fullPath)) {
        if ($structureOk) {
            Write-Host " FAIL" -ForegroundColor Red
            $structureOk = $false
        }
        Write-Host "  Missing: $path" -ForegroundColor Red
        $AllGreen = $false
    }
}
if ($structureOk) {
    Write-Host " OK" -ForegroundColor Green
    Write-Host "  All required files present" -ForegroundColor Gray
}

# Check Virtual Environment (Warning only)
Write-Host "`nChecking Virtual Environment..." -NoNewline
if ($env:VIRTUAL_ENV) {
    Write-Host " OK" -ForegroundColor Green
    Write-Host "  Active venv: $env:VIRTUAL_ENV" -ForegroundColor Gray
} else {
    Write-Host " WARN" -ForegroundColor Yellow
    Write-Host "  No virtual environment active (recommended but not required)" -ForegroundColor Yellow
}

# Final Status
Write-Host "`n==================================" -ForegroundColor Cyan
if ($AllGreen) {
    Write-Host "All checks passed! Environment ready." -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some checks failed. Please fix issues above." -ForegroundColor Red
    exit 1
}
