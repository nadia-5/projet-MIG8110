resource "postgresql_script" "view_orders_dataset" {
  commands = [
    <<-EOT
    DROP VIEW IF EXISTS view_orders_dataset;
    EOT
    ,
    <<-EOT
    CREATE VIEW view_orders_dataset AS
    SELECT 
        f.order_id,
        f.customer_sk,
        f.product_sk,
        f.seller_sk,
        dp.product_category,
        ds.seller_city,
        ds.seller_state,
        dc.customer_city,
        dc.customer_state,
        -- Financials
        SUM(f.quantity) as quantity,
        SUM(f.total_item_price) as total_revenue,
        SUM(f.total_freight) as total_freight,
        -- Timestamps (Accumulating Snapshot Logic: Get the latest known state)
        MAX(f.purchase_date) as purchase_date,
        MAX(f.approved_date) as approved_date,
        MAX(f.delivered_carrier_date) as delivered_carrier_date,
        MAX(f.delivered_customer_date) as delivered_customer_date,
        MAX(f.estimated_delivery_date) as estimated_delivery_date,
        -- Logistics KPIs (Derived)
        (MAX(f.approved_date) - MAX(f.purchase_date)) as days_to_approve,
        (MAX(f.delivered_carrier_date) - MAX(f.approved_date)) as days_to_carrier,
        (MAX(f.delivered_customer_date) - MAX(f.delivered_carrier_date)) as days_transit,
        (MAX(f.delivered_customer_date) - MAX(f.purchase_date)) as days_total_delivery,
        (MAX(f.estimated_delivery_date) - MAX(f.delivered_customer_date)) as days_estimated_error,
        CASE 
            WHEN MAX(f.delivered_customer_date) > MAX(f.estimated_delivery_date) THEN TRUE 
            ELSE FALSE 
        END as is_late
    FROM fact_orders f
    JOIN dim_product dp ON f.product_sk = dp.product_sk
    JOIN dim_seller ds ON f.seller_sk = ds.seller_sk
    JOIN dim_customer dc ON f.customer_sk = dc.customer_sk
    GROUP BY 
        f.order_id, 
        f.customer_sk, 
        f.product_sk, 
        f.seller_sk,
        dp.product_category,
        ds.seller_city,
        ds.seller_state,
        dc.customer_city,
        dc.customer_state;
    EOT
  ]

  depends_on = [
    postgresql_script.fact_orders,
    postgresql_script.dim_product,
    postgresql_script.dim_seller,
    postgresql_script.dim_customer
  ]
}
