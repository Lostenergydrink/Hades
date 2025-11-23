# Clean Workspace Script
# Removes temporary files, caches, and build artifacts from the Apex Agent workspace

param(
    [switch]$DryRun
)

$ApexRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Cleaning Apex Agent workspace..." -ForegroundColor Cyan

# Directories to remove
$DirsToRemove = @(
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".coverage",
    "htmlcov",
    "dist",
    "build",
    "*.egg-info"
)

# File patterns to remove
$FilesToRemove = @(
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".coverage",
    ".DS_Store"
)

# Checkpoint cleanup
$CheckpointDir = Join-Path $ApexRoot ".apex\checkpoints"

# Test artifact cleanup
$TestArtifactsPattern = "tests\eval\*.tmp"

function Remove-Paths {
    param([string]$Pattern, [string]$Type)
    
    $items = Get-ChildItem -Path $ApexRoot -Recurse -Force -Filter $Pattern -ErrorAction SilentlyContinue
    
    foreach ($item in $items) {
        if ($DryRun) {
            Write-Host "[DRY RUN] Would remove ${Type}: $($item.FullName)" -ForegroundColor Yellow
        }
        else {
            try {
                Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction Stop
                Write-Host "Removed ${Type}: $($item.FullName)" -ForegroundColor Green
            }
            catch {
                Write-Host "Failed to remove ${Type}: $($item.FullName) - $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
}

# Remove directories
foreach ($dir in $DirsToRemove) {
    Remove-Paths -Pattern $dir -Type "directory"
}

# Remove files
foreach ($file in $FilesToRemove) {
    Remove-Paths -Pattern $file -Type "file"
}

# Clean checkpoints
if (Test-Path $CheckpointDir) {
    if ($DryRun) {
        Write-Host "[DRY RUN] Would clean checkpoints: $CheckpointDir" -ForegroundColor Yellow
    }
    else {
        try {
            Remove-Item -Path "$CheckpointDir\*" -Recurse -Force -ErrorAction Stop
            Write-Host "Cleaned checkpoints: $CheckpointDir" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to clean checkpoints: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Clean test artifacts
$testArtifacts = Get-ChildItem -Path (Join-Path $ApexRoot "tests\eval") -Filter "*.tmp" -ErrorAction SilentlyContinue
foreach ($artifact in $testArtifacts) {
    if ($DryRun) {
        Write-Host "[DRY RUN] Would remove test artifact: $($artifact.FullName)" -ForegroundColor Yellow
    }
    else {
        try {
            Remove-Item -Path $artifact.FullName -Force -ErrorAction Stop
            Write-Host "Removed test artifact: $($artifact.FullName)" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to remove test artifact: $($artifact.FullName) - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

if ($DryRun) {
    Write-Host "`n[DRY RUN] No files were actually removed. Run without -DryRun to clean." -ForegroundColor Yellow
}
else {
    Write-Host "`nWorkspace cleaned successfully!" -ForegroundColor Green
}
