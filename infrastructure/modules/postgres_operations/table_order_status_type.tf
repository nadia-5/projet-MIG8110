resource "postgresql_script" "order_status_type" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_status_type cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE order_status_type (
    order_status_type_id integer primary key,
    order_status_type_code varchar(255) unique not null,
    order_status_type_description varchar(255),
    inserted_at timestamp not null,
    constraint chk_order_status_type_code_lower check (order_status_type_code = lower(order_status_type_code))
    );
    EOT
    ,
        <<-EOT
    SELECT audit.audit_table('public.order_status_type');
    EOT
  ]
    depends_on = [ postgresql_function.audit_table ]
}