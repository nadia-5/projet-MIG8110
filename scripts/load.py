import os
import time
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Import des définitions des tables
from tables_definitions import tables

# --- Connexion PostgreSQL avec retry ---
db_host = os.environ.get("POSTGRES_HOST", "db")
db_port = int(os.environ.get("POSTGRES_PORT", 5432))
db_name = os.environ.get("POSTGRES_DB", "ecommerce")
db_user = os.environ.get("POSTGRES_USER", "user")
db_password = os.environ.get("POSTGRES_PASSWORD", "password")

max_retries = 10
for i in range(max_retries):
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        cur = conn.cursor()
        print("Connexion PostgreSQL réussie ✅")
        break
    except psycopg2.OperationalError:
        print(f"Tentative {i+1} échouée, attente 2 secondes...")
        time.sleep(2)
else:
    raise Exception("Impossible de se connecter à PostgreSQL après plusieurs tentatives")

data_folder = "data"

# --- Création des tables et insertion des CSV ---
for table in tables:
    table_name = table["name"]
    columns = table["columns"]
    primary_key = table.get("primary_key")
    foreign_keys = table.get("foreign_keys", [])

    file_path = os.path.join(data_folder, f"{table_name}.csv")
    if not os.path.exists(file_path):
        print(f"⚠️ Fichier {file_path} introuvable, skipping...")
        continue

    # Création de la table SQL
    cols_sql = ", ".join([f"{col} TEXT" for col in columns])

    # Gestion des clés primaires (simples ou multiples)
    if primary_key:
        if isinstance(primary_key, list):
            pk_cols = ", ".join(primary_key)
            cols_sql += f", PRIMARY KEY ({pk_cols})"
        else:
            cols_sql += f", PRIMARY KEY ({primary_key})"

    # Gestion des clés étrangères
    for fk in foreign_keys:
        fk_col, ref_table, ref_col = fk
        cols_sql += f", FOREIGN KEY ({fk_col}) REFERENCES {ref_table}({ref_col})"

    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_sql});"
    cur.execute(create_sql)
    conn.commit()
    print(f"✅ Table {table_name} prête")

    # --- Insertion CSV ---
    df = pd.read_csv(file_path)

    # Nettoyage optionnel (remplace NaN par None)
    df = df.where(pd.notnull(df), None)

    # Conversion en tuples
    data_tuples = list(df[columns].itertuples(index=False, name=None))
    if not data_tuples:
        print(f"⚠️ Aucun enregistrement trouvé pour {table_name}")
        continue

    # Insertion rapide
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"
    try:
        execute_values(cur, sql, data_tuples)
        conn.commit()
        print(f"✅ Données insérées dans {table_name} ({len(data_tuples)} lignes)")
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de l’insertion dans {table_name} : {e}")

cur.close()
conn.close()
print("🔚 Connexion fermée.")
