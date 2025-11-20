resource "postgresql_script" "payment_type" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS payment_type cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE payment_type (
    payment_type_id int primary key,
    payment_type_code varchar(255) unique not null,
    payment_type_description varchar(255),
    inserted_at timestamp not null,
    constraint chk_payment_type_code_lower check (payment_type_code = lower(payment_type_code))
    );
    EOT
  ]
  depends_on = [ postgresql_script.order_status_type ]
}