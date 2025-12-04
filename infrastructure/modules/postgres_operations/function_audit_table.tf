resource "postgresql_function" "if_modified_func" {
  name     = "if_modified_func"
  schema   = "audit"
  returns  = "trigger"
  language = "plpgsql"
  security_definer = true

  body = <<-EOF
    DECLARE
        audit_row audit.logged_actions;
        include_values boolean;
        log_diffs boolean;
        h_old hstore;
        h_new hstore;
        excluded_cols text[] = ARRAY[]::text[];
    BEGIN
        IF TG_WHEN <> 'AFTER' THEN
            RAISE EXCEPTION 'audit.if_modified_func() may only run as an AFTER trigger';
        END IF;

        audit_row = ROW(
            nextval('audit.logged_actions_event_id_seq'),
            TG_TABLE_SCHEMA::text,
            TG_TABLE_NAME::text,
            TG_RELID,
            session_user::text,
            current_timestamp,
            statement_timestamp(),
            txid_current(),
            current_setting('application_name'),
            inet_client_addr(),
            inet_client_port(),
            current_query(),
            substring(TG_OP,1,1),
            NULL, NULL,
            'f'
        );

        IF (TG_OP = 'UPDATE' AND TG_LEVEL = 'ROW') THEN
            audit_row.row_data = to_jsonb(OLD);
            audit_row.changed_fields = to_jsonb(NEW) - to_jsonb(OLD);
        ELSIF (TG_OP = 'DELETE' AND TG_LEVEL = 'ROW') THEN
            audit_row.row_data = to_jsonb(OLD);
        ELSIF (TG_OP = 'INSERT' AND TG_LEVEL = 'ROW') THEN
            audit_row.row_data = to_jsonb(NEW);
        END IF;

        INSERT INTO audit.logged_actions VALUES (audit_row.*);
        RETURN NULL;
    END;
  EOF

  depends_on = [ postgresql_schema.audit, postgresql_extension.hstore, postgresql_script.logged_actions]
}


resource "postgresql_function" "audit_table" {
  name     = "audit_table"
  schema   = "audit"
  returns  = "void"
  language = "plpgsql"

  body = <<-EOF
    BEGIN
        EXECUTE 'CREATE TRIGGER audit_trigger_row
                 AFTER INSERT OR UPDATE OR DELETE ON ' || target_table ||
                 ' FOR EACH ROW EXECUTE PROCEDURE audit.if_modified_func();';
    END;
  EOF

  arg {
    name = "target_table"
    type = "regclass"
  }

  depends_on = [ postgresql_function.if_modified_func ]
}
