import polars as pl
from proct_olis.core.config import Config
from proct_olis.core.session import Session
from proct_olis.settings import Settings
from abc import ABC, abstractmethod
from proct_olis.core.utilities import Utilities
from datetime import datetime



from proct_olis.core.watermark import Watermark
from sqlalchemy import create_engine, text


class WritterBase(ABC):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, watermark_value: datetime | None = None):
        self.process_name = process_name
        self.destination = config.destination
        self.settings = settings
        self.df = df
        self.config = config
        self.watermark_value = watermark_value
        self.utilities = Utilities()
        self.current_datetime = datetime.now()

    @abstractmethod
    def write(self):
        raise NotImplementedError


class S3Writter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, watermark_value: datetime | None = None):
        super().__init__(process_name, config, settings, df, watermark_value)
        self.fs = Session(settings, self.destination.destination_type).s3

    def write(self) -> None:
        if not self.df.is_empty():
            if not self.destination.date_bucket:
                path_save = f"s3://{self.destination.bucket_name}/{self.destination.file_name}"
            else:
                date = datetime.strptime(self.destination.date_bucket, "%Y-%m-%d")
                annee = str(date.year).zfill(4)
                mois = str(date.month).zfill(2)
                jour = str(date.day).zfill(2)

                path_save = f"s3://{self.destination.bucket_name}/{annee}{mois}{jour}/{self.destination.file_name}"

            # Écriture directe dans MinIO
            with self.fs.open(path_save, "wb") as f:
                self.df.write_parquet(f)

