resource "postgresql_script" "dim_customer" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dim_customer cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dim_customer (
        customer_id integer primary key,
        customer_code varchar(32) NOT NULL,
        customer_state char(2),
        customer_city varchar(64),
        customer_zip_code varchar(16),
        valid_from timestamp not null,
        valid_to timestamp,
        is_current boolean not null,
        rowhash varchar(64) not null
    );
    EOT
  ]
}