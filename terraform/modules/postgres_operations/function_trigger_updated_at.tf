resource "postgresql_script" "trigger_function" {
  commands = [
    <<-EOT
    -- 1. Création de la fonction générique
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    EOT
  ]
}