resource "postgresql_script" "dim_location" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_location cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dim_location (
        location_sk SERIAL PRIMARY KEY,
        zip_code_prefix VARCHAR(20) NOT NULL,
        city VARCHAR(50) NOT NULL,
        state VARCHAR(50) NOT NULL,
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rowhash VARCHAR(64) NOT NULL,
        
        CONSTRAINT chk_city_lower CHECK (city = lower(city)),
        CONSTRAINT chk_state_lower CHECK (state = lower(state)),
        CONSTRAINT uq_location_zip_city_state UNIQUE (zip_code_prefix, city, state)
    );
    CREATE INDEX idx_dim_location_zip ON dim_location(zip_code_prefix);
    EOT
  ]
}