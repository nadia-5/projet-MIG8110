resource "postgresql_extension" "hstore" {
  name = "hstore"
  schema = "public"
}