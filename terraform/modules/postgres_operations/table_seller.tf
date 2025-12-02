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
        inserted_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at timestamp
    );
    EOT
  ,    <<-EOT
    -- Attachement du trigger
    DROP TRiGGER IF EXISTS update_seller_modtime ON seller;
    CREATE TRIGGER update_seller_modtime
    BEFORE UPDATE ON seller
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    EOT
  ]
  depends_on = [ postgresql_script.trigger_function ]
}