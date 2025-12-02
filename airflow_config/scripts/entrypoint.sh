#!/bin/bash
set -e

# echo "⏳ Attente de PostgreSQL..."

# # Attente active jusqu'à ce que PostgreSQL réponde
# until pg_isready -h postgres_metadata -p 5432 -U admin; do
#   echo "⏱️  PostgreSQL non prêt, nouvelle tentative dans 5s..."
#   sleep 5
# done

# echo "✅ PostgreSQL est prêt."

# # Vérifie si la table 'log' existe
# echo "🔍 Vérification de la table 'log'..."
# if psql "postgresql://airflow:airflow@postgres_metadata:5432/metadata" -tAc \
#    "SELECT 1 FROM information_schema.tables WHERE table_name = 'log';" | grep -q 1; then
#   echo "✅ Table 'log' déjà présente, pas besoin d'initialiser."
# else
#   echo "⚙️  Table 'log' absente, initialisation de la base..."
#   airflow db init
# fi

echo "⚙️  Table 'log' absente, initialisation de la base..."
airflow db init

# (Optionnel) Appliquer les migrations si tu utilises `airflow db migrate`
airflow db migrate

# Création de l'utilisateur admin si nécessaire
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin

# Lancement du scheduler en arrière-plan
echo "🚀 Lancement du scheduler..."
airflow scheduler &

# Lancement du webserver
echo "🌐 Lancement du webserver..."
exec airflow webserver --port 8080
