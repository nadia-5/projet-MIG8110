resource "postgresql_script" "order_payment" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_payment;
    EOT
    ,
    <<-EOT
    create table order_payment (
    order_id varchar(255) not null ,
    payment_seq integer not null,
    order_item_id integer,
    payment_type_id integer,
    installments integer,
    value decimal(19,2) not null,
    foreign key (order_id) references orders(order_id),
    foreign key (payment_type_id) references payment_type(payment_type_id),
    constraint pk_order_payment primary key (order_id, payment_seq),
    constraint chk_installments_nonneg check (installments is null or installments >= 0),
    constraint chk_payment_value_nonneg check (value >= 0)
);

    EOT
  ]
    depends_on = [ postgresql_script.order, postgresql_script.payment_type ]
}