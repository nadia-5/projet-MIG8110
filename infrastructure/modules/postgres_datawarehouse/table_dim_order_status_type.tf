resource "postgresql_script" "dim_order_status_type" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_order_status_type cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dim_order_status_type (
        order_status_sk SERIAL PRIMARY KEY,
        order_status_type_code VARCHAR(255) UNIQUE NOT NULL,
        order_status_type_description VARCHAR(255),
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rowhash VARCHAR(64) NOT NULL,
        CONSTRAINT chk_order_status_type_code_lower CHECK (order_status_type_code = lower(order_status_type_code))
    );
    EOT
  ]
}