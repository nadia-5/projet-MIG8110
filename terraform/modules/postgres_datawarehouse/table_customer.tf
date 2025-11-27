resource "postgresql_script" "customer" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS customer;
    EOT
    ,
    <<-EOT
    CREATE TABLE customer (
        customer_id integer PRIMARY KEY,
        location_id integer NOT NULL,
        FOREIGN KEY (location_id) REFERENCES location(location_id)
    );
    EOT
  ]
  depends_on = [ postgresql_script.location ]
}