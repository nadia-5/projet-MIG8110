resource "postgresql_schema" "my_schema" {
    name  = "dw"
    database = "datawarehouse"

    depends_on = [postgresql_database.datawarehouse]
}
