resource "postgresql_script" "customer" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS customer cascade;
    EOT
    ,
    <<-EOT
    CREATE TABLE customer (
        customer_id uuid primary key,
        customer_code uuid NOT NULL,       -- ⬅️ CHANGE: varchar(32) -> uuid
        customer_state char(2),
        customer_city varchar(64),
        customer_zip_code varchar(16),
        inserted_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at timestamp
    );
    EOT
  # ... (rest of the file remains the same)
  ,
    <<-EOT
    -- Attachement du trigger
    DROP TRIGGER IF EXISTS update_customer_modtime ON customer;
    CREATE TRIGGER update_customer_modtime
    BEFORE UPDATE ON customer
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    EOT
  ]
  depends_on = [ postgresql_script.trigger_function ]
}