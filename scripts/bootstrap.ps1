#!/usr/bin/env pwsh
# Bootstrap script for Windows
# Sets up Python virtual environment and installs dependencies

Write-Host "=== Bootstrap Puls Events Culturs RAG ===" -ForegroundColor Cyan

# Check Python version
$pythonCmd = "python"
try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check minimum Python version (3.11)
$versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
if ($versionMatch) {
    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
        Write-Host "Error: Python 3.11+ required, found Python $major.$minor" -ForegroundColor Red
        exit 1
    }
}

# Create virtual environment
Write-Host "`nCreating virtual environment in .venv..." -ForegroundColor Cyan
if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists, skipping creation" -ForegroundColor Yellow
} else {
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Cyan
$venvPython = ".\.venv\Scripts\python.exe"
$venvPip = ".\.venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Error: Virtual environment activation failed" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Cyan
& $venvPip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Failed to upgrade pip" -ForegroundColor Yellow
}

# Install project in editable mode with dev dependencies
Write-Host "`nInstalling project dependencies..." -ForegroundColor Cyan
& $venvPip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Copy .env.example to .env if not exists
Write-Host "`nSetting up environment file..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host ".env already exists, skipping" -ForegroundColor Yellow
} else {
    Copy-Item ".env.example" ".env"
    Write-Host ".env created from .env.example" -ForegroundColor Green
    Write-Host "Please edit .env and add your API keys!" -ForegroundColor Yellow
}

# Create logs directory
Write-Host "`nCreating logs directory..." -ForegroundColor Cyan
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "logs/ directory created" -ForegroundColor Green
}

Write-Host "`n=== Bootstrap Complete ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env and add your API keys (OPENAGENDA_API_KEY, MISTRAL_API_KEY)" -ForegroundColor White
Write-Host "  2. Build the index: .\.venv\Scripts\python scripts\build_index.py" -ForegroundColor White
Write-Host "  3. Run the API: .\.venv\Scripts\uvicorn api.main:app --reload" -ForegroundColor White
Write-Host "  4. Or use VS Code tasks: Ctrl+Shift+P -> Tasks: Run Task" -ForegroundColor White
Write-Host ""
