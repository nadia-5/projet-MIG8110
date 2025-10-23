resource "postgresql_script" "order_item" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_item;
    EOT
    ,
    <<-EOT
    create table order_item (
    order_id varchar(255) not null references order(order_id),
    item_id integer not null,
    product_id varchar(255) not null references product(product_id),
    seller_id varchar(255) not null references seller(seller_id),
    shipping_limit_date timestamp,
    price decimal(19,2) not null,
    freight_value decimal(19,2) not null,
    constraint pk_order_item primary key (order_id, item_id),
    constraint chk_order_item_price_nonneg check (price >= 0),
    constraint chk_order_item_freight_nonneg check (freight_value >= 0)
);
    EOT
  ]
    depends_on = [ postgresql_script.order, postgresql_script.product, postgresql_script.seller ]
}
