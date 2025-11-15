resource "postgresql_script" "seller" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS seller cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE seller (
        seller_id integer PRIMARY KEY,
        seller_state char(2),
        seller_city varchar(64),
        seller_zip_code varchar(16),
        created_at timestamp NOT NULL
    );
    EOT
  ]
}