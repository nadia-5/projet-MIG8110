resource "postgresql_script" "product_category" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS product_category;
    EOT
    ,
    <<-EOT
    CREATE TABLE product_category (
        product_category_id integer PRIMARY KEY,
        product_category_code VARCHAR(50) NOT NULL,
        product_category_description TEXT
    );
    EOT
  ]
}