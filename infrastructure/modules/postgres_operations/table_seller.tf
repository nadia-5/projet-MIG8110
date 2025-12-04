resource "postgresql_script" "seller" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS seller cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE seller (
        seller_id uuid PRIMARY KEY,
        seller_state char(2),
        seller_city varchar(64),
        seller_zip_code varchar(16),
        inserted_at timestamp NOT NULL
    );
    EOT
    ,
        <<-EOT
    SELECT audit.audit_table('public.seller');
    EOT
  ]
  depends_on = [ postgresql_function.audit_table ]
}