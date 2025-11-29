resource "postgresql_script" "product_seller" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS product_seller cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE product_seller (
    product_id uuid primary key,
    seller_id uuid NOT NULL,
    price decimal(19,2) NOT NULL,
    inserted_at timestamp NOT NULL
);
    EOT
  ]
  depends_on = [ postgresql_script.product, postgresql_script.seller ]
}