class tableWritter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, watermark_value: datetime | None = None):
        super().__init__(process_name, config, settings, df, watermark_value)
        self.pg_conn = Session(self.settings, kind=self.destination.destination_type).pg_conn
        self.wm = Watermark(settings)
    
    def update_watermark(self):
        if self.watermark_value:
            for name, source in self.config.sources.items():
                if source.watermark_column:
                    # Update watermark for sources that track it
                    self.wm.set_watermark(
                        source_name=name,
                        destination_name=self.destination.table,
                        watermark_column=source.watermark_column,
                        last_value=self.watermark_value
                    )

    def append_table(self) -> None:
        # Skip if input DataFrame is empty
        if self.df.is_empty():
            print("No data to process. Skipping append.")
            self.update_watermark()
            return
        
        query = f"""SELECT * FROM {self.destination.schema}.{self.destination.table}"""
        try:
            historical_df = pl.read_database_uri(query=query, uri=self.pg_conn)
        except Exception:
            historical_df = pl.DataFrame()

        if self.destination.business_keys:
            business_keys = self.destination.business_keys
        else:
            pk_list = self.destination.primary_key if isinstance(self.destination.primary_key, list) else ([self.destination.primary_key] if self.destination.primary_key else [])
            excluded_columns = pk_list + ["inserted_at", "updated_at"]
            business_keys = [col for col in self.df.columns if col not in excluded_columns]
    
        if not historical_df.is_empty():
            destination_table = (
                self.utilities.calculate_hash_based_on_columns(historical_df, business_keys)
            )

            current_df = self.utilities.calculate_hash_based_on_columns(self.df, business_keys)

            df_to_insert = (
                current_df
                .join(destination_table, on="hash_key", how="anti")
                .drop("hash_key")
            )
        else:
            df_to_insert = self.df

        print(f"Number of new rows to insert: {df_to_insert.height}")

        # Ajout des metadonnées
        df_to_insert = df_to_insert.with_columns(
            pl.lit(self.current_datetime).alias("inserted_at")
        )

        if not df_to_insert.is_empty():
            # Insérer les nouvelles lignes
            df_to_insert.write_database(
                table_name=f"{self.destination.schema}.{self.destination.table}",
                connection=self.pg_conn,
                if_table_exists="append"
            )
        
        # Update Watermark
        self.update_watermark()

    def scd1(self) -> None:
        """
        SCD Type 1: Overwrite old values with new values.
        Implementation: UPDATE existing records, INSERT new records (no table replacement).
        """
        # Skip if input DataFrame is empty
        if self.df.is_empty():
            print("No data to process. Skipping SCD1.")
            self.update_watermark()
            return
        
        query = f"""SELECT * FROM {self.destination.schema}.{self.destination.table}"""
        try:
            historical_df = pl.read_database_uri(query=query, uri=self.pg_conn)
        except Exception:
            # Table might not exist
            historical_df = pl.DataFrame()

        if self.destination.business_keys:
            business_keys = self.destination.business_keys
        else:
            # Default fallback if not specified
            excluded_columns = [self.destination.primary_key, "inserted_at", "updated_at", "rowhash"]
            business_keys = [col for col in self.df.columns if col not in excluded_columns]

        # Calculate hash for comparison
        scd_cols = ["inserted_at", "updated_at", "rowhash"]
        hash_cols = [c for c in self.df.columns if c not in scd_cols]
        
        current_df_hashed = self.utilities.calculate_hash_based_on_columns(self.df, hash_cols)
        
        if not historical_df.is_empty():
            # Trust stored rowhash
            historical_hashed = historical_df.with_columns(
                pl.col("rowhash").alias("hash_key")
            )
            
            # Identify new records (business keys not in historical)
            new_records = current_df_hashed.join(historical_hashed, on=business_keys, how="anti")
            
            # Identify existing records
            joined = current_df_hashed.join(
                historical_hashed.select(business_keys + ["hash_key", self.destination.primary_key]), 
                on=business_keys, 
                suffix="_hist"
            )
            
            # Records that changed (need UPDATE)
            changed_records = joined.filter(pl.col("hash_key") != pl.col("hash_key_hist"))
            
            if not changed_records.is_empty():
                print(f"Updating {changed_records.height} records...")
                
                # Build UPDATE statements for each changed record
                from sqlalchemy import create_engine, text
                engine = create_engine(self.pg_conn)
                
                # Get list of columns to update (exclude PK and metadata)
                update_cols = [c for c in self.df.columns if c not in [self.destination.primary_key]]
                
                with engine.begin() as conn:
                    for row in changed_records.iter_rows(named=True):
                        pk_value = row[self.destination.primary_key]
                        
                        # Build SET clause
                        set_clauses = []
                        for col in update_cols:
                            if col in row and col != "hash_key" and col != "hash_key_hist":
                                value = row[col]
                                if value is None:
                                    set_clauses.append(f"{col} = NULL")
                                elif isinstance(value, str):
                                    set_clauses.append(f"{col} = '{value}'")
                                else:
                                    set_clauses.append(f"{col} = {value}")
                        
                        # Add hash and updated_at
                        set_clauses.append(f"rowhash = '{row['hash_key']}'")
                        set_clauses.append(f"updated_at = '{self.current_datetime}'")
                        
                        update_query = f"""
                            UPDATE {self.destination.schema}.{self.destination.table}
                            SET {', '.join(set_clauses)}
                            WHERE {self.destination.primary_key} = {pk_value}
                        """
                        
                        conn.execute(text(update_query))
            
            # Prepare new records for INSERT
            if not new_records.is_empty():
                print(f"Inserting {new_records.height} new records...")
                new_inserts = new_records.with_columns(
                    pl.col("hash_key").alias("rowhash"),
                    pl.lit(self.current_datetime).alias("inserted_at"),
                    pl.lit(self.current_datetime).alias("updated_at")
                ).drop("hash_key")
                
                new_inserts.write_database(
                    table_name=f"{self.destination.schema}.{self.destination.table}",
                    connection=self.pg_conn,
                    if_table_exists="append"
                )
        else:
            # Initial load
            print(f"Initial load: Inserting {current_df_hashed.height} records...")
            initial_df = current_df_hashed.with_columns(
                pl.col("hash_key").alias("rowhash"),
                pl.lit(self.current_datetime).alias("inserted_at"),
                pl.lit(self.current_datetime).alias("updated_at")
            ).drop("hash_key")
            
            initial_df.write_database(
                table_name=f"{self.destination.schema}.{self.destination.table}",
                connection=self.pg_conn,
                if_table_exists="append"
            )
        
        print(f"SCD1 complete.")
        
        # Update Watermark
        self.update_watermark()


    def scd2(self) -> None:
        """
        SCD Type 2: Keep history.
        """
        # Skip if input DataFrame is empty
        if self.df.is_empty():
            print("No data to process. Skipping SCD2.")
            self.update_watermark()
            return
        
        query = f"""SELECT * FROM {self.destination.schema}.{self.destination.table}"""
        try:
            historical_df = pl.read_database_uri(query=query, uri=self.pg_conn)
        except Exception:
            historical_df = pl.DataFrame()

        if self.destination.business_keys:
            business_keys = self.destination.business_keys
        else:
            raise ValueError("Business Keys required for SCD2")

        # Exclude Watermark Columns from Hash Calculation if present
        # We scan sources to find watermark cols
        watermark_cols = []
        for source in self.config.sources.values():
             if source.watermark_column:
                 watermark_cols.append(source.watermark_column)
                 if source.columns and source.watermark_column in source.columns:
                     watermark_cols.append(source.columns[source.watermark_column])
        
        scd_cols = ["valid_from", "valid_to", "is_current", "rowhash", "inserted_at"] + watermark_cols
        hash_cols = [c for c in self.df.columns if c not in scd_cols]

        current_df_hashed = self.utilities.calculate_hash_based_on_columns(self.df, hash_cols)
        

        if not historical_df.is_empty():
            historical_active = historical_df.filter(pl.col("is_current") == True)
            historical_inactive = historical_df.filter(pl.col("is_current") == False)
            
            # Trust stored rowhash instead of recalculating
            # We alias it to 'hash_key' to match the convention used in comparison logic
            historical_active_hashed = historical_active.with_columns(
                pl.col("rowhash").alias("hash_key")
            )
            
            new_records = current_df_hashed.join(historical_active_hashed, on=business_keys, how="anti")
            
            joined = current_df_hashed.join(
                historical_active_hashed.select(business_keys + ["hash_key", "valid_from", self.destination.primary_key]), 
                on=business_keys, 
                suffix="_hist"
            )
            changed_records = joined.filter(pl.col("hash_key") != pl.col("hash_key_hist"))
            print(changed_records.head())
            unchanged_records_keys = joined.filter(pl.col("hash_key") == pl.col("hash_key_hist")).select(business_keys)
            
            # Prepare Updates (Closing old records)
            # We need the Primary Key (Surrogate Key) to update specific rows
            records_to_close = changed_records.select(self.destination.primary_key)
            
            if not records_to_close.is_empty():
                print(f"Closing {records_to_close.height} records...")
                ids_to_close = records_to_close[self.destination.primary_key].to_list()
                
                # Convert list to tuple-like string for SQL IN clause
                # Handle single item tuple syntax
                if len(ids_to_close) == 1:
                    ids_str = f"({ids_to_close[0]})"
                else:
                    ids_str = str(tuple(ids_to_close))
                
                update_query = f"""
                    UPDATE {self.destination.schema}.{self.destination.table}
                    SET is_current = FALSE, valid_to = '{self.current_datetime}'
                    WHERE {self.destination.primary_key} IN {ids_str}
                """
                
                engine = create_engine(self.pg_conn)
                with engine.begin() as conn:
                    conn.execute(text(update_query))
            
            # Prepare Inserts (New Versions + New Keys)
            new_versions = changed_records.select(self.df.columns + ["hash_key"]).with_columns(
                pl.lit(self.current_datetime).alias("valid_from"),
                pl.lit(None).cast(pl.Datetime).alias("valid_to"),
                pl.lit(True).alias("is_current"),
                pl.lit(self.current_datetime).alias("inserted_at")
            ).rename({"hash_key": "rowhash"})

            new_inserts = new_records.with_columns(
                pl.col("hash_key").alias("rowhash"),
                pl.lit(self.current_datetime).alias("valid_from"),
                pl.lit(None).cast(pl.Datetime).alias("valid_to"),
                pl.lit(True).alias("is_current"),
                pl.lit(self.current_datetime).alias("inserted_at")
            ).drop("hash_key")

            # Combine Inserts
            df_to_write = pl.concat([new_versions, new_inserts], how="vertical_relaxed")
            
        else:
            # Initial Load
            df_to_write = current_df_hashed.with_columns(
                pl.lit(self.current_datetime).alias("valid_from"),
                pl.lit(None).cast(pl.Datetime).alias("valid_to"),
                pl.lit(True).alias("is_current"),
                pl.lit(self.current_datetime).alias("inserted_at"),
                pl.col("hash_key").alias("rowhash")
            ).drop("hash_key")
            
            print(df_to_write.head())
        # Write Append
        if not df_to_write.is_empty():
            print(f"Inserting {df_to_write.height} new records...")
            df_to_write.write_database(
                table_name=f"{self.destination.schema}.{self.destination.table}",
                connection=self.pg_conn,
                if_table_exists="append"
            )
        print(f"SCD2 complete. Rows: {df_to_write.height}")
        
        # Update Watermark
        self.update_watermark()

    def write(self) -> None:
        print(f"Writing to {self.destination.schema}.{self.destination.table}") 
        print(f"Watermark: {self.watermark_value}") 
        print(f"Destination kind: {self.destination.kind}")
        if self.destination.kind == "append":
            self.append_table()
        elif self.destination.kind == "scd1":
            self.scd1()
        elif self.destination.kind == "scd2":
            self.scd2()


class Writter:
    def __init__(self, process_name: str, df: pl.DataFrame, config: Config, settings: Settings, watermark_value: datetime | None = None):
        self.process_name = process_name
        self.config = config
        self.settings = settings
        self.df = df
        self.watermark_value = watermark_value

    def write(self) -> None:
        if self.config.destination.destination_type == "s3":
            S3Writter(self.process_name, self.config, self.settings, self.df, self.watermark_value).write()
        elif self.config.destination.destination_type in ["postgres_operational", "postgres_datawarehouse"]:
            tableWritter(self.process_name, self.config, self.settings, self.df, self.watermark_value).write()