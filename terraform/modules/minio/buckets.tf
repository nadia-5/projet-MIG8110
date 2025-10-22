resource "minio_bucket" "raw-data" {
  name      = "raw-data"
}

resource "minio_bucket" "processed-data" {
  name      = "processed-data"
}

resource "minio_bucket" "logs" {
  name      = "logs"
}