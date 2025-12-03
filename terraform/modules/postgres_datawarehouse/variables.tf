variable "db_admin_user" {
  type        = string
  description = "Utilisateur administrateur de la base de données"
  default     = "admin"
}

variable "db_host" {
  type    = string
  default = "postgres_operations"
}

variable "db_port" {
  type    = number
  default = 5432
}

variable "db_admin_password" {
  type    = string
  default = "admin"
}