resource "minio_s3_bucket" "sources" {
  bucket      = "sources"
  acl = "public"
}

resource "minio_s3_bucket" "raw-data" {
  bucket      = "raw-data"
  acl = "public"
}