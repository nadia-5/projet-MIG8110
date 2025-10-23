resource "postgresql_script" "lead_type" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS lead_type;
    EOT
    ,
    <<-EOT
    CREATE TABLE lead_type (
        lead_type_id integer PRIMARY KEY,
        lead_type_code VARCHAR(255) NOT NULL,
        lead_type_description TEXT,
        constraint chk_lead_type_code_lower check (lead_type_code = lower(lead_type_code))
    );
    EOT
  ]
}