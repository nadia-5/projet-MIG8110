resource "postgresql_script" "review" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS review cascade;
    EOT
    ,
    <<-EOT
create table review (
    review_id uuid primary key,
    creation_date timestamp not null,
    answer_date timestamp, 
    inserted_at timestamp not null
);
    EOT
  ]
    depends_on = [ postgresql_script.customer ]
}
