resource "postgresql_script" "origin" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS origin;
    EOT
    ,
    <<-EOT
    CREATE TABLE origin (
    origin_id serial primary key,
    origin_code varchar(255) unique not null,
    origin_description varchar(255),
    constraint chk_origin_code_lower check (origin_code = lower(origin_code))
);
    EOT
  ]
}