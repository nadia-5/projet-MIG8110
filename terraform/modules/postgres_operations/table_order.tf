resource "postgresql_script" "order" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS orders cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE orders (
    order_id uuid primary key,
    customer_id uuid NOT NULL,
    status_id integer NOT NULL,
    purchase_date timestamp NOT NULL,
    estimated_delivery_date timestamp NOT NULL,
    approved_date timestamp,
    delivered_carrier_date timestamp,
    delivered_customer_date timestamp,
    inserted_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp,
    foreign key (customer_id) references customer(customer_id),
    foreign key (status_id) references order_status_type(order_status_type_id)
);
    EOT
  ,    <<-EOT
    -- Attachement du trigger
    DROP TRiGGER IF EXISTS update_order_modtime ON orders;
    CREATE TRIGGER update_order_modtime
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    EOT
  ]
  depends_on = [ postgresql_script.customer, postgresql_script.order_status_type, postgresql_script.trigger_function ]
}