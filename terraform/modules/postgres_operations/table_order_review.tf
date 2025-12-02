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
    inserted_at timestamp not null default CURRENT_TIMESTAMP,
    updated_at timestamp,
    foreign key (order_id) references orders(order_id),
    foreign key (review_id) references review(review_id),
    constraint chk_review_score_range check (score between 1 and 5),
    constraint primary_key PRIMARY KEY (review_id, order_id)
);
    EOT
    ,    <<-EOT
    -- Attachement du trigger
    DROP TRiGGER IF EXISTS update_order_review_modtime ON order_review;
    CREATE TRIGGER update_order_review_modtime
    BEFORE UPDATE ON order_review
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    EOT
  ]
    depends_on = [ postgresql_script.order, postgresql_script.review, postgresql_script.trigger_function ]
}
