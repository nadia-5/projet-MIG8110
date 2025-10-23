variable "minio_user" {
    type    = string
    description = "MinIO root user"
}

variable "minio_password" {
    type    = string
    description = "MinIO root password"
}

variable "db_host" {
    type    = string
    description = "PostgreSQL database host"
    default = "postgres_operations"
}
variable "db_port" {
    type    = number
    description = "PostgreSQL database port"
    default = 5432
}

variable "db_admin_user" {
    type    = string
    description = "PostgreSQL database admin user"
    default = "admin"
}

variable "db_admin_password" {
    type    = string
    description = "PostgreSQL database admin password"
    default = "admin"
}