#!/bin/bash
# Docker Entrypoint Script
# Vérifie les données, télécharge si nécessaire, puis construit l'index FAISS avant de lancer l'API

set -e

echo "Demarrage du systeme RAG Puls Events Culturs..."

# Vérifier si les données JSON existent
if [ ! -f "/app/data/raw/openagenda.json" ]; then
    echo "ATTENTION: Donnees JSON OpenAgenda introuvables."
    echo "Recuperation des evenements depuis l'API OpenAgenda..."
    
    # Le script build_index.py télécharge automatiquement les données si elles n'existent pas
    python scripts/build_index.py
    
    if [ $? -eq 0 ]; then
        echo "SUCCES: Donnees recuperees et index construit avec succes."
    else
        echo "ERREUR: Echec de la recuperation des donnees ou de la construction de l'index."
        exit 1
    fi
elif [ ! -f "/app/data/index/faiss_index/index.faiss" ]; then
    echo "Donnees JSON trouvees."
    echo "ATTENTION: Index FAISS introuvable. Construction de l'index a partir des donnees existantes..."
    
    python scripts/build_index.py
    
    if [ $? -eq 0 ]; then
        echo "SUCCES: Index construit avec succes."
    else
        echo "ERREUR: Echec de la construction de l'index."
        exit 1
    fi
else
    echo "Donnees JSON trouvees."
    echo "Index FAISS trouve. Pas de reconstruction necessaire."
fi

echo "Demarrage du serveur API..."

# Lancer l'API avec les arguments passés au script
exec "$@"
