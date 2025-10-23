resource "postgresql_script" "origin" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS origin;
    EOT
    ,
    <<-EOT
    CREATE TABLE origin (
        origin_id integer PRIMARY KEY,
        origin_code VARCHAR(50) NOT NULL,
        origin_description TEXT
    );
    EOT
  ]
}