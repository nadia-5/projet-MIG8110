resource "postgresql_script" "marketing_qualified_lead" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS marketing_qualified_lead cascade;
    EOT
    ,
    <<-EOT
create table marketing_qualified_lead (
    mql_id varchar(255) primary key,
    first_contact_date integer not null,
    landing_page_id integer,
    origin_id integer,
    foreign key (origin_id) references origin(origin_id)
);
    EOT
  ]
   depends_on = [ postgresql_script.lead_type, postgresql_script.seller ]
}
