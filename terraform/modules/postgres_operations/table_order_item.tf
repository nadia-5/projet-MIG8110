resource "postgresql_script" "order_item" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_item;
    EOT
    ,
    <<-EOT
    create table order_item (
    order_id varchar(255) not null,
    item_id integer not null,
    product_id varchar(255) not null,
    seller_id integer not null,
    shipping_limit_date timestamp,
    price decimal(19,2) not null,
    freight_value decimal(19,2) not null,
    foreign key (order_id) references orders(order_id),
    foreign key (product_id) references product(product_id),
    foreign key (seller_id) references seller(seller_id),
    constraint pk_order_item primary key (order_id, item_id),
    constraint chk_order_item_price_nonneg check (price >= 0),
    constraint chk_order_item_freight_nonneg check (freight_value >= 0)
);
    EOT
  ]
    depends_on = [ postgresql_script.order, postgresql_script.product, postgresql_script.seller ]
}
