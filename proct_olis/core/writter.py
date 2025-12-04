import polars as pl
from proct_olis.core.config import Config
from proct_olis.core.session import Session
from proct_olis.settings import Settings
from abc import ABC, abstractmethod
from proct_olis.core.utilities import Utilities
from datetime import datetime
from typing import Optional, List
import sqlalchemy

class WritterBase(ABC):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, execution_date: Optional[str] = None):
        self.process_name = process_name
        self.destination = config.destination
        self.settings = settings
        self.df = df
        self.execution_date = execution_date
        self.utilities = Utilities()
        
        if execution_date:
            self.current_datetime = datetime.strptime(execution_date, "%Y-%m-%d")
        else:
            self.current_datetime = datetime.now()

    @abstractmethod
    def write(self):
        raise NotImplementedError

class S3Writter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, execution_date: Optional[str] = None):
        super().__init__(process_name, config, settings, df, execution_date)
        self.fs = Session(settings, self.destination.destination_type).s3

    def write(self) -> None:
        if self.destination.file_name.startswith("common/"):
            path_save = f"s3://{self.destination.bucket_name}/{self.destination.file_name}"
        elif self.execution_date:
            path_save = f"s3://{self.destination.bucket_name}/daily_data/{self.execution_date}/{self.destination.file_name}"
        elif hasattr(self.destination, 'date_bucket') and self.destination.date_bucket:
            date = pl.Date.strptime(pl.lit(self.destination.date_bucket), fmt="%Y-%m-%d").to_python_date()
            annee = str(date.year).zfill(4)
            mois = str(date.month).zfill(2)
            jour = str(date.day).zfill(2)
            path_save = f"s3://{self.destination.bucket_name}/{annee}/{mois}/{jour}/{self.destination.file_name}"
        else:
            path_save = f"s3://{self.destination.bucket_name}/{self.destination.file_name}"

        print(f"Writing S3: {path_save}")
        with self.fs.open(path_save, "wb") as f:
            self.df.write_parquet(f)

