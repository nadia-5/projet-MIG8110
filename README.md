## Description du projet

* Ce projet met en place une pipeline de traitement de données complète permettant :

* L’extraction de données depuis diverses sources brutes, comme des fichiers CSV.

* Le stockage de ces données dans un Data Lake pour conservation et analyse.

* La transformation et le chargement des données dans une base de données opérationnelle.

* L’historisation des données dans un entrepôt de données pour faciliter l’analyse et la visualisation.

L’objectif est de construire une architecture modulaire, automatisée et scalable, capable de centraliser et de traiter efficacement les données pour répondre aux besoins analytiques et opérationnels

## Architecture générale
![Texte alternatif](./Architecture.png)

## Exécution du pipeline

### Deploiement du projet
`git clone https://github.com/nadia-5/projet-MIG8110`

`cd projet-MIG8110`

Utiliser IDE VSCode de préférence et s'assurer que docker est activer

Faire open in container

`pdm install`: installation des dependances

`pdm clean-env`: suppression des fichiers temporaires de l'environnement

`pdm infra-up`: mise en marche de l'infrastrucutre docker 

`pdm deploy-tf`: deploiement des ressources terraform (table, views, functions, procedures)

`pdm deploy-lib`: deploiement de la librairie et des dag d'orchestration dans airflow

`pdm load-lake`: chargement des données dans le data lake

`pdm deploy-oltp`: chargement de la bd operationnelle

`pdm deploy-olap`: Chargement du datawarehouse

