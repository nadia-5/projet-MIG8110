resource "postgresql_script" "order_step" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_step;
    EOT
    ,
    <<-EOT
create table order_step (
    order_step_id serial primary key,
    order_id varchar(255) not null references order(order_id),
    order_status_type_id integer references order_status_type(order_status_type_id),
    creation_date timestamp,
    comment varchar(255)
);
    EOT
  ]
    depends_on = [ postgresql_script.order, postgresql_script.order_status_type ]
}
