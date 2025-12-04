from sqlalchemy import create_engine, text

OPERATIONAL_DSN = "postgresql://admin:admin@postgres:5432/operation"


SQL_TRUNCATE_PUBLIC = """
DO $$
DECLARE
    t_name text;
BEGIN
    FOR t_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('TRUNCATE TABLE public.%I RESTART IDENTITY CASCADE', t_name);
    END LOOP;
END
$$ LANGUAGE plpgsql;
"""

SQL_TRUNCATE_DW = """
DO $$
DECLARE
    t_name text;
BEGIN
    FOR t_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'dw'
    LOOP
        EXECUTE format('TRUNCATE TABLE dw.%I RESTART IDENTITY CASCADE', t_name);
    END LOOP;
END
$$ LANGUAGE plpgsql;
"""


def main():
    engine = create_engine(OPERATIONAL_DSN)
    with engine.connect() as conn:
        print("🧹 Truncating all tables in schema public...")
        conn.execute(text(SQL_TRUNCATE_PUBLIC))
        print("✅ public truncated")

        print("🧹 Truncating all tables in schema dw...")
        conn.execute(text(SQL_TRUNCATE_DW))
        print("✅ dw truncated")

        conn.commit()


if __name__ == "__main__":
    main()
