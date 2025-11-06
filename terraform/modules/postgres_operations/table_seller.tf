resource "postgresql_script" "seller" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS seller cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE seller (
        seller_id integer PRIMARY KEY,
        location_id integer NOT NULL,
        FOREIGN KEY (location_id) REFERENCES location(location_id)
    );
    EOT
  ]
  depends_on = [ postgresql_script.location ]
}