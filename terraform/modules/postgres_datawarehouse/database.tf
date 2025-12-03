resource "postgresql_database" "datawarehouse" {
    name              = "datawarehouse"
    connection_limit  = -1
    allow_connections = true
}