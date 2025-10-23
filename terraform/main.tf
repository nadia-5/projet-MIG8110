terraform {
  required_providers {
    
    minio = {
      source  = "refaktory/minio"
      version = "0.1.0" 
    }

    postgresql = {
      source  = "doctolib/postgresql"
      version = "2.26.0-beta1"
    }
  }
  required_version = ">= 1.3.0"
}

provider "minio" {
  alias    = "minio_provider"
  endpoint      = "minio:9000"
  access_key    =  var.minio_user
  secret_key    =  var.minio_password
  ssl           = false
}

provider "postgresql" {
  alias   = "pgcore"
  database        = "operation"
  host            = var.db_host
  port            = var.db_port
  username        = var.db_admin_user
  password        = var.db_admin_password
  sslmode         = "disable"
  connect_timeout = 15
}

module "minio_objects" {
    source = "./modules/minio"
    minio_root_password = var.minio_password
    minio_root_user     = var.minio_user
    providers = {
      minio = minio.minio_provider
    }
}

module "postgres_operations" {
    source = "./modules/postgres_operations"
    providers = {
      postgresql = postgresql.pgcore
    }
}