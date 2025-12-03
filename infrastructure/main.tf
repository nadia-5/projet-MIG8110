module "postgres_operations" {
    source = "./modules/postgres_operations"
    providers = {
      postgresql = postgresql.pg_ops
    }
}

module "postgres_datawarehouse" {
    source = "./modules/postgres_datawarehouse"
    providers = {
      postgresql = postgresql.pg_dw
    }
}

module "minio_objects" {
    source = "./modules/minio"
    providers = {
      minio = minio.minio_provider
    }
}

