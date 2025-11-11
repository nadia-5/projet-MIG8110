resource "postgresql_script" "order_step" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_step cascade;
    EOT
    ,
    <<-EOT
create table order_step (
    order_step_id serial primary key,
    order_id varchar(255) not null ,
    order_status_type_id integer not null,
    creation_date timestamp,
    comment varchar(255),
    foreign key (order_id) references orders(order_id),
    foreign key (order_status_type_id) references order_status_type(order_status_type_id)
);
    EOT
  ]
    depends_on = [ postgresql_script.order, postgresql_script.order_status_type ]
}
