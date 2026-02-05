# Métriques d'Évaluation RAG - Guide Complet

Ce document explique les métriques utilisées pour évaluer la qualité du système RAG et comment les interpréter.

## 📊 Métriques RAGAS

### 1. Faithfulness (Fidélité)

**Définition** : Mesure si la réponse générée est fidèle aux sources/contextes fournis, sans hallucination.

**Calcul** : 
```
Faithfulness = Nombre de déclarations soutenues par les sources / Nombre total de déclarations
```

**Interprétation** :
- **0.90 - 1.00** : Excellent - Très peu ou pas d'hallucinations
- **0.70 - 0.89** : Bon - Quelques imprécisions mineures
- **0.50 - 0.69** : Moyen - Hallucinations notables
- **< 0.50** : Mauvais - Hallucinations fréquentes

**Importance** : ⭐⭐⭐⭐⭐ (Critique)

**Actions si score faible** :
- Vérifier la qualité des chunks/contextes
- Améliorer le prompt pour réduire les hallucinations
- Augmenter le nombre de sources récupérées
- Revoir le système de reranking

### 2. Answer Relevancy (Pertinence de la Réponse)

**Définition** : Mesure si la réponse est pertinente par rapport à la question posée.

**Calcul** : Basé sur la similarité sémantique entre la question et la réponse générée.

**Interprétation** :
- **0.90 - 1.00** : Excellent - Réponse très pertinente
- **0.70 - 0.89** : Bon - Réponse généralement pertinente
- **0.50 - 0.69** : Moyen - Réponse partiellement pertinente
- **< 0.50** : Mauvais - Réponse hors sujet

**Importance** : ⭐⭐⭐⭐⭐ (Critique)

**Actions si score faible** :
- Améliorer le prompt système
- Optimiser la récupération de contexte
- Vérifier la qualité des embeddings
- Ajuster les paramètres de température du LLM

### 3. Context Precision (Précision du Contexte)

**Définition** : Mesure la proportion de contextes récupérés qui sont réellement pertinents pour la question.

**Calcul** :
```
Context Precision = Contextes pertinents récupérés / Total contextes récupérés
```

**Interprétation** :
- **0.80 - 1.00** : Excellent - Peu de bruit dans les contextes
- **0.60 - 0.79** : Bon - Quelques contextes non pertinents
- **0.40 - 0.59** : Moyen - Beaucoup de bruit
- **< 0.40** : Mauvais - Majorité de contextes non pertinents

**Importance** : ⭐⭐⭐⭐

**Actions si score faible** :
- Améliorer le chunking (taille, overlap)
- Optimiser les embeddings
- Implémenter/améliorer le reranking
- Ajuster le nombre k de résultats récupérés

### 4. Context Recall (Rappel du Contexte)

**Définition** : Mesure la proportion d'informations nécessaires qui ont été récupérées.

**Calcul** :
```
Context Recall = Informations nécessaires récupérées / Total informations nécessaires
```

**Interprétation** :
- **0.80 - 1.00** : Excellent - Toutes les infos nécessaires récupérées
- **0.60 - 0.79** : Bon - Quelques infos manquantes
- **0.40 - 0.59** : Moyen - Beaucoup d'infos manquantes
- **< 0.40** : Mauvais - Informations critiques manquantes

**Importance** : ⭐⭐⭐⭐

**Actions si score faible** :
- Augmenter k (nombre de résultats)
- Améliorer la qualité de l'indexation
- Enrichir les métadonnées
- Vérifier la complétude des données sources

## 🎯 Seuils Recommandés

### Environnement de Production

```python
PRODUCTION_THRESHOLDS = {
    "faithfulness": 0.85,          # Critique
    "answer_relevancy": 0.85,      # Critique
    "context_precision": 0.75,     # Important
    "context_recall": 0.75         # Important
}
```

### Environnement de Développement

```python
DEV_THRESHOLDS = {
    "faithfulness": 0.70,
    "answer_relevancy": 0.70,
    "context_precision": 0.65,
    "context_recall": 0.65
}
```

### Environnement de Test

```python
TEST_THRESHOLDS = {
    "faithfulness": 0.60,
    "answer_relevancy": 0.60,
    "context_precision": 0.55,
    "context_recall": 0.55
}
```

## 📈 Score de Qualité Global

### Calcul Simple (Moyenne)

```python
quality_score = (faithfulness + answer_relevancy + context_precision + context_recall) / 4
```

### Calcul Pondéré (Recommandé)

```python
weights = {
    "faithfulness": 0.35,          # Le plus important
    "answer_relevancy": 0.35,      # Le plus important
    "context_precision": 0.15,
    "context_recall": 0.15
}

quality_score = sum(metric * weights[name] for name, metric in metrics.items())
```

### Interprétation du Score Global

