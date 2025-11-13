resource "postgresql_script" "location" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS location cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE location (
        location_id integer PRIMARY KEY,
        zip_code_prefix VARCHAR(20) NOT NULL,
        city VARCHAR(50) NOT NULL,
        state VARCHAR(50) NOT NULL,
        constraint chk_city_lower check (city = lower(city)),
        constraint chk_state_lower check (state = lower(state)),
        constraint unique_key unique (zip_code_prefix, city, state)
    );
    EOT
  ]
}