# Puls Events Culturs - RAG POC

POC de recherche sémantique sur événements culturels utilisant RAG (Retrieval-Augmented Generation) avec LangChain, Mistral AI, et FAISS.

## Table des Matières

- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du Projet](#structure-du-projet)
- [Développement](#développement)
- [Docker](#docker)
- [Tests](#tests)
- [API Documentation](#api-documentation)

## ️ Architecture

### Stack Technique

- **Python**: 3.11+
- **Framework API**: FastAPI + Uvicorn
- **LLM**: Mistral AI (via API)
- **Embeddings**: Sentence Transformers (local)
- **Vector Store**: FAISS (local)
- **RAG Framework**: LangChain
- **Data Source**: OpenAgenda API
- **Configuration**: Pydantic Settings
- **Testing**: Pytest
- **Linting**: Ruff
- **Containerization**: Docker + Docker Compose

### Workflow

```
OpenAgenda API → Fetcher → Text Processing → Embeddings → FAISS Index
                                                              ↓
User Query → FastAPI → RAG System → Retriever → LLM → Response
```

## Prérequis

### Logiciels Requis

- **Python 3.11+** ([Télécharger](https://www.python.org/downloads/))
- **Git** ([Télécharger](https://git-scm.com/downloads))
- **VS Code** (recommandé) avec extensions:
  - Python
  - Pylance
  - Ruff

### Clés API Nécessaires

1. **OpenAgenda API Key**: [Obtenir une clé](https://openagenda.com/developers)
2. **Mistral AI API Key**: [Obtenir une clé](https://console.mistral.ai/)

## Installation

### Option 1: Script Bootstrap (Recommandé)

#### Windows (PowerShell)
```powershell
# Depuis le dossier du projet
.\scripts\bootstrap.ps1
```

#### Linux/Mac (Bash)
```bash
# Depuis le dossier du projet
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

Le script bootstrap va:
- Vérifier Python 3.11+
- Créer l'environnement virtuel `.venv`
- Installer toutes les dépendances
- Copier `.env.example` vers `.env`
- Créer le dossier `logs/`

### Option 2: Installation Manuelle

#### Windows
```powershell
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer le projet
pip install -e ".[dev]"

# Copier le template d'environnement
copy .env.example .env
```

#### Linux/Mac
```bash
# Créer l'environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip

# Installer le projet
pip install -e ".[dev]"

# Copier le template d'environnement
cp .env.example .env
```

## ️ Configuration

### Éditer le fichier `.env`

Ouvrez `.env` et remplissez les valeurs requises:

```bash
# OpenAgenda Configuration
OPENAGENDA_API_KEY=votre_clé_api_openagenda
OPENAGENDA_AGENDA_UID=uid_de_votre_agenda
OPENAGENDA_LOCATION=Paris

# Mistral AI Configuration
MISTRAL_API_KEY=votre_clé_api_mistral
MISTRAL_MODEL_NAME=mistral-medium-latest
```

### Configuration Avancée

Voir [.env.example](.env.example) pour toutes les options disponibles:
- Configuration RAG (top_k, chunk_size, etc.)
- Configuration FAISS (index_type, etc.)
- Configuration API (host, port, etc.)
- Configuration Logging (level, format, etc.)

## Utilisation

### 1. Construire l'Index FAISS

**Important**: Cette étape doit être effectuée avant de lancer l'API.

#### Avec Make
```bash
make build-index
```

#### Avec Python
```bash
# Windows
.\.venv\Scripts\python scripts\build_index.py

# Linux/Mac
python scripts/build_index.py
```

#### Avec VS Code
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Build: Index from OpenAgenda"

**Sortie**: L'index sera créé dans `data/index/faiss_index/`

### 2. Démarrer l'API

#### Avec Make
```bash
make run          # Mode production
make run-debug    # Mode développement (auto-reload)
```

#### Avec Python
```bash
# Windows
.\.venv\Scripts\uvicorn api.main:app --reload

# Linux/Mac
uvicorn api.main:app --reload
```

#### Avec VS Code
- `F5` → "FastAPI: Run API Server"
- Ou: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run: API Server"

**API disponible à**: http://localhost:8000

### 3. Tester l'API

#### Via l'Interface Swagger
Ouvrez votre navigateur: http://localhost:8000/docs

#### Via curl

**Query RAG (avec génération LLM)**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Quels sont les concerts de jazz à Paris ce mois-ci?\"}"
```

**Similarity Search (sans LLM)**:
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"concert jazz\", \"k\": 5}"
```

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Stats**:
```bash
curl http://localhost:8000/stats
```

## Structure du Projet

```
Puls-Events-Culturs/
|-- .github/                    # Workflows CI
|-- .vscode/                    # Configuration VS Code
|   |-- settings.json           # Parametres Python, Ruff, Pytest
|   |-- launch.json             # Configurations de debug
|   `-- tasks.json              # Taches (bootstrap, lint, test, run)
|
|-- api/                        # Application FastAPI
|   |-- __init__.py
|   `-- main.py                 # Endpoints API
|
|-- src/                        # Code source principal
|   |-- __init__.py
|   |-- config.py               # Configuration (Pydantic Settings)
|   |-- logger.py               # Configuration logging
|   |-- indexer.py              # Fetcher OpenAgenda + FAISS builder
|   `-- rag.py                  # Systeme RAG (LangChain + Mistral)
|
|-- scripts/                    # Scripts utilitaires
|   |-- bootstrap.ps1           # Bootstrap Windows
|   |-- bootstrap.sh            # Bootstrap Linux/Mac
|   |-- build_index.py          # Script de build d'index
|   |-- run_tests.ps1           # Lancer les tests (Windows)
|   `-- run_automated_evaluation.py
|
|-- tests/                      # Tests unitaires et fonctionnels
|   |-- __init__.py
|   |-- conftest.py             # Fixtures pytest
|   |-- test_api.py             # Tests API
|   |-- test_config.py          # Tests configuration
|   |-- test_functional_api.py  # Tests fonctionnels API
|   `-- test_indexer.py         # Tests indexer
|
|-- data/                       # Donnees et index
|   |-- raw/                    # Donnees brutes (events.json)
|   |-- processed/              # Donnees traitees
|   |-- index/                  # Index FAISS
|   `-- test/                   # Donnees de test
|
|-- docs/                       # Documentation
|-- notebooks/                  # Jupyter notebooks (exploration)
|-- logs/                       # Fichiers de logs
|
|-- .env                        # Variables locales (non versionne)
|-- .env.example                # Template de configuration
|-- .gitattributes              # Git LFS (index FAISS)
|-- .gitignore                  # Fichiers a ignorer
|-- pyproject.toml              # Configuration projet + dependances
|-- pytest.ini                  # Configuration pytest
|-- requirements.txt            # Dependances figees
|-- Makefile                    # Commandes make
|-- Dockerfile                  # Image Docker
|-- docker-compose.yml          # Orchestration Docker
`-- README.md                   # Ce fichier
```

### Rôle des Dossiers

| Dossier | Description |
|---------|-------------|
| `api/` | API FastAPI avec endpoints RAG |
| `src/` | Logique métier (config, logging, indexing, RAG) |
| `scripts/` | Scripts d'automatisation (bootstrap, build index) |
| `tests/` | Tests unitaires et fonctionnels avec pytest |
| `data/` | Données (raw), données traitées (processed), index FAISS (index) |
| `docs/` | Documentation supplémentaire |
| `notebooks/` | Notebooks Jupyter pour exploration/prototypage |
| `logs/` | Fichiers de logs de l'application |

## ️ Développement

### Commandes Make Disponibles

```bash
make help           # Afficher l'aide
make install        # Installer dépendances production
make install-dev    # Installer toutes les dépendances
make lint           # Lancer Ruff (vérification)
make format         # Formater le code avec Ruff
make test           # Lancer les tests
make test-cov       # Tests avec couverture
make build-index    # Construire l'index FAISS
make run            # Démarrer l'API
make run-debug      # Démarrer l'API (debug mode)
make clean          # Nettoyer les fichiers temporaires
```

### Workflow de Développement

1. **Créer une branche**:
   ```bash
   git checkout -b feature/ma-feature
   ```

2. **Faire vos modifications**

3. **Linter et formater**:
   ```bash
   make format
   make lint
   ```

4. **Tester**:
   ```bash
   make test
   ```

5. **Commiter et pusher**:
   ```bash
   git add .
   git commit -m "feat: description"
   git push origin feature/ma-feature
   ```



## Docker

### Build l'Image

```bash
make docker-build
# Ou
docker build -t puls-events-rag:latest .
```

### Lancer avec Docker Compose

```bash
make docker-run
# Ou
docker-compose up -d
```

### Configuration Docker

Le conteneur:
- Expose le port **8000**
- Monte `.env` en lecture seule
- Persiste `data/index/` pour l'index FAISS
- Persiste `logs/` pour les logs
- Inclut un health check

### Arrêter Docker

```bash
make docker-stop
# Ou
docker-compose down
```

## Tests

### Suite de Tests (15 tests)

Le projet inclut une suite complète de tests unitaires :
- **test_api.py** : 6 tests pour les endpoints FastAPI
- **test_config.py** : 5 tests pour la configuration
- **test_indexer.py** : 4 tests pour l'indexation et le chunking

### Lancer Tous les Tests

```bash
# Avec Make
make test

# Avec pytest directement
pytest tests/ -v

# Avec le script PowerShell (Windows)
.\scripts\run_tests.ps1 quick
```

### Tests avec Couverture

```bash
make test-cov

# Le rapport HTML sera disponible dans htmlcov/index.html
```

### Lancer un Fichier de Test Spécifique

```bash
# Windows
.\.venv\Scripts\pytest.exe tests/test_api.py -v
.\.venv\Scripts\pytest.exe tests/test_config.py -v
.\.venv\Scripts\pytest.exe tests/test_indexer.py -v

# Linux/Mac
pytest tests/test_api.py -v
pytest tests/test_config.py -v
pytest tests/test_indexer.py -v
```

### Lancer un Test Spécifique

```bash
# Test d'un endpoint spécifique
pytest tests/test_api.py::test_health_endpoint -v

# Test d'une classe spécifique
pytest tests/test_api.py::TestAPIEndpoints -v
```

### Markers de Tests

```bash
# Tests unitaires uniquement
pytest -m unit

# Tests d'intégration uniquement
pytest -m integration

# Exclure les tests lents
pytest -m "not slow"
```

### Documentation des Tests

Pour plus de détails sur les tests :
- Consultez [docs/TESTING.md](docs/TESTING.md) pour le guide complet
- Les fixtures communes sont dans [tests/conftest.py](tests/conftest.py)
- Configuration pytest : [pytest.ini](pytest.ini)

## API Documentation

### Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Health check de l'API et de l'index |
| `/docs` | GET | Documentation Swagger UI interactive |
| `/redoc` | GET | Documentation ReDoc alternative |
| `/ask` | POST | Pose une question sur les événements (RAG complet) |
| `/rebuild` | POST | Ajoute de nouveaux événements à l'index existant |
| `/evaluate` | POST | Évalue le système RAG avec RAGAS |

### Exemples de Requêtes

#### GET /health

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "index_loaded": true
}
```

#### POST /ask

Pose une question et obtient une réponse générée par le LLM avec sources.

**Request**:
```json
{
  "question": "Quels sont les événements de théâtre à Paris?"
}
```

**Response**:
```json
{
  "question": "Quels sont les événements de théâtre à Paris?",
  "answer": "Voici les événements de théâtre à Paris...",
  "sources": [
    {
      "content": "Événement: Hamlet\nLieu: Théâtre de la Ville, Paris...",
      "metadata": {
        "event_id": "12345",
        "title": "Hamlet",
        "location_city": "Paris"
      }
    }
  ]
}
```

#### POST /rebuild

Ajoute de nouveaux événements à l'index FAISS existant.

**Request**:
```json
{
  "events": [
    {
      "title_fr": "Concert de Jazz",
      "description_fr": "Grande soirée jazz avec des artistes internationaux",
      "location_name": "Salle Pleyel",
      "location_city": "Paris",
      "location_region": "Île-de-France",
      "firstdate_begin": "2026-03-15T20:00:00",
      "uid": "event_12345"
    }
  ]
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Index mis à jour avec succès",
  "events_processed": 1,
  "chunks_created": 3
}
```

#### POST /evaluate

Évalue le système RAG avec des métriques RAGAS.

**Request**:
```json
{
  "test_file_path": "data/test/ragas_questions_mini.json"
}
```

**Response**:
```json
{
  "status": "success",
  "metrics": {
    "faithfulness": 0.85,
    "answer_relevancy": 0.90,
    "context_precision": 0.80,
    "context_recall": 0.75
  },
  "message": "Évaluation terminée avec succès"
}
```

#### POST /search

**Request**:
```json
{
  "query": "concert musique classique",
  "k": 3
}
```

**Response**:
```json
{
  "query": "concert musique classique",
  "results": [
    {
      "content": "Titre: Concert de l'Orchestre de Paris...",
      "metadata": {...}
    }
  ],
  "count": 3
}
```

## Troubleshooting

### L'index FAISS n'est pas trouvé

**Erreur**: `FAISS index not found`

**Solution**:
```bash
make build-index
```

### Erreur de clé API

**Erreur**: `Invalid API key`

**Solution**: Vérifiez que vos clés dans `.env` sont correctes:
- `OPENAGENDA_API_KEY`
- `MISTRAL_API_KEY`

### Module introuvable

**Erreur**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Assurez-vous que le projet est installé en mode éditable:
```bash
pip install -e .
```

### Python version incorrecte

**Erreur**: Version de Python < 3.11

**Solution**: Installez Python 3.11+ et recréez le venv:
```bash
python3.11 -m venv .venv
```




