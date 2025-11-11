resource "postgresql_script" "review_message" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS review_message cascade;
    EOT
    ,
    <<-EOT

create table review_message (
    review_message_id serial primary key,
    review_id varchar(255) not null,
    sender_role varchar(255),
    message varchar(255),
    creation_date timestamp,
    foreign key (review_id) references order_review(review_id)
);
    EOT
  ]
    depends_on = [ postgresql_script.order_review ]
}
