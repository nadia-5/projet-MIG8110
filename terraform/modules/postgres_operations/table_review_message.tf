resource "postgresql_script" "review_message" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS review_message;
    EOT
    ,
    <<-EOT

create table review_message (
    review_message_id serial primary key,
    review_id varchar(255) not null references order_review(review_id),
    sender_role varchar(255),
    message varchar(255),
    creation_date timestamp
);
    EOT
  ]
    depends_on = [ postgresql_script.order_review ]
}
