resource "postgresql_script" "logged_actions" {
commands = [
    <<-EOT
    DROP TABLE IF EXISTS audit.logged_actions cascade;
    EOT
    ,
    <<-EOT
CREATE TABLE audit.logged_actions (
    event_id bigserial primary key,
    schema_name text not null,
    table_name text not null,
    relid oid not null,
    session_user_name text,
    action_tstamp_tx TIMESTAMP WITH TIME ZONE NOT NULL,
    action_tstamp_stm TIMESTAMP WITH TIME ZONE NOT NULL,
    transaction_id bigint,
    application_name text,
    client_addr inet,
    client_port integer,
    client_query text,
    action TEXT NOT NULL CHECK (action IN ('I','D','U', 'T')),
    row_data jsonb,
    changed_fields jsonb,
    statement_only boolean not null
);
    EOT
    ,
    <<-EOT
    CREATE INDEX logged_actions_relid_idx ON audit.logged_actions(relid);
    CREATE INDEX logged_actions_action_tstamp_tx_idx ON audit.logged_actions(action_tstamp_tx);
    EOT
  ]
    depends_on = [ postgresql_schema.audit ]
}