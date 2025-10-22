import pandas as pd
import os
import psycopg2

# Lire les infos de connexion depuis l'environnement, avec valeurs par défaut
db_host = os.environ.get("POSTGRES_HOST", "localhost")
db_port = int(os.environ.get("POSTGRES_PORT", 5432))
db_name = os.environ.get("POSTGRES_DB", "ecommerce")
db_user = os.environ.get("POSTGRES_USER", "user")
db_password = os.environ.get("POSTGRES_PASSWORD", "password")

# Connexion à la base
conn = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)
cur = conn.cursor()

# Créer table si elle n'existe pas
cur.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT,
    customer_unique_id TEXT,
    customer_zip_code_prefix TEXT,
    customer_city TEXT,
    customer_state TEXT
)
""")
conn.commit()

# Dossier des CSV
data_folder = "data"
files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

for file in files:
    file_path = os.path.join(data_folder, file)
    df = pd.read_csv(file_path)

    # Insertion ligne par ligne
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO customers (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
            VALUES (%s, %s, %s, %s, %s)
        """, (row['customer_id'], row['customer_unique_id'], row['customer_zip_code_prefix'], row['customer_city'], row['customer_state']))
    conn.commit()
    print(f"{file} inséré dans PostgreSQL ✅")

cur.close()
conn.close()
