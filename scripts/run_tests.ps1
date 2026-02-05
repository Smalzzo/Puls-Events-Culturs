#!/usr/bin/env pwsh
# Script PowerShell pour faciliter l'exécution des tests
# Usage: .\scripts\run_tests.ps1 [options]

param(
    [Parameter(Position=0)]
    [ValidateSet("all", "unit", "integration", "performance", "evaluation", "coverage", "quick")]
    [string]$TestType = "quick",
    
    [Parameter()]
    [string]$TestFile,
    
    [Parameter()]
    [switch]$Verbose,
    
    [Parameter()]
    [switch]$StopOnFailure,
    
    [Parameter()]
    [switch]$ShowDurations,
    
    [Parameter()]
    [switch]$Parallel,
    
    [Parameter()]
    [switch]$Html
)

# Couleurs pour l'affichage
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# En-tête
Write-ColorOutput "`n========================================" "Cyan"
Write-ColorOutput "  Tests - Puls Events Culturs RAG" "Cyan"
Write-ColorOutput "========================================`n" "Cyan"

# Vérifier que le venv existe
$venvPath = Join-Path $PSScriptRoot ".." ".venv"
$pythonExe = Join-Path $venvPath "Scripts" "python.exe"
$pytestExe = Join-Path $venvPath "Scripts" "pytest.exe"

if (-not (Test-Path $pythonExe)) {
    Write-ColorOutput "❌ Erreur: Environnement virtuel non trouvé" "Red"
    Write-ColorOutput "Veuillez exécuter: .\scripts\bootstrap.ps1" "Yellow"
    exit 1
}

if (-not (Test-Path $pytestExe)) {
    Write-ColorOutput "⚠️  Pytest non installé, installation..." "Yellow"
    & $pythonExe -m pip install pytest pytest-cov pytest-mock
}

# Construire la commande pytest
$pytestArgs = @()

# Options communes
if ($Verbose) {
    $pytestArgs += "-v"
}

if ($StopOnFailure) {
    $pytestArgs += "-x"
}

if ($ShowDurations) {
    $pytestArgs += "--durations=10"
}

if ($Parallel) {
    # Vérifier si pytest-xdist est installé
    $xdistInstalled = & $pythonExe -c "try: import pytest_xdist; print('yes')\nexcept: print('no')" 2>$null
    if ($xdistInstalled -eq "yes") {
        $pytestArgs += "-n", "auto"
    } else {
        Write-ColorOutput "⚠️  pytest-xdist non installé, exécution séquentielle" "Yellow"
    }
}

# Type de test
switch ($TestType) {
    "all" {
        Write-ColorOutput "🧪 Exécution de TOUS les tests..." "Green"
        # Aucun marqueur spécifique
    }
    "unit" {
        Write-ColorOutput "🧪 Exécution des tests unitaires..." "Green"
        $pytestArgs += "-m", "unit"
    }
    "integration" {
        Write-ColorOutput "🧪 Exécution des tests d'intégration..." "Green"
        $pytestArgs += "-m", "integration"
    }
    "performance" {
        Write-ColorOutput "📊 Exécution des tests de performance..." "Green"
        $pytestArgs += "-m", "performance"
        $pytestArgs += "tests/test_performance.py"
    }
    "evaluation" {
        Write-ColorOutput "🤖 Exécution des tests d'évaluation RAGAS..." "Green"
        $pytestArgs += "-m", "evaluation"
        $pytestArgs += "tests/test_ragas_automation.py"
    }
    "coverage" {
        Write-ColorOutput "📈 Exécution avec couverture de code..." "Green"
        $pytestArgs += "--cov=src"
        $pytestArgs += "--cov-report=term"
        $pytestArgs += "--cov-report=html"
        if ($Html) {
            $pytestArgs += "--cov-report=html:htmlcov"
        }
    }
    "quick" {
        Write-ColorOutput "⚡ Exécution des tests rapides (sans les lents)..." "Green"
        $pytestArgs += "-m", "not slow"
    }
}

# Fichier de test spécifique
if ($TestFile) {
    Write-ColorOutput "📄 Test du fichier: $TestFile" "Cyan"
    $pytestArgs += $TestFile
}

# Afficher la commande
Write-ColorOutput "`nCommande: pytest $($pytestArgs -join ' ')`n" "DarkGray"

# Exécuter les tests
$startTime = Get-Date
& $pytestExe @pytestArgs
$exitCode = $LASTEXITCODE
$duration = (Get-Date) - $startTime

# Résumé
Write-ColorOutput "`n========================================" "Cyan"
if ($exitCode -eq 0) {
    Write-ColorOutput "✅ SUCCÈS - Tous les tests ont réussi!" "Green"
} else {
    Write-ColorOutput "❌ ÉCHEC - Certains tests ont échoué" "Red"
}
Write-ColorOutput "Durée: $([math]::Round($duration.TotalSeconds, 2))s" "Cyan"
Write-ColorOutput "========================================`n" "Cyan"

# Ouvrir le rapport HTML si demandé et généré
if ($Html -and $exitCode -eq 0 -and $TestType -eq "coverage") {
    $htmlReport = Join-Path $PSScriptRoot ".." "htmlcov" "index.html"
    if (Test-Path $htmlReport) {
        Write-ColorOutput "📊 Ouverture du rapport de couverture..." "Cyan"
        Start-Process $htmlReport
    }
}

# Options supplémentaires affichées
if ($exitCode -eq 0) {
    Write-ColorOutput "💡 Options disponibles:" "Yellow"
    Write-ColorOutput "  - Tests rapides:      .\scripts\run_tests.ps1 quick" "Gray"
    Write-ColorOutput "  - Tests unitaires:    .\scripts\run_tests.ps1 unit" "Gray"
    Write-ColorOutput "  - Tests performance:  .\scripts\run_tests.ps1 performance" "Gray"
    Write-ColorOutput "  - Avec couverture:    .\scripts\run_tests.ps1 coverage -Html" "Gray"
    Write-ColorOutput "  - Fichier spécifique: .\scripts\run_tests.ps1 -TestFile tests/test_api.py" "Gray"
    Write-ColorOutput ""
}

exit $exitCode
