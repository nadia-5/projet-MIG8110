resource "postgresql_script" "location" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS location cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE location (
        location_id integer PRIMARY KEY,
        city VARCHAR(50) NOT NULL,
        state VARCHAR(50) NOT NULL,
        constraint chk_city_lower check (city = lower(city)),
        constraint chk_state_lower check (state = lower(state))
    );
    EOT
  ]
}