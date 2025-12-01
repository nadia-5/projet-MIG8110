terraform {
  required_providers {
    postgresql = {
      source  = "doctolib/postgresql"
    }
  }
  required_version = ">= 1.3.0"
}

resource "postgresql_schema" "dw" {
  name  = "dw"
  owner = var.db_admin_user
}