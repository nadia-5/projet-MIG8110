resource "postgresql_script" "product_seller" {
  commands = [
    <<-EOT
    DROP TABLE IF EXISTS product_seller CASCADE;
    EOT
    ,
    <<-EOT
    CREATE TABLE product_seller (
        product_id UUID NOT NULL,
        seller_id UUID NOT NULL,
        price DECIMAL(19,2),
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,

        PRIMARY KEY (product_id, seller_id),
        FOREIGN KEY (product_id) REFERENCES product(product_id),
        FOREIGN KEY (seller_id) REFERENCES seller(seller_id)
    );
    EOT
  ,    <<-EOT
    -- Attachement du trigger
    DROP TRiGGER IF EXISTS update_product_seller_modtime ON product_seller;
    CREATE TRIGGER update_product_seller_modtime
    BEFORE UPDATE ON product_seller
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    EOT
  ]
  depends_on = [ postgresql_script.product, postgresql_script.seller, postgresql_script.trigger_function ]
}