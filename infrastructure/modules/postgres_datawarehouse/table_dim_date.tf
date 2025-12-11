resource "postgresql_script" "dim_date" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_date cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dim_date (
        date_sk INTEGER PRIMARY KEY,
        date_value DATE NOT NULL,
        year INTEGER NOT NULL,
        quarter INTEGER NOT NULL,
        month INTEGER NOT NULL,
        day INTEGER NOT NULL,
        week_of_year INTEGER NOT NULL,
        day_of_week INTEGER NOT NULL,
        is_weekend BOOLEAN NOT NULL,
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rowhash VARCHAR(64) NOT NULL
    );
    CREATE INDEX idx_dim_date_value ON dim_date(date_value);
    EOT
  ]
}