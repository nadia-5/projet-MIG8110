resource "postgresql_script" "product_category" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS product_category cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE product_category (
    product_category_id serial primary key,
    product_category_name varchar(255) unique not null,
    product_category_description varchar(255),
    constraint chk_product_category_name_lower check (product_category_name = lower(product_category_name))
    );
    EOT
  ]
}