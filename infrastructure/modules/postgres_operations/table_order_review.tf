resource "postgresql_script" "order_review" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS order_review cascade;
    EOT
    ,
    <<-EOT
create table order_review (
    review_id uuid not null,
    order_id uuid not null ,
    score integer not null,
    title varchar(255),
    message text,
    inserted_at timestamp not null,
    foreign key (order_id) references orders(order_id),
    foreign key (review_id) references review(review_id),
    constraint chk_review_score_range check (score between 1 and 5),
    constraint primary_key PRIMARY KEY (review_id, order_id)
);
    EOT
    ,
        <<-EOT
    SELECT audit.audit_table('public.order_review');
    EOT
  ]
    depends_on = [ postgresql_script.order, postgresql_script.review, postgresql_function.audit_table ]
}
