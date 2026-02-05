# 🚀 GUIDE BOOTSTRAP COMPLET
# Puls Events Culturs - POC RAG

## ✅ ÉTAPE 1: VÉRIFICATION DES PRÉREQUIS

### Windows (PowerShell)
```powershell
# Vérifier Python (version 3.11+)
python --version



## ✅ ÉTAPE 2: BOOTSTRAP DU PROJET

### Option A: Script Bootstrap Automatique (RECOMMANDÉ)

#### Windows (PowerShell)
```powershell
# Se placer dans le dossier du projet
cd c:\Dev\Deploiment_ML\Puls-Events-Culturs

# Permettre l'exécution de scripts PowerShell (si nécessaire)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Lancer le bootstrap
.\scripts\bootstrap.ps1
```

**Ce que fait le script**:
- ✅ Vérifie la version de Python
- ✅ Crée l'environnement virtuel `.venv`
- ✅ Met à jour `pip`, `setuptools`, `wheel`
- ✅ Installe toutes les dépendances (production + dev)
- ✅ Copie `.env.example` vers `.env`
- ✅ Crée le dossier `logs/`

### Option B: Installation Manuelle

#### Windows (PowerShell)
```powershell
# Se placer dans le projet
cd c:\Dev\Deploiment_ML\Puls-Events-Culturs

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Mettre à jour pip
python -m pip install --upgrade pip setuptools wheel

# Installer le projet en mode éditable avec dépendances dev
pip install -e ".[dev]"

# Copier le fichier d'environnement
copy .env.example .env

# Créer le dossier logs
New-Item -ItemType Directory -Path logs -Force
```

---

## ✅ ÉTAPE 3: CONFIGURATION

### 3.1 Éditer le fichier .env

Ouvrir le fichier `.env` dans VS Code ou un éditeur de texte et remplir:

```bash
# ===========================
# OpenAgenda Configuration
# ===========================
OPENAGENDA_API_KEY=votre_clé_openagenda_ici
OPENAGENDA_AGENDA_UID=votre_agenda_uid_ici
OPENAGENDA_LOCATION=Paris

# ===========================
# Mistral AI Configuration
# ===========================
MISTRAL_API_KEY=votre_clé_mistral_ici
```

**Où obtenir les clés?**
- **OpenAgenda**: https://openagenda.com/developers
- **Mistral AI**: https://console.mistral.ai/

### 3.2 Vérifier l'installation

```powershell
# Activer l'environnement (si pas déjà fait)
.\.venv\Scripts\Activate.ps1

# Vérifier les packages installés
pip list

# Vérifier la configuration
python -c "from src.config import settings; print(f'Environment: {settings.environment}')"
```

---

## ✅ ÉTAPE 4: CONSTRUIRE L'INDEX FAISS

**⚠️ IMPORTANT**: Cette étape est OBLIGATOIRE avant de lancer l'API.

### 4.1 Lancer le Build

```powershell
# S'assurer que l'environnement est activé
.\.venv\Scripts\Activate.ps1

# Option 1: Avec Python
python scripts\build_index.py

# Option 2: Avec Make
make build-index

# Option 3: Avec VS Code
# Ctrl+Shift+P -> "Tasks: Run Task" -> "Build: Index from OpenAgenda"
```

### 4.2 Vérifier la Création de l'Index

```powershell
# Vérifier que l'index existe
dir data\index\faiss_index
```

**Fichiers attendus**:
- `index.faiss`: L'index vectoriel FAISS
- `index.pkl`: Métadonnées et docstore

**Durée attendue**: 2-5 minutes selon le nombre d'événements

---

## ✅ ÉTAPE 5: DÉMARRER L'API

### 5.1 Lancer le Serveur

```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Option 1: Mode développement (avec auto-reload)
.\.venv\Scripts\uvicorn.exe api.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Avec Make
make run-debug

# Option 3: Avec VS Code
# F5 -> "FastAPI: Run API Server"
```

### 5.2 Vérifier que l'API est Démarrée

Vous devriez voir dans le terminal:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**URLs à tester**:
- API Docs (Swagger): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## ✅ ÉTAPE 6: TESTER L'API

### 6.1 Via le Navigateur

Ouvrir http://localhost:8000/docs

### 6.2 Via PowerShell

#### Test Health Check
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -ExpandProperty Content
```

