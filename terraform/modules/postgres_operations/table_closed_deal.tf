resource "postgresql_script" "closed_deal" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS closed_deal;
    EOT
    ,
    <<-EOT
create table closed_deal (
    mql_id varchar(255) not null references marketing_qualified_lead(mql_id),
    lead_type_id integer references lead_type(lead_type_id),
    seller_id varchar(255) not null references seller(seller_id),
    won_date integer not null,
    business_segment varchar(255),
    constraint pk_closed_deal primary key (mql_id, seller_id)
);
    EOT
  ]
   depends_on = [ postgresql_script.marketing_qualified_lead, postgresql_script.lead_type, postgresql_script.seller ]
}
