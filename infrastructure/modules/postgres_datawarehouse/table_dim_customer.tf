resource "postgresql_script" "dim_customer" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_customer cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dim_customer (
        customer_sk SERIAL PRIMARY KEY,
        customer_id VARCHAR(50) NOT NULL,
        customer_code VARCHAR(32),
        customer_state CHAR(2),
        customer_city VARCHAR(64),
        customer_zip_code VARCHAR(16),
        valid_from TIMESTAMP NOT NULL,
        valid_to TIMESTAMP,
        is_current BOOLEAN NOT NULL DEFAULT TRUE,
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rowhash VARCHAR(64) NOT NULL
    );
    CREATE INDEX idx_dim_customer_id ON dim_customer(customer_id);
    CREATE INDEX idx_dim_customer_current ON dim_customer(customer_id) WHERE is_current = TRUE;
    EOT
  ]
}