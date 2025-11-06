import polars as pl
import s3fs

<<<<<<< HEAD
=======

def save_file_path(bucket_name: str, base_file: pl.DataFrame, date: str = None) -> str:
    if date is None:
        path_save = f"s3://raw-data/{bucket_name}/{bucket_name}.parquet"
    else:
        annee = str(date.year).zfill(4)
        mois = str(date.month).zfill(2)
        jour = str(date.day).zfill(2)

        path_save = f"s3://raw-data/{bucket_name}/{annee}/{mois}/{jour}/{bucket_name}.parquet"

    # Écriture directe dans MinIO
    with fs.open(path_save, "wb") as f:
        base_file.write_parquet(f)
        f.close()

def read_file_path(bucket_name: str, file_name: str) -> str:
    path_read = f"s3://{bucket_name}/{file_name}.csv"

    with fs.open(path_read, "rb") as f:
        df = pl.read_csv(f)
        f.close()

    return df

# Configurer le système de fichiers S3 (compatible MinIO)
fs = s3fs.S3FileSystem(
    key="minio",
    secret="minio123",
    client_kwargs={"endpoint_url": "http://minio:9000"}
)

>>>>>>> 737b56b (feat: add etl extraction)
# Lire directement un CSV depuis MinIO
customer_df = read_file_path("sources", "customers_dataset")
geolocation_df = read_file_path("sources", "geolocation_dataset")
order_items_df = read_file_path("sources", "order_items_dataset")
order_payments_df = read_file_path("sources", "order_payments_dataset")
order_reviews_df = read_file_path("sources", "order_reviews_dataset")
orders_df = read_file_path("sources", "orders_dataset")
products_df = read_file_path("sources", "products_dataset")
products_category_name_translation_df = read_file_path("sources", "product_category_name_translation")
sellers_df = read_file_path("sources", "sellers_dataset")

save_file_path("ref-product-category-name-translation", products_category_name_translation_df)

save_file_path("ref-geolocation", geolocation_df)

distinct_dates = (
    orders_df.select(pl.col("order_purchase_timestamp").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").cast(pl.Date))
      .unique()
      .sort("order_purchase_timestamp")
)

for date in distinct_dates["order_purchase_timestamp"]:

<<<<<<< HEAD
    order_historique_result_df = orders_df.filter(pl.col("order_purchase_timestamp").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").cast(pl.Date) < date)

    order_result_df = orders_df.filter(pl.col("order_purchase_timestamp").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").cast(pl.Date) == date)
    
    order_reviews_result_df = (
        order_result_df
        .join(order_reviews_df, on="order_id", how="inner").select(order_reviews_df.columns)
    )

    order_items_result_df = (
        order_result_df
        .join(order_items_df, on="order_id", how="inner").select(order_items_df.columns)
    )

    order_items_historique_result_df = order_historique_result_df.join(order_items_df, on="order_id", how="inner").select(order_items_df.columns)
    

    order_payments_result_df = (
        order_result_df
        .join(order_payments_df, on="order_id", how="inner").select(order_payments_df.columns)
    )

    customer_result_df = (
        order_result_df
        .join(order_historique_result_df, on="customer_id", how="anti")
        .join(customer_df, on="customer_id", how="inner").select(customer_df.columns)
    )

    sellers_result_df = (
        order_items_result_df
        .join(order_items_historique_result_df, on="seller_id", how="anti")
        .join(sellers_df, on="seller_id", how="inner").select(sellers_df.columns)
    )

    products_result_df = (
        order_items_result_df
        .join(order_items_historique_result_df, on="product_id", how="anti")
        .join(products_df, on="product_id", how="inner").select(products_df.columns)
    )
=======
    order_result_df = orders_df.filter(pl.col("order_purchase_timestamp").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").cast(pl.Date) <= date)

    order_reviews_result_df = order_result_df.join(order_reviews_df, on="order_id", how="inner").select(order_reviews_df.columns)

    order_items_result_df = order_result_df.join(order_items_df, on="order_id", how="inner").select(order_items_df.columns)

    order_payments_result_df = order_result_df.join(order_payments_df, on="order_id", how="inner").select(order_payments_df.columns)

    customer_result_df = order_result_df.join(customer_df, on="customer_id", how="inner").select(customer_df.columns)

    sellers_result_df = order_items_result_df.join(sellers_df, on="seller_id", how="inner").select(sellers_df.columns)

    products_result_df = order_items_result_df.join(products_df, on="product_id", how="inner").select(products_df.columns)
>>>>>>> 737b56b (feat: add etl extraction)


    # Chemin S3 (compatible ARN)
    save_file_path("orders", order_result_df, date)

    save_file_path("order-reviews", order_reviews_result_df, date)

    save_file_path("order-items", order_items_result_df, date)

    save_file_path("order-payments", order_payments_result_df, date)

    save_file_path("customers", customer_result_df, date)

    save_file_path("sellers", sellers_result_df, date)

    save_file_path("products", products_result_df, date)

