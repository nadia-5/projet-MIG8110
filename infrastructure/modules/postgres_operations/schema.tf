resource "postgresql_schema" "audit" {
  name  = "audit"
  if_not_exists = true
  drop_cascade = true
}