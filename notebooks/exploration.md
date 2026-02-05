# Exploration des Événements Culturels

Ce notebook permet d'explorer les données OpenAgenda et tester le système RAG.

## Setup

```python
import sys
from pathlib import Path

# Ajouter le projet au path
project_root = Path.cwd().parent
sys.path.insert(0, str(project_root))

# Imports
import json
import pandas as pd
from src.config import settings
from src.indexer import OpenAgendaFetcher, EventProcessor
from src.rag import get_rag_system
```

## 1. Fetch Events

```python
# Initialiser le fetcher
fetcher = OpenAgendaFetcher(
    api_key=settings.openagenda_api_key,
    base_url=settings.openagenda_base_url,
    agenda_uid=settings.openagenda_agenda_uid,
)

# Fetcher quelques événements
events = fetcher.fetch_events(location="Paris", max_events=50)
print(f"Fetched {len(events)} events")
```

## 2. Explore Events

```python
# Convertir en DataFrame
df = pd.DataFrame(events)
df.head()
```

```python
# Statistiques
print(f"Total events: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")
```

```python
# Exemple d'événement
event = events[0]
print(json.dumps(event, indent=2, ensure_ascii=False)[:1000])
```

## 3. Text Processing

```python
# Processor
processor = EventProcessor(chunk_size=500, chunk_overlap=100)

# Convertir un événement en texte
text = processor.event_to_text(events[0])
print(text)
```

```python
# Process plusieurs événements
texts, metadatas = processor.process_events(events[:10])
print(f"Generated {len(texts)} text chunks from 10 events")
print(f"\nExample chunk:\n{texts[0]}")
print(f"\nExample metadata:\n{metadatas[0]}")
```

## 4. Test RAG System

**Note**: L'index FAISS doit être construit avant cette section.

```python
# Charger le système RAG
rag_system = get_rag_system()
rag_system.load_index()
rag_system.initialize_llm()
rag_system.setup_qa_chain()

print("RAG system loaded!")
```

```python
# Test query
result = rag_system.query(
    question="Quels sont les événements de théâtre disponibles?",
    return_sources=True
)

print("Question:", result["question"])
print("\nAnswer:", result["answer"])
print(f"\nSources: {len(result.get('sources', []))} documents")
```

```python
# Test similarity search
results = rag_system.similarity_search(
    query="concert jazz",
    k=3
)

for i, result in enumerate(results, 1):
    print(f"\n=== Result {i} ===")
    print(f"Content: {result['content'][:200]}...")
    print(f"Metadata: {result['metadata']}")
```

## 5. Visualizations

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Distribution par lieu (top 10)
if 'locationName' in df.columns:
    location_counts = df['locationName'].value_counts().head(10)
    
    plt.figure(figsize=(12, 6))
    location_counts.plot(kind='barh')
    plt.title('Top 10 Lieux d\'Événements')
    plt.xlabel('Nombre d\'Événements')
    plt.tight_layout()
    plt.show()
```

```python
# Nuage de mots des descriptions
from wordcloud import WordCloud

# Extraire toutes les descriptions
descriptions = []
for event in events:
    if desc := event.get('description', {}).get('fr'):
        descriptions.append(desc)

all_text = ' '.join(descriptions)

# Générer le nuage
wordcloud = WordCloud(
    width=800, 
    height=400,
    background_color='white',
    colormap='viridis'
).generate(all_text)

plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Nuage de Mots - Descriptions d\'Événements', fontsize=16)
plt.tight_layout()
plt.show()
```

---

**Note**: Pour installer les dépendances supplémentaires pour ce notebook:

```bash
pip install jupyter matplotlib seaborn wordcloud
```
