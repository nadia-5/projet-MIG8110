resource "postgresql_script" "dim_product" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_product cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dim_product (
        product_sk SERIAL PRIMARY KEY,
        product_id VARCHAR(50) NOT NULL,
        product_category VARCHAR(255),
        name_length INTEGER,
        description_length INTEGER,
        photos_qty INTEGER,
        weight_g INTEGER,
        length_cm INTEGER,
        height_cm INTEGER,
        width_cm INTEGER,
        valid_from TIMESTAMP NOT NULL,
        valid_to TIMESTAMP,
        is_current BOOLEAN NOT NULL DEFAULT TRUE,
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rowhash VARCHAR(64) NOT NULL,
        
        CONSTRAINT chk_product_name_length CHECK (name_length IS NULL OR name_length >= 0),
        CONSTRAINT chk_product_description_length CHECK (description_length IS NULL OR description_length >= 0),
        CONSTRAINT chk_product_photos_qty CHECK (photos_qty IS NULL OR photos_qty >= 0),
        CONSTRAINT chk_product_weight_g CHECK (weight_g IS NULL OR weight_g >= 0),
        CONSTRAINT chk_product_length_cm CHECK (length_cm IS NULL OR length_cm >= 0),
        CONSTRAINT chk_product_height_cm CHECK (height_cm IS NULL OR height_cm >= 0),
        CONSTRAINT chk_product_width_cm CHECK (width_cm IS NULL OR width_cm >= 0)
    );
    CREATE INDEX idx_dim_product_id ON dim_product(product_id);
    CREATE INDEX idx_dim_product_current ON dim_product(product_id) WHERE is_current = TRUE;
    EOT
  ]
}