resource "postgresql_script" "fact_orders" {

  commands = [
    <<-EOT
    DROP TABLE IF EXISTS fact_orders CASCADE;
    EOT
    ,
    <<-EOT
    CREATE TABLE fact_orders (
        fact_order_id SERIAL PRIMARY KEY,
        order_id VARCHAR(50) NOT NULL,
        customer_sk INTEGER NOT NULL,    
        product_sk INTEGER NOT NULL,     
        seller_sk INTEGER NOT NULL,         
        order_status_sk INTEGER,             
        date_id INTEGER,                     
        location_sk INTEGER,                 
        price DECIMAL(10,2),
        freight_value DECIMAL(10,2),
        quantity INTEGER DEFAULT 1,
        total_item_price DECIMAL(10,2),
        total_freight DECIMAL(10,2),        
        purchase_date TIMESTAMP,
        approved_date TIMESTAMP,
        delivered_carrier_date TIMESTAMP,
        delivered_customer_date TIMESTAMP,
        estimated_delivery_date TIMESTAMP,
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rowhash VARCHAR(64) NOT NULL,
        
        CONSTRAINT fk_fact_customer FOREIGN KEY (customer_sk) REFERENCES dim_customer(customer_sk),
        CONSTRAINT fk_fact_product FOREIGN KEY (product_sk) REFERENCES dim_product(product_sk),
        CONSTRAINT fk_fact_seller FOREIGN KEY (seller_sk) REFERENCES dim_seller(seller_sk),
        CONSTRAINT fk_fact_location FOREIGN KEY (location_sk) REFERENCES dim_location(location_sk),
        CONSTRAINT fk_fact_status FOREIGN KEY (order_status_sk) REFERENCES dim_order_status_type(order_status_sk)
    );
    CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_sk);
    CREATE INDEX idx_fact_orders_product ON fact_orders(product_sk);
    CREATE INDEX idx_fact_orders_seller ON fact_orders(seller_sk);
    CREATE INDEX idx_fact_orders_date ON fact_orders(date_id);
    EOT
  ]
  
  depends_on = [
    postgresql_script.dim_product,
    postgresql_script.dim_seller,
    postgresql_script.dim_order_status_type,
    postgresql_script.dim_customer,
    postgresql_script.dim_location
  ]
}