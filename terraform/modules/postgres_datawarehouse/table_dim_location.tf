resource "postgresql_script" "dim_location" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dw.dim_location cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dw.dim_location (
        location_id integer PRIMARY KEY,
        zip_code_prefix VARCHAR(20) NOT NULL,
        city VARCHAR(50) NOT NULL,
        state VARCHAR(50) NOT NULL,
        inserted_at timestamp NOT NULL,
        updated_at timestamp NOT NULL,
        rowhash varchar(64) not null,
        constraint chk_city_lower check (city = lower(city)),
        constraint chk_state_lower check (state = lower(state)),
        constraint uq_dim_location_zip_code_prefix_city_state unique (zip_code_prefix, city, state)
    );
    EOT
  ]
}