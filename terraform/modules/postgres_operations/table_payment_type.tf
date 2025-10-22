resource "postgresql_script" "payment_type" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS payment_type;
    EOT
    ,
    <<-EOT
    CREATE TABLE payment_type (
        payment_type_id integer PRIMARY KEY,
        payment_type_code VARCHAR(50) NOT NULL,
        payment_type_description TEXT
    );
    EOT
  ]
  depends_on = [ postgresql_script.order_status_type ]
}