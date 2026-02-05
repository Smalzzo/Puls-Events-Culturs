# Architecture du Projet

## 🏛️ Vue d'Ensemble

Ce document décrit l'architecture technique du POC RAG Puls Events Culturs.

## 📐 Architecture Système

### Composants Principaux

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ /query   │  │ /search  │  │ /health  │  │ /stats   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   Business Logic (src/)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Config     │  │   Logger     │  │     RAG      │      │
│  │  (Pydantic)  │  │   (JSON)     │  │  (LangChain) │      │
│  └──────────────┘  └──────────────┘  └──────┬───────┘      │
│  ┌──────────────────────────────────────────▼───────┐      │
│  │              Indexer & Embeddings                 │      │
│  │  (OpenAgenda Fetcher + Sentence Transformers)     │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   Data & Storage Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  FAISS Index │  │  Raw Events  │  │     Logs     │      │
│  │  (data/index)│  │  (data/raw)  │  │   (logs/)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   External Services                          │
│  ┌──────────────┐                  ┌──────────────┐         │
│  │  OpenAgenda  │                  │  Mistral AI  │         │
│  │     API      │                  │     API      │         │
│  └──────────────┘                  └──────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Flux de Données

### 1. Indexation (Build Phase)

```
┌──────────────┐
│ build_index  │
│   script     │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│ OpenAgendaFetcher                │
│ - Fetch events via API           │
│ - Filter by location             │
│ - Save raw JSON                  │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ EventProcessor                   │
│ - Convert events to text         │
│ - Chunk text (RecursiveTextSplit)│
│ - Extract metadata               │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ FAISSIndexBuilder                │
│ - Load embedding model           │
│ - Generate embeddings            │
│ - Build FAISS index              │
│ - Save to disk                   │
└──────────────────────────────────┘
```

### 2. Requête (Query Phase)

```
┌──────────────┐
│ User Query   │
│ via API      │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────┐
│ FastAPI Endpoint (/query)          │
│ - Validate request                 │
│ - Log query                        │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ RAGSystem                          │
│ - Embed query                      │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ FAISS Retriever                    │
│ - Similarity search                │
│ - Retrieve top-k documents         │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Mistral LLM (via LangChain)        │
│ - Format prompt with context       │
│ - Generate answer                  │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│ Response                           │
│ - Answer + sources                 │
│ - Return to user                   │
└────────────────────────────────────┘
```

## 🧩 Modules Détaillés

### src/config.py

**Responsabilité**: Configuration centralisée

**Technologies**:
- `pydantic-settings`: Validation et parsing
- `.env`: Variables d'environnement

**Fonctionnalités**:
- Chargement automatique depuis `.env`
- Validation des types
- Valeurs par défaut
- Cache singleton (`@lru_cache`)

### src/logger.py

**Responsabilité**: Logging structuré

**Technologies**:
- Python `logging`
- Custom JSON formatter

**Fonctionnalités**:
- Format JSON ou texte
- Multi-handlers (console + fichier)
- Niveaux configurables
- Réduction du bruit (libs tierces)

### src/indexer.py

**Responsabilité**: Indexation des événements

**Classes**:

1. **OpenAgendaFetcher**
   - Requêtes HTTP vers OpenAgenda
   - Pagination automatique
   - Sauvegarde des données brutes

2. **EventProcessor**
   - Conversion event → texte
   - Chunking avec LangChain
   - Extraction de métadonnées

3. **FAISSIndexBuilder**
   - Chargement du modèle d'embeddings
   - Génération des vecteurs
   - Construction de l'index FAISS
   - Persistance sur disque

### src/rag.py

**Responsabilité**: Système RAG complet

**Classes**:

1. **RAGSystem**
   - Chargement de l'index FAISS
   - Initialisation du LLM Mistral
   - Setup de la chaîne QA (LangChain)
   - Méthodes de query/search

**Patterns**:
- Singleton lazy-loaded
- Séparation retrieval/generation
- Prompt template personnalisable

### api/main.py

**Responsabilité**: API REST

**Technologies**:
- FastAPI
- Pydantic models
- CORS middleware
- Lifespan events

**Endpoints**:
- `GET /`: Info API
- `GET /health`: Health check
- `POST /query`: RAG complet
- `POST /search`: Similarity search
- `GET /stats`: Statistiques index

## 🔐 Sécurité

### Pratiques Actuelles

✅ **Implémenté**:
- Variables sensibles dans `.env`
- `.env` dans `.gitignore`
- Validation Pydantic des inputs
- CORS configuré
- Health checks
- Error handling global

⚠️ **À Implémenter (Production)**:
- Authentification API (JWT, API keys)
- Rate limiting
- HTTPS obligatoire
- Secrets management (Vault, AWS Secrets)
- Input sanitization avancée
- Monitoring & alerting

## 📊 Performance

### Optimisations

1. **Embeddings**:
   - Modèle local (pas d'appel API)
   - Cache possible des embeddings

2. **FAISS**:
   - Index `Flat` (exact) pour précision
   - Option `IVF` pour rapidité (si gros volume)

3. **API**:
   - Async/await où approprié
   - Pre-loading de l'index au startup
   - Singleton RAG system

### Limites

- **FAISS**: Chargé en mémoire (RAM)
- **LLM**: Latence API Mistral (réseau)
- **Concurrence**: Single process (utiliser Gunicorn pour scale)

## 🧪 Tests

### Stratégie de Test

```
tests/
├── test_config.py      # Tests unitaires configuration
├── test_indexer.py     # Tests unitaires indexation
├── test_api.py         # Tests d'intégration API
└── __init__.py         # Fixtures pytest
```

**Couverture**:
- Tests unitaires: Logique métier isolée
- Tests d'intégration: Endpoints API
- Mocks: Services externes (Mistral, OpenAgenda)

## 🐳 Docker

### Architecture Container

**Image**:
- Base: `python:3.11-slim`
- Multi-stage build (optimisation taille)
- User non-root pour sécurité

**Volumes**:
- `.env`: Configuration (read-only)
- `data/index/`: Persistance index FAISS
- `logs/`: Persistance logs

**Networking**:
- Port 8000 exposé
- Bridge network

## 📈 Évolutivité

### Scaling Horizontal

**Options**:
1. **API**: Load balancer + multiple instances
2. **Index**: Index partagé (NFS, S3)
3. **Cache**: Redis pour embeddings fréquents

### Scaling Vertical

**Bottlenecks**:
- RAM: Taille de l'index FAISS
- CPU: Génération embeddings
- I/O: Lecture/écriture index

## 🔧 Maintenance

### Opérations Courantes

1. **Rebuild Index**:
   ```bash
   python scripts/build_index.py
   ```

2. **Update Dependencies**:
   ```bash
   pip install --upgrade -e ".[dev]"
   ```

3. **Check Logs**:
   ```bash
   tail -f logs/app.log
   ```

4. **Backup Index**:
   ```bash
   tar -czf faiss_backup.tar.gz data/index/
   ```

---

## 📚 Références Techniques

- **LangChain**: https://python.langchain.com/
- **FAISS**: https://github.com/facebookresearch/faiss
- **FastAPI**: https://fastapi.tiangolo.com/
- **Mistral AI**: https://docs.mistral.ai/
- **Pydantic**: https://docs.pydantic.dev/
- **Sentence Transformers**: https://www.sbert.net/
