resource "minio_user" "analytics_user" {
  access_key    = "analytics_user"
  secret_key    = "analytics_user_password"
  policies      = ["analytics_policy"]
}
resource "minio_user" "etl_user" {
  access_key    = "etl_user"
  secret_key    = "etl_user_password"
  policies      = ["etl_policy"]
}