**Réponse attendue**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "index_loaded": true
}
```

#### Test Query RAG
```powershell
$body = @{
    question = "Quels sont les concerts de jazz à Paris ce mois-ci?"
    return_sources = $true
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/query" -Method POST -Body $body -ContentType "application/json"
```

#### Test Similarity Search
```powershell
$body = @{
    query = "concert jazz"
    k = 5
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/search" -Method POST -Body $body -ContentType "application/json"
```

#### Test Stats
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/stats" | Select-Object -ExpandProperty Content
```

---

## ✅ ÉTAPE 7: LANCER LES TESTS

### 7.1 Tests Unitaires

```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Lancer tous les tests
.\.venv\Scripts\pytest.exe tests -v

# Avec Make
make test

# Tests avec couverture
make test-cov
```

### 7.2 Voir le Rapport de Couverture

Après `make test-cov`, ouvrir: `htmlcov/index.html`

```powershell
# Ouvrir le rapport dans le navigateur par défaut
start htmlcov\index.html
```

---

## ✅ ÉTAPE 8: DÉVELOPPEMENT

### 8.1 Linter & Formatter

```powershell
# Vérifier le code
.\.venv\Scripts\ruff.exe check .

# Formater le code
.\.venv\Scripts\ruff.exe format .

# Avec Make
make lint
make format
```

### 8.2 Debugging dans VS Code

1. Ouvrir VS Code dans le dossier du projet
2. Installer les extensions recommandées:
   - Python (Microsoft)
   - Pylance (Microsoft)
   - Ruff (Charliermarsh)
3. Appuyer sur `F5` et choisir:
   - "FastAPI: Run API Server" pour debug l'API
   - "Python: Build Index" pour debug l'indexation
   - "Pytest: Run All Tests" pour debug les tests

### 8.3 Tasks VS Code

`Ctrl+Shift+P` → "Tasks: Run Task" → Choisir:
- Bootstrap: Create venv & Install
- Install: Dependencies
- Lint: Ruff Check
- Format: Ruff Format
- Test: Run All Tests
- Build: Index from OpenAgenda
- Run: API Server

---

## ✅ ÉTAPE 9: DOCKER (Optionnel)

### 9.1 Build l'Image Docker

```powershell
# Build
docker build -t puls-events-rag:latest .

# OU avec Make
make docker-build
```

### 9.2 Lancer avec Docker Compose

```powershell
# Démarrer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down

# OU avec Make
make docker-run    # Démarrer
make docker-stop   # Arrêter
```

### 9.3 Accès API dans Docker

L'API sera accessible sur: http://localhost:8000

---

## ✅ ÉTAPE 10: WORKFLOW QUOTIDIEN

### Démarrage Journalier

```powershell
# 1. Ouvrir le terminal dans VS Code
# 2. Activer l'environnement
.\.venv\Scripts\Activate.ps1

# 3. Mettre à jour les dépendances (si nécessaire)
git pull
pip install -e ".[dev]"

# 4. Lancer l'API
make run-debug
```

### Avant un Commit

```powershell
# 1. Formater le code
make format

# 2. Vérifier le linting
make lint

# 3. Lancer les tests
make test

# 4. Si tout est OK, commiter
git add .
git commit -m "feat: votre message"
git push
```

---

## 🔧 TROUBLESHOOTING

### Problème: "Python not found"

**Solution**:
```powershell
# Vérifier que Python est dans le PATH
$env:Path -split ';' | Select-String python

# Si absent, ajouter manuellement ou réinstaller Python avec "Add to PATH"
```

### Problème: "Module not found"

**Solution**:
```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Réinstaller en mode éditable
pip install -e .
```

### Problème: "FAISS index not found"

**Solution**:
```powershell
# Reconstruire l'index
python scripts\build_index.py
```

### Problème: "Execution Policy"

Si vous avez une erreur lors de l'activation du venv:

**Solution**:
```powershell
# Permettre l'exécution de scripts PowerShell pour l'utilisateur courant
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Puis réessayer
.\.venv\Scripts\Activate.ps1
```

### Problème: "Invalid API key"

**Solution**:
1. Vérifier le fichier `.env`
2. S'assurer qu'il n'y a pas de guillemets autour des clés
3. Pas d'espaces autour du `=`
4. Exemple correct: `MISTRAL_API_KEY=sk-abc123`

### Problème: "Port 8000 already in use"

**Solution**:
```powershell
# Trouver le processus utilisant le port 8000
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object OwningProcess

# Arrêter le processus (remplacer <PID> par le numéro de processus)
Stop-Process -Id <PID> -Force

# OU utiliser un autre port
.\.venv\Scripts\uvicorn.exe api.main:app --reload --port 8001
```

---

## 📋 CHECKLIST FINALE

Avant de considérer le projet prêt:

- [ ] Python 3.11+ installé et dans le PATH
- [ ] Environnement virtuel `.venv` créé
- [ ] Toutes les dépendances installées (`pip list` montre les packages)
- [ ] Fichier `.env` créé et configuré avec les clés API
- [ ] Index FAISS construit (`data\index\faiss_index\` existe)
- [ ] Tests passent (`make test` sans erreur)
- [ ] API démarre (`make run-debug` sans erreur)
- [ ] Health check OK (http://localhost:8000/health)
- [ ] Swagger UI accessible (http://localhost:8000/docs)
- [ ] Un test de query fonctionne (via Swagger ou PowerShell)

---

## 🎉 FÉLICITATIONS!

Votre environnement de développement Windows est prêt!

**Prochaines étapes**:
1. Consulter la documentation complète: [README.md](README.md)
2. Explorer le code dans VS Code
3. Tester l'API via Swagger UI

**Ressources**:
- API Docs: http://localhost:8000/docs
- Logs: `logs\app.log`
- Tests: `make test`
- Code quality: `make lint` + `make format`

**Commandes essentielles à retenir**:
```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Construire l'index
python scripts\build_index.py

# Lancer l'API
make run-debug

# Lancer les tests
make test
```

Bon développement! 🚀
