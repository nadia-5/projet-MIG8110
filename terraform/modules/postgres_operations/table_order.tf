resource "postgresql_script" "order" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS orders;
    EOT
    ,
    <<-EOT
    CREATE TABLE orders (
    order_id varchar(255) primary key,
    customer_id integer not null,
    status_id integer ,
    purchase_timestamp timestamp,
    estimated_delivery_date timestamp,
    foreign key (customer_id) references customer(customer_id),
    foreign key (status_id) references order_status_type(order_status_type_id)
);
    EOT
  ]
  depends_on = [ postgresql_script.customer, postgresql_script.order_status_type ]
}
