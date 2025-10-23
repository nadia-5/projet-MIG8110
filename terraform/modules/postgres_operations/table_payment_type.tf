resource "postgresql_script" "payment_type" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS payment_type;
    EOT
    ,
    <<-EOT
    CREATE TABLE payment_type (
    payment_type_id serial primary key,
    payment_type_code varchar(255) unique not null,
    payment_type_description varchar(255),
    constraint chk_payment_type_code_lower check (payment_type_code = lower(payment_type_code))
    );
    EOT
  ]
  depends_on = [ postgresql_script.order_status_type ]
}