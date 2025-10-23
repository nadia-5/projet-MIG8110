resource "postgresql_script" "order_status_type" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_status_type;
    EOT
    ,
    <<-EOT
    CREATE TABLE order_status_type (
     order_status_type_id serial primary key,
    order_status_type_code varchar(255) unique not null,
    order_status_type_description varchar(255),
    constraint chk_order_status_type_code_lower check (order_status_type_code = lower(order_status_type_code))
    );
    EOT
  ]
}