class tableWritter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, execution_date: Optional[str] = None):
        super().__init__(process_name, config, settings, df, execution_date)
        self.pg_conn = Session(self.settings, kind=self.destination.destination_type).pg_conn
        self.engine = sqlalchemy.create_engine(self.pg_conn)
        self.table_name = f"{self.destination.schema}.{self.destination.table}"

    def _execute_sql(self, query: str) -> None:
        """Execute raw SQL for UPDATE/DELETE operations."""
        with self.engine.connect() as conn:
            conn.execute(sqlalchemy.text(query))
            conn.commit()

    def _get_existing_data(self) -> pl.DataFrame:
        """Read existing data from destination table."""
        query = f"SELECT * FROM {self.table_name}"
        try:
            return pl.read_database_uri(query=query, uri=self.pg_conn)
        except Exception as e:
            print(f"⚠️ No existing data in {self.table_name}: {e}")
            return pl.DataFrame()

    def _table_has_column(self, column_name: str) -> bool:
        """Check if table has specific column."""
        try:
            query = f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema='{self.destination.schema}' 
                AND table_name='{self.destination.table}' 
                AND column_name='{column_name}'
            """
            result = pl.read_database_uri(query=query, uri=self.pg_conn)
            return not result.is_empty()
        except:
            return False

    def append_table(self) -> None:
        """
        Append / upsert based on business_keys.

        Behavior:
        - If no historical data -> full insert.
        - If historical exists:
          - Insert rows whose business_keys do not exist yet.
          - For rows whose business_keys exist:
            - If any non-key column changed -> UPDATE row and set updated_at.
            - If nothing changed -> do nothing.
        """
        print(f"\n📊 Writing to {self.destination.schema}.{self.destination.table}")
        print(f"📥 Incoming rows: {self.df.height}")

        query = f"SELECT * FROM {self.destination.schema}.{self.destination.table}"
        try:
            historical_df = pl.read_database_uri(query=query, uri=self.pg_conn)
        except Exception:
            historical_df = pl.DataFrame(schema=self.df.schema)

        # If no historical data: simple insert
        if historical_df.is_empty():
            print("🆕 No historical data, full insert.")
            df_to_insert = self.df

            # inserted_at for operational tables
            if self.destination.destination_type == "postgres_operational" and "inserted_at" not in df_to_insert.columns:
                df_to_insert = df_to_insert.with_columns(
                    pl.lit(self.current_datetime).alias("inserted_at")
                )

            df_to_insert.write_database(
                table_name=f"{self.destination.schema}.{self.destination.table}",
                connection=self.pg_conn,
                if_table_exists="append",
            )
            print(f"✅ Inserted {df_to_insert.height} rows.")
            return

        # There is historical data
        business_keys = self.destination.business_keys or []
        if not business_keys:
            # Fallback: no business keys -> behave like pure append, no update
            print("⚠️ No business_keys configured, pure append.")
            df_to_insert = self.df

            if self.destination.destination_type == "postgres_operational" and "inserted_at" not in df_to_insert.columns:
                df_to_insert = df_to_insert.with_columns(
                    pl.lit(self.current_datetime).alias("inserted_at")
                )

            df_to_insert.write_database(
                table_name=f"{self.destination.schema}.{self.destination.table}",
                connection=self.pg_conn,
                if_table_exists="append",
            )
            print(f"✅ Inserted {df_to_insert.height} rows (no dedupe).")
            return

        print(f"🔑 Business keys: {business_keys}")

        # Determine non-key columns to compare
        meta_cols = {"inserted_at", "updated_at"}
        compare_cols = [c for c in self.df.columns if c not in set(business_keys) | meta_cols]

        # Join incoming with historical on business_keys
        incoming = self.df
        existing = historical_df

        # Find rows that are completely new (no match on business_keys)
        new_keys = incoming.join(
            existing.select(business_keys), on=business_keys, how="anti"
        )
        new_to_insert = incoming.join(new_keys.select(business_keys), on=business_keys, how="inner")

        # Find rows whose keys exist and may need update
        potential_updates = incoming.join(
            existing, on=business_keys, how="inner", suffix="_existing"
        )

        # Detect real changes on non-key columns
        changed_keys = []
        if not potential_updates.is_empty() and compare_cols:
            change_exprs = []
            for col in compare_cols:
                change_exprs.append(
                    (pl.col(col).is_null() & pl.col(f"{col}_existing").is_not_null())
                    | (pl.col(col).is_not_null() & pl.col(f"{col}_existing").is_null())
                    | (pl.col(col) != pl.col(f"{col}_existing"))
                )

            has_changes = change_exprs[0]
            for expr in change_exprs[1:]:
                has_changes = has_changes | expr

            changed_df = potential_updates.filter(has_changes).select(business_keys)
            changed_keys = changed_df.to_dicts()
        else:
            changed_keys = []

        print(f"🆕 New rows: {new_to_insert.height}")
        print(f"♻️ Rows to update: {len(changed_keys)}")

        # 1) INSERT new rows
        if not new_to_insert.is_empty():
            to_ins = new_to_insert
            if self.destination.destination_type == "postgres_operational" and "inserted_at" not in to_ins.columns:
                to_ins = to_ins.with_columns(
                    pl.lit(self.current_datetime).alias("inserted_at")
                )

            to_ins.write_database(
                table_name=f"{self.destination.schema}.{self.destination.table}",
                connection=self.pg_conn,
                if_table_exists="append",
            )
            print(f"✅ Inserted {to_ins.height} new rows.")

        # 2) UPDATE changed rows (SCD1-style)
        if changed_keys:
            print("🔧 Applying updates on existing rows...")
            with sqlalchemy.create_engine(self.pg_conn).connect() as conn:
                for key_dict in changed_keys:
                    # Build SET clause from incoming row
                    key_filter = " AND ".join(
                        f"{k} = '{v}'" if v is not None else f"{k} IS NULL"
                        for k, v in key_dict.items()
                    )

                    # Build SET for all compare_cols + updated_at
                    set_parts = [f"updated_at = '{self.current_datetime}'"]
                    row = (
                        incoming.filter(
                            pl.all(
                                [pl.col(k) == pl.lit(v) if v is not None else pl.col(k).is_null() for k, v in key_dict.items()]
                            )
                        )
                        .to_dicts()
                    )
                    if row:
                        row = row[0]
                        for col in compare_cols:
                            val = row.get(col)
                            if val is None:
                                set_parts.append(f"{col} = NULL")
                            else:
                                set_parts.append(f"{col} = '{val}'")

                        update_sql = f"""
                            UPDATE {self.destination.schema}.{self.destination.table}
                            SET {", ".join(set_parts)}
                            WHERE {key_filter}
                        """
                        conn.execute(text(update_sql))
                conn.commit()
            print(f"✅ Updated {len(changed_keys)} existing rows.")


    def scd2_table(self) -> None:
        """SCD Type 2: Track historical changes to dimension records."""
        print(f"\n🔄 SCD2 Processing: {self.table_name}")
        
        business_keys = getattr(self.destination, 'business_keys', None)
        if not business_keys:
            raise ValueError(f"SCD2 requires business_keys in config for {self.table_name}")

        existing_df = self._get_existing_data()
        
        # Initial load
        if existing_df.is_empty():
            print(f"📥 SCD2 Initial Load: Inserting {self.df.height} records")
            self.df.write_database(
                table_name=self.table_name,
                connection=self.pg_conn,
                if_table_exists="append"
            )
            return

        current_records = existing_df.filter(pl.col("is_current") == True)
        
        # NEW records
        new_records = self.df.join(
            current_records.select(business_keys),
            on=business_keys,
            how="anti"
        )

        # Insert new records
        if not new_records.is_empty():
            new_records.write_database(
                table_name=self.table_name,
                connection=self.pg_conn,
                if_table_exists="append"
            )
        
        print(f"✅ SCD2 Complete: {new_records.height} new records")

    def write(self) -> None:
        kind = getattr(self.destination, 'kind', None)
        if kind == "append":
            self.append_table()
        elif kind == "scd2":
            self.scd2_table()
        else:
            raise ValueError(f"Unknown write kind: {kind}")

class Writter:
    def __init__(self, process_name: str, df: pl.DataFrame, config: Config, settings: Settings, execution_date: Optional[str] = None):
        self.process_name = process_name
        self.config = config
        self.settings = settings
        self.df = df
        self.execution_date = execution_date

    def write(self) -> None:
        if self.config.destination.destination_type == "s3":
            S3Writter(self.process_name, self.config, self.settings, self.df, self.execution_date).write()
        elif self.config.destination.destination_type in ["postgres_operational", "postgres_datawarehouse"]:
            tableWritter(self.process_name, self.config, self.settings, self.df, self.execution_date).write()
