resource "postgresql_script" "dim_order_status_type" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dw.dim_order_status_type cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dw.dim_order_status_type (
    order_status_type_id integer primary key,
    order_status_type_code varchar(255) unique not null,
    order_status_type_description varchar(255),
    inserted_at timestamp not null,
    updated_at timestamp not null,
    rowhash varchar(64) not null,
    constraint chk_order_status_type_code_lower check (order_status_type_code = lower(order_status_type_code))
    );
    EOT
  ]
}