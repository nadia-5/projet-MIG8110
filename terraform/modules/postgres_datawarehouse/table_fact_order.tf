resource "postgresql_script" "fact_orders" {

  commands = [
    <<-EOT
    DROP TABLE IF EXISTS dw.fact_orders CASCADE;
    EOT
    ,
    <<-EOT
    CREATE TABLE dw.fact_orders (
        fact_order_id SERIAL PRIMARY KEY,
        order_id VARCHAR(50) NOT NULL,
        order_item_id INTEGER NOT NULL,
        customer_id VARCHAR(50) NOT NULL,    
        product_id VARCHAR(50) NOT NULL,     
        seller_id VARCHAR(50) NOT NULL,         
        order_status_id INTEGER,             
        date_id INTEGER,                     
        location_id INTEGER,                 
        price DECIMAL(10,2),
        freight_value DECIMAL(10,2),         
        num_items INTEGER DEFAULT 1,        
        purchase_date TIMESTAMP,
        approved_date TIMESTAMP,
        delivered_carrier_date TIMESTAMP,
        delivered_customer_date TIMESTAMP,
        estimated_delivery_date TIMESTAMP,
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_fact_product FOREIGN KEY (product_id) REFERENCES dw.dim_product(product_id),
        CONSTRAINT fk_fact_seller FOREIGN KEY (seller_id) REFERENCES dw.dim_seller(seller_id),
        CONSTRAINT fk_fact_status FOREIGN KEY (order_status_id) REFERENCES dw.dim_order_status_type(order_status_type_id)
    );
    EOT
  ]
  
  depends_on = [
    postgresql_script.dim_product,
    postgresql_script.dim_seller,
    postgresql_script.dim_order_status_type,
    postgresql_script.dim_customer, 
    
    postgresql_schema.dw
  ]
}