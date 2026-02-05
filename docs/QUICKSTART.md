# Guide de Démarrage Rapide

## 🎯 En 5 Minutes

### Étape 1: Clone et Bootstrap (2 min)

```bash
# Cloner le projet (si ce n'est pas déjà fait)
cd c:\Dev\Deploiment_ML\Puls-Events-Culturs

# Lancer le bootstrap
.\scripts\bootstrap.ps1  # Windows
# OU
./scripts/bootstrap.sh   # Linux/Mac
```

### Étape 2: Configuration (1 min)

Ouvrir `.env` et remplir les clés API:

```bash
OPENAGENDA_API_KEY=votre_clé_ici
OPENAGENDA_AGENDA_UID=votre_agenda_uid
MISTRAL_API_KEY=votre_clé_mistral
```

### Étape 3: Build Index (2 min)

```bash
# Activer le venv
.\.venv\Scripts\Activate.ps1  # Windows
# OU
source .venv/bin/activate     # Linux/Mac

# Construire l'index
python scripts/build_index.py
```

### Étape 4: Lancer l'API (10 sec)

```bash
uvicorn api.main:app --reload
```

### Étape 5: Tester (30 sec)

Ouvrez http://localhost:8000/docs et testez l'endpoint `/query`.

---

## 🔍 Commandes Essentielles

### Windows (PowerShell)

```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Construire l'index
python scripts\build_index.py

# Lancer l'API
uvicorn api.main:app --reload

# Lancer les tests
pytest tests -v

# Linter
ruff check .

# Formater
ruff format .
```

### Linux/Mac (Bash)

```bash
# Activer l'environnement
source .venv/bin/activate

# Construire l'index
python scripts/build_index.py

# Lancer l'API
uvicorn api.main:app --reload

# Lancer les tests
pytest tests -v

# Linter
ruff check .

# Formater
ruff format .
```

### Avec Make (Cross-platform)

```bash
make build-index    # Construire l'index
make run           # Lancer l'API
make test          # Lancer les tests
make lint          # Vérifier le code
make format        # Formater le code
```

---

## 📋 Checklist Avant Démo

- [ ] `.env` configuré avec les clés API
- [ ] Environnement virtuel activé
- [ ] Dépendances installées (`pip install -e ".[dev]"`)
- [ ] Index FAISS construit (`make build-index`)
- [ ] Tests passent (`make test`)
- [ ] API démarre sans erreur (`make run`)
- [ ] Health check OK (`curl http://localhost:8000/health`)
- [ ] Swagger UI accessible (http://localhost:8000/docs)

---

## 🐛 Problèmes Courants

### Problème: "Python not found"

**Solution Windows**:
```powershell
# Ajouter Python au PATH ou utiliser:
py -3.11 -m venv .venv
```

**Solution Linux/Mac**:
```bash
# Installer Python 3.11
sudo apt install python3.11 python3.11-venv  # Ubuntu/Debian
brew install python@3.11                      # macOS
```

### Problème: "Module not found"

**Solution**:
```bash
# Réinstaller en mode éditable
pip install -e .
```

### Problème: "FAISS index not found"

**Solution**:
```bash
# Reconstruire l'index
python scripts/build_index.py
```

### Problème: "API key invalid"

**Solution**: Vérifier `.env`:
- Les clés ne doivent pas avoir de guillemets
- Pas d'espaces autour du `=`
- Exemple: `MISTRAL_API_KEY=sk-abc123`

---

## 🎓 Ressources

- **Documentation API**: http://localhost:8000/docs
- **Logs**: `logs/app.log`
- **Index FAISS**: `data/index/faiss_index/`
- **Données brutes**: `data/raw/events.json`

---

## 💡 Tips VS Code

### Raccourcis Utiles

- `F5`: Démarrer le debugger
- `Ctrl+Shift+P` → "Tasks": Lancer une tâche
- `Ctrl+Shift+``: Ouvrir un nouveau terminal
- `Ctrl+B`: Toggle sidebar

### Extensions Recommandées

- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Ruff** (Charliermarsh)
- **Docker** (Microsoft) - optionnel
- **GitLens** - optionnel

### Snippets Utiles

Créer un test rapidement:

```python
import pytest

def test_my_function():
    """Test description."""
    # Arrange
    expected = "result"
    
    # Act
    result = my_function()
    
    # Assert
    assert result == expected
```

---

## 📊 Architecture Simplifiée

```
┌─────────────┐
│ OpenAgenda  │
│     API     │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│   Indexer   │─────▶│ FAISS Index  │
│  (scripts)  │      │   (data/)    │
└─────────────┘      └──────┬───────┘
                            │
                            │ Load
                            ▼
┌─────────────┐      ┌──────────────┐
│    User     │─────▶│  FastAPI     │
│   Query     │      │   (api/)     │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  RAG System  │
                     │   (src/)     │
                     └──────┬───────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       ┌──────────────┐           ┌──────────────┐
       │   Retriever  │           │  Mistral AI  │
       │   (FAISS)    │           │     LLM      │
       └──────────────┘           └──────────────┘
```

---

Bon développement! 🚀
