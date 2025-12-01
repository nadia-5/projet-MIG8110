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
        
        -- La clé primaire est le couple (Produit + Vendeur)
        PRIMARY KEY (product_id, seller_id),
        
        -- Clés étrangères (Optionnel mais recommandé pour l'intégrité)
        FOREIGN KEY (product_id) REFERENCES product(product_id),
        FOREIGN KEY (seller_id) REFERENCES seller(seller_id)
    );
    EOT
  ]
  depends_on = [ postgresql_script.product, postgresql_script.seller ]
}