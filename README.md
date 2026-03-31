# Projet Data Engineering M1 - Architecture Médaillon Collaborative

Ce projet implémente une plateforme de données complète pour l'analyse des ventes e-commerce (Olist), structurée selon l'architecture Médaillon (Raw, Silver, Gold).

## Équipe
- **Adam BELOUCIF** (@Adam-Blf)
- **Emilien MORICE** (@emilien754)

## Architecture
1. **Ingestion (Raw)** : `feeder.py` - Ingestion des fichiers CSV vers Parquet avec partitionnement temporel.
2. **Transformation (Silver)** : `processor.py` - Nettoyage, validation métier, jointures complexes et agrégations.
3. **Datamart (Gold)** : `datamart.py` - Export vers une base de données relationnelle SQLite pour exploitation.
4. **API Rest** : `api.py` - Exposition des données via FastAPI avec sécurité JWT et pagination.
5. **Visualisation** : `app.py` - Dashboard interactif Streamlit.

## Installation
```bash
pip install -r requirements.txt
```

## Utilisation
Consultez les commentaires dans chaque script pour les paramètres Spark.
