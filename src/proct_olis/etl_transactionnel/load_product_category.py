import psycopg2
import csv
import os


def get_connection():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "postgres"),
        port=os.getenv("PG_PORT", "5432"),
        database=os.getenv("PG_DATABASE", "operation"),
        user=os.getenv("PG_USER", "admin"),
        password=os.getenv("PG_PASSWORD", "admin"),
    )


def detect_columns(fieldnames):

    print("Colonnes trouvées dans le CSV :", fieldnames)

    norm_map = {name.strip().lower(): name for name in fieldnames}

    pt_col = None
    en_col = None

    for norm, original in norm_map.items():
        if "product_category_name_english" in norm:
            en_col = original
        elif "product_category_name" in norm:
            # attention à ne pas écraser la version english
            if "english" not in norm:
                pt_col = original

    if pt_col is None or en_col is None:
        raise RuntimeError(
            f"Impossible de trouver les colonnes pour les catégories.\n"
            f"Colonnes disponibles : {fieldnames}"
        )

    print(f"Colonne portugais  détectée : {pt_col}")
    print(f"Colonne anglais    détectée : {en_col}")
    return pt_col, en_col


def load_product_category(csv_path: str):
    conn = get_connection()
    cur = conn.cursor()

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            pt_col, en_col = detect_columns(reader.fieldnames)

            for row in reader:
                name_pt = row[pt_col]
                name_en = row[en_col]

                cur.execute(
                    """
                    INSERT INTO product_category (product_category_name, product_category_description)
                    VALUES (%s, %s)
                    ON CONFLICT (product_category_name) DO NOTHING;
                    """,
                    (name_pt.lower(), name_en),
                )

        conn.commit()
        print("✔ product_category chargé avec succès !")

    except Exception as e:
        print("ERREUR :", e)
        conn.rollback()

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load_product_category("source_data/product_category_name_translation.csv")
