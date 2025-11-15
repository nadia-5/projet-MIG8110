resource "postgresql_script" "customer" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS customer cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE customer (
        customer_id uuid PRIMARY KEY,
        customer_code varchar(32) NOT NULL,
        customer_state char(2),
        customer_city varchar(64),
        customer_zip_code varchar(16),
        created_at timestamp NOT NULL
    );
    EOT
  ]
}