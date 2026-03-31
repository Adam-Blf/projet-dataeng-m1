# Projet Data Engineering M1 - Architecture Médaillon Collaborative

![Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

Ce projet implémente une plateforme de données complète pour l'analyse des ventes e-commerce (Olist), structurée selon l'architecture Médaillon (Raw, Silver, Gold).

## Équipe
- **Adam BELOUCIF** ([@Adam-Blf](https://github.com/Adam-Blf))
- **Emilien MORICE** ([@emilien754](https://github.com/emilien754))
- **Arnaud DISSONGO** ([@Panason1c](https://github.com/Panason1c))

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
