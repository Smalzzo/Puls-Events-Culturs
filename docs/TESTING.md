# Guide des Tests - Puls Events Culturs RAG

Ce document explique comment exécuter et utiliser les différents types de tests du projet.

## 📋 Table des matières

- [Types de tests](#types-de-tests)
- [Installation](#installation)
- [Exécution des tests](#exécution-des-tests)
- [Tests de performance](#tests-de-performance)
- [Évaluation automatisée](#évaluation-automatisée)
- [Couverture de code](#couverture-de-code)
- [CI/CD](#cicd)

## 🧪 Types de tests

### Tests unitaires (`test_*.py`)

Tests rapides qui valident les composants individuels :

- **`test_config.py`** : Configuration et paramètres
- **`test_indexer.py`** : Tests de base de l'indexeur
- **`test_indexer_advanced.py`** : Tests avancés d'indexation (qualité, robustesse)
- **`test_api.py`** : Tests des endpoints API

### Tests de performance (`test_performance.py`)

Tests qui mesurent les performances du système :

- Temps de réponse des requêtes
- Charge et accès concurrent
- Scalabilité avec grands volumes
- Utilisation des ressources

### Tests d'évaluation (`test_ragas_automation.py`)

Tests pour l'automatisation des métriques RAGAS :

- Configuration de l'évaluateur
- Création de datasets d'évaluation
- Validation des métriques
- Détection de régressions

## 🔧 Installation

Installer les dépendances de test :

```bash
# Windows PowerShell
.\.venv\Scripts\python.exe -m pip install pytest pytest-cov pytest-mock pytest-asyncio

# Linux/Mac
.venv/bin/python -m pip install pytest pytest-cov pytest-mock pytest-asyncio
```

## ▶️ Exécution des tests

### Tous les tests

```bash
# Windows
.\.venv\Scripts\pytest.exe

# Linux/Mac
.venv/bin/pytest
```

### Tests par marqueur

```bash
# Tests unitaires uniquement (rapides)
.\.venv\Scripts\pytest.exe -m unit

# Tests d'intégration
.\.venv\Scripts\pytest.exe -m integration

# Tests de performance
.\.venv\Scripts\pytest.exe -m performance

# Tests d'évaluation RAGAS (lents)
.\.venv\Scripts\pytest.exe -m evaluation
```

### Tests par fichier

```bash
# Tests d'indexation avancés
.\.venv\Scripts\pytest.exe tests/test_indexer_advanced.py

# Tests de performance
.\.venv\Scripts\pytest.exe tests/test_performance.py

# Tests d'évaluation
.\.venv\Scripts\pytest.exe tests/test_ragas_automation.py
```

### Tests par classe ou fonction

```bash
# Une classe spécifique
.\.venv\Scripts\pytest.exe tests/test_indexer_advanced.py::TestIndexDataQuality

# Une fonction spécifique
.\.venv\Scripts\pytest.exe tests/test_performance.py::TestRAGPerformance::test_query_response_time_single
```

### Options utiles

```bash
# Mode verbeux avec sortie détaillée
.\.venv\Scripts\pytest.exe -v

# Arrêter à la première erreur
.\.venv\Scripts\pytest.exe -x

# Afficher les print statements
.\.venv\Scripts\pytest.exe -s

# Exécuter les N tests les plus lents
.\.venv\Scripts\pytest.exe --durations=10

# Exécuter en parallèle (nécessite pytest-xdist)
.\.venv\Scripts\pytest.exe -n auto
```

## 📊 Tests de performance

Les tests de performance mesurent :

1. **Temps de réponse** : Latence des requêtes individuelles
2. **Débit** : Nombre de requêtes par seconde
3. **Charge concurrente** : Comportement sous charge parallèle
4. **Scalabilité** : Performance avec grands volumes de données

### Exécution

```bash
# Tous les tests de performance
.\.venv\Scripts\pytest.exe tests/test_performance.py -v

# Avec rapport de temps d'exécution
.\.venv\Scripts\pytest.exe tests/test_performance.py --durations=0
```

### Métriques collectées

- Temps de réponse moyen, médian, P95, P99
- Throughput (requêtes/seconde)
- Temps de construction d'index
- Utilisation mémoire

## 🤖 Évaluation automatisée

### Script d'évaluation automatique

Le script `scripts/run_automated_evaluation.py` permet d'automatiser les évaluations RAGAS :

```bash
# Évaluation avec le fichier mini (rapide)
.\.venv\Scripts\python.exe scripts/run_automated_evaluation.py

# Évaluation avec le fichier complet
.\.venv\Scripts\python.exe scripts/run_automated_evaluation.py --test-file data/test/ragas_questions.json

# Avec Mistral embeddings
.\.venv\Scripts\python.exe scripts/run_automated_evaluation.py --use-mistral-embeddings

# Générer un rapport de tendance
.\.venv\Scripts\python.exe scripts/run_automated_evaluation.py --trend-report

# Exporter l'historique en CSV
.\.venv\Scripts\python.exe scripts/run_automated_evaluation.py --export-csv
```

### Fonctionnalités

- ✅ Exécution automatique des évaluations RAGAS
- ✅ Historique des évaluations avec timestamps
- ✅ Détection d'alertes (scores sous seuils)
- ✅ Détection de régressions (baisse de performance)
- ✅ Génération de rapports JSON
- ✅ Export CSV pour analyse
- ✅ Rapports de tendance

### Seuils de qualité

Les seuils par défaut sont :

```python
{
    "faithfulness": 0.70,          # Fidélité aux sources
    "answer_relevancy": 0.70,      # Pertinence de la réponse
    "context_precision": 0.65,     # Précision du contexte
    "context_recall": 0.65         # Rappel du contexte
}
```

### Interprétation des résultats

- **Success** : Tous les scores au-dessus des seuils, aucune régression
- **Warning** : Alertes ou régressions de sévérité moyenne
- **Critical** : Alertes ou régressions de haute sévérité

### Rapports générés

Les rapports sont sauvegardés dans `data/evaluations/` :

- `evaluation_YYYYMMDD_HHMMSS.json` : Rapport d'évaluation individuel
- `evaluation_history.json` : Historique complet
- `trend_report.json` : Rapport de tendance
- `metrics_history.csv` : Export CSV pour Excel/Google Sheets

## 📈 Couverture de code

### Exécuter avec couverture

```bash
# Générer la couverture
.\.venv\Scripts\pytest.exe --cov=src --cov-report=html --cov-report=term

# Voir le rapport HTML
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux
```

### Rapport de couverture

Le rapport HTML détaille :

- Pourcentage de code couvert par fichier
- Lignes non couvertes (en rouge)
- Branches non testées
- Statistiques globales

### Objectifs de couverture

- **Minimum acceptable** : 70%
- **Objectif** : 80%
- **Excellent** : 90%+

## 🔄 CI/CD

### Tests pour intégration continue

```bash
# Tests rapides pour CI (exclure les tests lents)
.\.venv\Scripts\pytest.exe -m "not slow" --tb=short

# Tests avec code de sortie
.\.venv\Scripts\pytest.exe -x --tb=short || exit 1

# Générer un rapport XML pour CI
.\.venv\Scripts\pytest.exe --junitxml=test-results.xml
```

### Configuration GitHub Actions (exemple)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest -m "not slow" --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 🛠️ Commandes utiles

### Lancer les tests depuis VS Code

Utiliser les tâches configurées :

```bash
# Tâche "Test: Run All Tests"
Ctrl+Shift+P > Tasks: Run Task > Test: Run All Tests
```

### Debugging de tests

```python
# Ajouter un breakpoint dans pytest
import pytest
pytest.set_trace()

# Ou utiliser le debugger VS Code
# Mettre un breakpoint et lancer en mode debug
```

### Générer un nouveau fichier de test

```bash
# Créer à partir du template
cp tests/test_template.py tests/test_new_feature.py
```

## 📝 Bonnes pratiques

1. **Écrire des tests avant le code** (TDD quand possible)
2. **Nommer les tests de manière descriptive** : `test_should_do_something_when_condition`
3. **Un test = une assertion** (dans l'idéal)
4. **Utiliser les fixtures** pour réduire la duplication
5. **Marquer les tests lents** avec `@pytest.mark.slow`
6. **Mocker les appels externes** (API, base de données)
7. **Tester les cas limites** (valeurs nulles, vides, extrêmes)
8. **Documenter les tests complexes** avec des docstrings

## 🐛 Résolution de problèmes

### Les tests ne s'exécutent pas

```bash
# Vérifier l'installation de pytest
.\.venv\Scripts\python.exe -m pytest --version

# Réinstaller si nécessaire
.\.venv\Scripts\python.exe -m pip install --upgrade pytest
```

### Erreurs d'import

```bash
# Vérifier le PYTHONPATH
.\.venv\Scripts\python.exe -c "import sys; print('\n'.join(sys.path))"

# Installer le projet en mode éditable
.\.venv\Scripts\python.exe -m pip install -e .
```

### Tests lents

```bash
# Identifier les tests lents
.\.venv\Scripts\pytest.exe --durations=20

# Exclure les tests lents
.\.venv\Scripts\pytest.exe -m "not slow"
```

## 📚 Ressources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Coverage](https://pytest-cov.readthedocs.io/)
- [RAGAS Documentation](https://docs.ragas.io/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

## 🤝 Contribution

Pour ajouter de nouveaux tests :

1. Créer un fichier `test_*.py` dans `tests/`
2. Utiliser les fixtures de `conftest.py`
3. Ajouter les marqueurs appropriés
4. Documenter le test avec une docstring
5. Exécuter les tests pour vérifier

---

**Note** : Ce guide est maintenu et mis à jour régulièrement. Pour toute question, consulter l'équipe de développement.
