resource "postgresql_script" "location" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS location;
    EOT
    ,
    <<-EOT
    CREATE TABLE location (
        location_id integer PRIMARY KEY,
        city VARCHAR(50) NOT NULL,
        state VARCHAR(50) NOT NULL
    );
    EOT
  ]
}