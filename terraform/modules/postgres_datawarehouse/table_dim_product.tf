resource "postgresql_script" "dim_product" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dw.dim_product cascade;
    EOT
    ,
    <<-EOT
        CREATE TABLE dw.dim_product (
        product_id VARCHAR(50) PRIMARY KEY,  -- Correction : VARCHAR pour matcher Olist
        product_category VARCHAR(255),       -- Ajout d'une taille max conseillée
        name_length INTEGER,
        description_length INTEGER,
        photos_qty INTEGER,
        weight_g INTEGER,
        length_cm INTEGER,
        height_cm INTEGER,
        width_cm INTEGER,
        valid_from TIMESTAMP NOT NULL,
        valid_to TIMESTAMP,
        is_current BOOLEAN NOT NULL,
        rowhash VARCHAR(64) NOT NULL,
        
        CONSTRAINT chk_product_name_length CHECK (name_length IS NULL OR name_length >= 0),
        CONSTRAINT chk_product_description_length CHECK (description_length IS NULL OR description_length >= 0),
        CONSTRAINT chk_product_photos_qty CHECK (photos_qty IS NULL OR photos_qty >= 0),
        CONSTRAINT chk_product_weight_g CHECK (weight_g IS NULL OR weight_g >= 0),
        CONSTRAINT chk_product_length_cm CHECK (length_cm IS NULL OR length_cm >= 0),
        CONSTRAINT chk_product_height_cm CHECK (height_cm IS NULL OR height_cm >= 0),
        CONSTRAINT chk_product_width_cm CHECK (width_cm IS NULL OR width_cm >= 0) -- Correction : Pas de virgule ici !
);
    EOT
  ]

  depends_on = [ postgresql_schema.dw ]
}