resource "postgresql_script" "order_payment" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_payment cascade;
    EOT
    ,
    <<-EOT
    create table order_payment (
    order_id uuid not null ,
    payment_seq integer not null,
    payment_type_id integer,
    installments integer,
    value decimal(19,2) not null,
    inserted_at timestamp not null default CURRENT_TIMESTAMP,
    updated_at timestamp,
    foreign key (order_id) references orders(order_id),
    foreign key (payment_type_id) references payment_type(payment_type_id),
    constraint pk_order_payment primary key (order_id, payment_seq),
    constraint chk_installments_nonneg check (installments is null or installments >= 0),
    constraint chk_payment_value_nonneg check (value >= 0)
);

    EOT
  ,    <<-EOT
    -- Attachement du trigger
    DROP TRiGGER IF EXISTS update_order_item_modtime ON order_item;
    CREATE TRIGGER update_order_payment_modtime
    BEFORE UPDATE ON order_payment
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    EOT
  ]
    depends_on = [ postgresql_script.order, postgresql_script.payment_type, postgresql_script.trigger_function ]
}