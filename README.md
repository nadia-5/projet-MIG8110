# Projet MIG8110 – Infrastructure de base de données et analyse

## Description
Ce projet met en place une infrastructure de base de données PostgreSQL via Docker
et permet de charger, transformer et analyser des données à partir de fichiers CSV.
Les scripts Python automatisent la création des tables, l’insertion des données
et certaines analyses exploratoires.

---

## Structure du projet



---

## Installation et exécution

### 1. Cloner le dépôt
```bash
git clone https://github.com/nadia-5/projet-MIG8110.git
cd projet-MIG8110

docker-compose up --build
docker exec -it python_app python scripts/load.py
