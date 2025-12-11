resource "postgresql_script" "dim_product_seller_price" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_product_seller_price cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dim_product_seller_price (
        price_sk SERIAL PRIMARY KEY,
        product_id VARCHAR(50) NOT NULL,
        seller_id VARCHAR(50) NOT NULL,
        price DECIMAL(10,2),
        valid_from TIMESTAMP NOT NULL,
        valid_to TIMESTAMP,
        is_current BOOLEAN NOT NULL DEFAULT TRUE,
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rowhash VARCHAR(64) NOT NULL
    );
    CREATE INDEX idx_dim_price_product ON dim_product_seller_price(product_id);
    CREATE INDEX idx_dim_price_seller ON dim_product_seller_price(seller_id);
    CREATE INDEX idx_dim_price_current ON dim_product_seller_price(product_id, seller_id) WHERE is_current = TRUE;
    EOT
  ]
}
