resource "postgresql_script" "dim_seller" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS dw.dim_seller cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE dw.dim_seller (
        seller_id VARCHAR(50) PRIMARY KEY,
        seller_state char(2),
        seller_city varchar(64),
        seller_zip_code varchar(16),
        valid_from timestamp not null,
        valid_to timestamp,
        is_current boolean not null,
        rowhash varchar(64) not null
    );
    EOT
  ]

  depends_on = [ postgresql_schema.dw ]
}