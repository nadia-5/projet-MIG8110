resource "postgresql_script" "order" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS orders;
    EOT
    ,
    <<-EOT
    CREATE TABLE orders (
    order_id varchar(255) primary key,
    customer_id varchar(255) not null references customer(customer_id),
    status_id integer references order_status_type(order_status_type_id),
    purchase_timestamp timestamp,
    estimated_delivery_date timestamp
);
    EOT
  ]
  depends_on = [ postgresql_script.customer, postgresql_script.order_status_type ]
}
