terraform {
  required_providers {
    
    minio = {
      source  = "aminueza/minio"
      version = "3.11.3"
    }

    postgresql = {
      source  = "doctolib/postgresql"
      version = "2.26.0-beta1"
    }
  }
}

provider "minio" {
  alias           = "minio_provider"
  minio_server    = "minio:9000"
  minio_user      =  var.MINIO_ACCESS_KEY
  minio_password  =  var.MINIO_SECRET_KEY
  minio_ssl       = false
}

provider "postgresql" {
  alias   = "pg_ops"
  database        = var.POSTGRES_DATABASE
  host            = var.POSTGRES_HOST
  port            = var.POSTGRES_PORT
  username        = var.POSTGRES_USER
  password        = var.POSTGRES_PASSWORD
  sslmode         = "disable"
  connect_timeout = 15
}

provider "postgresql" {
  alias   = "pg_dw"
  database        = var.POSTGRES_DW_DATABASE
  host            = var.POSTGRES_DW_HOST
  port            = var.POSTGRES_DW_PORT
  username        = var.POSTGRES_DW_USER
  password        = var.POSTGRES_DW_PASSWORD
  sslmode         = "disable"
  connect_timeout = 15
}

