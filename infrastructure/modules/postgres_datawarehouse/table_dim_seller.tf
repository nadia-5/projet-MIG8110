resource "postgresql_script" "dim_seller" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_seller cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dim_seller (
        seller_sk SERIAL PRIMARY KEY,
        seller_id VARCHAR(50) NOT NULL,
        seller_state CHAR(2),
        seller_city VARCHAR(64),
        seller_zip_code VARCHAR(16),
        valid_from TIMESTAMP NOT NULL,
        valid_to TIMESTAMP,
        is_current BOOLEAN NOT NULL DEFAULT TRUE,
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rowhash VARCHAR(64) NOT NULL
    );
    CREATE INDEX idx_dim_seller_id ON dim_seller(seller_id);
    CREATE INDEX idx_dim_seller_current ON dim_seller(seller_id) WHERE is_current = TRUE;
    EOT
  ]
}