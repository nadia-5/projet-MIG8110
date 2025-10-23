resource "postgresql_script" "order_review" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_review;
    EOT
    ,
    <<-EOT
create table order_review (
    review_id varchar(255) primary key,
    order_id varchar(255) not null ,
    score integer not null,
    creation_date timestamp,
    foreign key (order_id) references orders(order_id),
    constraint chk_review_score_range check (score between 1 and 5)
);
    EOT
  ]
    depends_on = [ postgresql_script.order ]
}