- **0.85 - 1.00** : 🟢 Excellent - Système prêt pour production
- **0.70 - 0.84** : 🟡 Bon - Améliorations mineures recommandées
- **0.55 - 0.69** : 🟠 Moyen - Améliorations importantes nécessaires
- **< 0.55** : 🔴 Mauvais - Révision complète requise

## 🔍 Analyse des Régressions

### Détection de Régression

Une régression est détectée quand :

```python
change = current_score - previous_score
regression_threshold = -0.05  # -5%

if change < regression_threshold:
    # Régression détectée
    severity = "high" if change < -0.10 else "medium"
```

### Sévérité des Régressions

- **Haute** : Baisse > 10% → Intervention immédiate
- **Moyenne** : Baisse 5-10% → Investigation requise
- **Faible** : Baisse < 5% → Monitoring

## 📊 Métriques de Performance

### Temps de Réponse

- **Excellent** : < 1s
- **Bon** : 1-3s
- **Acceptable** : 3-5s
- **Lent** : > 5s

### Débit (Throughput)

- **Excellent** : > 10 req/s
- **Bon** : 5-10 req/s
- **Acceptable** : 1-5 req/s
- **Faible** : < 1 req/s

### Temps de Construction d'Index

Pour 1000 événements :
- **Excellent** : < 2 min
- **Bon** : 2-5 min
- **Acceptable** : 5-10 min
- **Lent** : > 10 min

## 📋 Checklist d'Évaluation

### Avant Déploiement

- [ ] Toutes les métriques RAGAS > seuils de production
- [ ] Aucune régression détectée
- [ ] Temps de réponse < 3s (P95)
- [ ] Tests de charge réussis
- [ ] Couverture de code > 80%
- [ ] Tous les tests unitaires passent

### Monitoring Continu

- [ ] Évaluation RAGAS hebdomadaire
- [ ] Suivi des tendances
- [ ] Alertes configurées
- [ ] Historique des évaluations sauvegardé
- [ ] Rapports générés automatiquement

## 🚨 Alertes et Actions

### Alerte Critique

**Conditions** :
- Faithfulness < 0.70
- Answer Relevancy < 0.70
- Régression > 10%

**Actions** :
1. Arrêter les déploiements
2. Analyser les logs
3. Identifier la cause
4. Corriger le problème
5. Re-tester
6. Redéployer

### Alerte Warning

**Conditions** :
- Métriques entre seuil - 0.10 et seuil
- Régression 5-10%

**Actions** :
1. Investiguer la cause
2. Planifier des améliorations
3. Augmenter la fréquence de monitoring
4. Documenter les observations

## 📝 Exemple d'Interprétation

### Scénario 1 : Résultats Excellents

```json
{
  "faithfulness": 0.92,
  "answer_relevancy": 0.89,
  "context_precision": 0.85,
  "context_recall": 0.83
}
```

**Interprétation** :
- ✅ Système très fiable (faithfulness élevé)
- ✅ Réponses pertinentes
- ✅ Contextes bien ciblés
- ✅ Bonne couverture des informations
- **Action** : Continuer le monitoring, prêt pour production

### Scénario 2 : Problème de Contexte

```json
{
  "faithfulness": 0.88,
  "answer_relevancy": 0.85,
  "context_precision": 0.55,
  "context_recall": 0.52
}
```

**Interprétation** :
- ✅ Bonnes réponses et fidélité
- ⚠️ Problème de récupération de contexte
- **Cause probable** : Chunking sous-optimal, embeddings faibles
- **Action** : Revoir la stratégie d'indexation et de récupération

### Scénario 3 : Problème d'Hallucination

```json
{
  "faithfulness": 0.55,
  "answer_relevancy": 0.82,
  "context_precision": 0.75,
  "context_recall": 0.78
}
```

**Interprétation** :
- ⚠️ Hallucinations fréquentes
- ✅ Bon contexte récupéré
- **Cause probable** : Prompt trop permissif, température trop élevée
- **Action** : Revoir le prompt, ajuster température, forcer l'utilisation des sources

## 🔄 Processus d'Amélioration Continue

1. **Collecter** : Exécuter évaluations régulières
2. **Analyser** : Identifier les patterns et tendances
3. **Diagnostiquer** : Trouver les causes des problèmes
4. **Améliorer** : Implémenter les corrections
5. **Valider** : Re-tester avec nouvelles évaluations
6. **Déployer** : Mettre en production si validé
7. **Monitor** : Surveiller en continu

## 📚 Ressources

- [RAGAS Documentation](https://docs.ragas.io/)
- [RAG Evaluation Best Practices](https://www.ragas.io/blog/evaluation)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

**Note** : Ces métriques et seuils sont des recommandations basées sur les meilleures pratiques. Ils peuvent être ajustés selon les besoins spécifiques de votre projet.
