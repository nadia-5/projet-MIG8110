resource "postgresql_script" "order_status_type" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_status_type;
    EOT
    ,
    <<-EOT
    CREATE TABLE order_status_type (
        id SERIAL PRIMARY KEY,
        status_name VARCHAR(50) NOT NULL,
        description TEXT
    );
    EOT
  ]
}