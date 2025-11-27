resource "postgresql_table" "dim_product_seller_price" {
  name   = "dim_product_seller_price"
  schema = var.datawarehouse_schema

  owner = var.db_user

  depends_on = [
    postgresql_schema.datawarehouse
  ]

  column {
    name = "price_key"
    type = "BIGSERIAL"
  }

  column {
    name = "product_id"
    type = "VARCHAR(50)"
  }

  column {
    name = "seller_id"
    type = "VARCHAR(50)"
  }

  column {
    name = "price"
    type = "DECIMAL(10,2)"
  }

  column {
    name = "freight_value"
    type = "DECIMAL(10,2)"
  }

  column {
    name = "created_at"
    type = "TIMESTAMP"
    default = "CURRENT_TIMESTAMP"
  }

  primary_key {
    columns = ["price_key"]
  }
}
