import pandas as pd
import os
import io
from datetime import timedelta
from minio import Minio
from minio.error import S3Error

# --- CONFIGURATION ---
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "minio"
MINIO_SECRET_KEY = "minio123"

# On écrit uniquement dans la "Landing Zone" (sources)
BUCKET_NAME = "sources"
SOURCE_DIR = "/workspace/source_data"

START_DATE = "2016-09-04"
END_DATE = "2018-10-17"

FILES = {
    "orders": "olist_orders_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
    "geolocation": "olist_geolocation_dataset.csv"
}

def get_minio_client():
    return Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

def upload_csv(client, df, object_path):
    """Upload un DataFrame en format CSV"""
    try:
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        csv_buffer = io.BytesIO(csv_bytes)
        
        client.put_object(
            BUCKET_NAME,
            object_path,
            csv_buffer,
            len(csv_bytes),
            content_type='application/csv'
        )
    except S3Error as err:
        print(f"❌ Erreur Upload {object_path}: {err}")

def load_data():
    print("⏳ Chargement des données locales...")
    dfs = {}
    for key, filename in FILES.items():
        path = os.path.join(SOURCE_DIR, filename)
        if os.path.exists(path):
            dfs[key] = pd.read_csv(path)
    
    if 'orders' in dfs:
        dfs['orders']['order_purchase_timestamp'] = pd.to_datetime(dfs['orders']['order_purchase_timestamp'])
    return dfs

def process_daily_split(client, target_date_str, dfs):
    target_date = pd.to_datetime(target_date_str).date()
    df_orders = dfs['orders']
    
    daily_orders = df_orders[df_orders['order_purchase_timestamp'].dt.date == target_date]
    if daily_orders.empty: return 0

    # Architecture : daily_data/YYYY-MM-DD/fichier.csv
    prefix = f"daily_data/{target_date_str}"
    
    daily_order_ids = daily_orders['order_id'].unique()
    
    # 1. Orders
    upload_csv(client, daily_orders, f"{prefix}/orders.csv")
    
    # 2. Items & Dépendances
    if 'items' in dfs:
        daily_items = dfs['items'][dfs['items']['order_id'].isin(daily_order_ids)]
        upload_csv(client, daily_items, f"{prefix}/items.csv")
        
        # Dimensions (Delta)
        if 'products' in dfs:
            d_prod = dfs['products'][dfs['products']['product_id'].isin(daily_items['product_id'].unique())]
            upload_csv(client, d_prod, f"{prefix}/products.csv")

        if 'sellers' in dfs:
            d_sell = dfs['sellers'][dfs['sellers']['seller_id'].isin(daily_items['seller_id'].unique())]
            upload_csv(client, d_sell, f"{prefix}/sellers.csv")

    # 3. Autres tables
    if 'payments' in dfs:
        d_pay = dfs['payments'][dfs['payments']['order_id'].isin(daily_order_ids)]
        upload_csv(client, d_pay, f"{prefix}/order_payments.csv")
        
    if 'reviews' in dfs:
        d_rev = dfs['reviews'][dfs['reviews']['order_id'].isin(daily_order_ids)]
        upload_csv(client, d_rev, f"{prefix}/order_reviews.csv")

    if 'customers' in dfs:
        # Note: on filtre customers sur ceux liés aux commandes du jour
        d_cust = dfs['customers'][dfs['customers']['customer_id'].isin(daily_orders['customer_id'])]
        upload_csv(client, d_cust, f"{prefix}/customers.csv")

    return len(daily_orders)

def main():
    client = get_minio_client()
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)

    dfs = load_data()
    
    # --- FICHIERS COMMUNS (Référence) ---
    print("\n--- Upload des références 'common' (CSV) ---")
    if 'geolocation' in dfs:
        upload_csv(client, dfs['geolocation'], "common/geolocation.csv")
        print("✅ Geolocation")
        
    if 'category_translation' in dfs:
        upload_csv(client, dfs['category_translation'], "common/product_category_name_translation.csv")
        print("✅ Traduction Catégories")

    # --- SPLIT QUOTIDIEN ---
    print("\n--- Découpage Quotidien ---")
    current_date = pd.to_datetime(START_DATE)
    end_date = pd.to_datetime(END_DATE)
    
    total_orders = 0
    while current_date <= end_date:
        str_date = current_date.strftime("%Y-%m-%d")
        count = process_daily_split(client, str_date, dfs)
        if count > 0:
            print(f"📅 {str_date} : {count} commandes")
            total_orders += count
        current_date += timedelta(days=1)
        
    print(f"\n🎉 Terminé ! {total_orders} commandes simulées dans '{BUCKET_NAME}'.")

if __name__ == "__main__":
    main()