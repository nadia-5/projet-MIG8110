resource "minio_s3_object" "customers" {
  depends_on = [minio_s3_bucket.sources]
  bucket_name = minio_s3_bucket.sources.bucket
  object_name = "customers_dataset.csv"
  content_type = "text/csv"
  source = "../source_data/olist_customers_dataset.csv"
}

resource "minio_s3_object" "geolocation" {
  depends_on = [minio_s3_bucket.sources]
  bucket_name = minio_s3_bucket.sources.bucket
  object_name = "geolocation_dataset.csv"
  content_type = "text/csv"
  source = "../source_data/olist_geolocation_dataset.csv"
}

resource "minio_s3_object" "order-items" {
  depends_on = [minio_s3_bucket.sources]
  bucket_name = minio_s3_bucket.sources.bucket
  object_name = "order_items_dataset.csv"
  content_type = "text/csv"
  source = "../source_data/olist_order_items_dataset.csv"
}

resource "minio_s3_object" "order-payments" {
  depends_on = [minio_s3_bucket.sources]
  bucket_name = minio_s3_bucket.sources.bucket
  object_name = "order_payments_dataset.csv"
  content_type = "text/csv"
  source = "../source_data/olist_order_payments_dataset.csv"
}

resource "minio_s3_object" "order-reviews" {
  depends_on = [minio_s3_bucket.sources]
  bucket_name = minio_s3_bucket.sources.bucket
  object_name = "order_reviews_dataset.csv"
  content_type = "text/csv"
  source = "../source_data/olist_order_reviews_dataset.csv"
}

resource "minio_s3_object" "orders" {
  depends_on = [minio_s3_bucket.sources]
  bucket_name = minio_s3_bucket.sources.bucket
  object_name = "orders_dataset.csv"
  content_type = "text/csv"
  source = "../source_data/olist_orders_dataset.csv"
}

resource "minio_s3_object" "products" {
  depends_on = [minio_s3_bucket.sources]
  bucket_name = minio_s3_bucket.sources.bucket
  object_name = "products_dataset.csv"
  content_type = "text/csv"
  source = "../source_data/olist_products_dataset.csv"
}

resource "minio_s3_object" "sellers" {
  depends_on = [minio_s3_bucket.sources]
  bucket_name = minio_s3_bucket.sources.bucket
  object_name = "sellers_dataset.csv"
  content_type = "text/csv"
  source = "../source_data/olist_sellers_dataset.csv"
}

resource "minio_s3_object" "product-category-name-translation" {
  depends_on = [minio_s3_bucket.sources]
  bucket_name = minio_s3_bucket.sources.bucket
  object_name = "product_category_name_translation.csv"
  content_type = "text/csv"
  source = "../source_data/product_category_name_translation.csv"
}