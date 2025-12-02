import polars as pl
from proct_olis.core.config import Config
from proct_olis.core.session import Session
from proct_olis.settings import Settings
from abc import ABC, abstractmethod
from proct_olis.core.utilities import Utilities
from datetime import datetime
from typing import Optional


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
        # 1. Gestion des fichiers communs
        if self.destination.file_name.startswith("common/"):
             path_save = f"s3://{self.destination.bucket_name}/{self.destination.file_name}"
        
        # 2. Gestion des fichiers quotidiens (Dossier daily_data)
        elif self.execution_date:
            path_save = f"s3://{self.destination.bucket_name}/daily_data/{self.execution_date}/{self.destination.file_name}"
        
        # 3. Fallback (Ancienne logique)
        elif self.destination.date_bucket:
            date = pl.Date.strptime(self.destination.date_bucket, fmt="%Y-%m-%d").to_python_date()
            annee = str(date.year).zfill(4)
            mois = str(date.month).zfill(2)
            jour = str(date.day).zfill(2)
            path_save = f"s3://{self.destination.bucket_name}/{annee}/{mois}/{jour}/{self.destination.file_name}"
        
        # 4. Racine par défaut
        else:
            path_save = f"s3://{self.destination.bucket_name}/{self.destination.file_name}"

        print(f"Writing S3: {path_save}")
        
        with self.fs.open(path_save, "wb") as f:
            self.df.write_parquet(f)


class tableWritter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame, execution_date: Optional[str] = None):
        super().__init__(process_name, config, settings, df, execution_date)
        self.pg_conn = Session(self.settings, kind=self.destination.destination_type).pg_conn
    
    def append_table(self) -> None:
        query = f"SELECT * FROM {self.destination.schema}.{self.destination.table}"
        
        try:
            historical_df = pl.read_database_uri(query=query, uri=self.pg_conn)
        except Exception:
            historical_df = pl.DataFrame(schema=self.df.schema)

        if self.destination.business_keys:
            business_keys = self.destination.business_keys
        else:
            excluded_columns = [self.destination.primary_key, "inserted_at", "updated_at"]
            if not historical_df.is_empty():
                business_keys = [col for col in historical_df.columns if col not in excluded_columns]
            else:
                business_keys = [col for col in self.df.columns if col not in excluded_columns]
    
        if not historical_df.is_empty():
            destination_table = self.utilities.calculate_hash_based_on_columns(historical_df, business_keys)
            current_df = self.utilities.calculate_hash_based_on_columns(self.df, business_keys)
            
            df_to_insert = current_df.join(destination_table, on="hash_key", how="anti")
        else:
            df_to_insert = self.df

        print(f"Number of new rows to insert: {df_to_insert.height}")

        # --- LOGIQUE CONDITIONNELLE ICI ---
        # On ajoute inserted_at SEULEMENT si c'est pour la base opérationnelle
        if self.destination.destination_type == "postgres_operational":
            if "inserted_at" not in df_to_insert.columns:
                df_to_insert = df_to_insert.with_columns(
                    pl.lit(self.current_datetime).alias("inserted_at")
                )

        if not df_to_insert.is_empty():
            cols_to_drop = ["hash_key"] if "hash_key" in df_to_insert.columns else []
            
            df_to_insert.drop(cols_to_drop).write_database(
                table_name=f"{self.destination.schema}.{self.destination.table}",
                connection=self.pg_conn,
                if_table_exists="append"
            )

    def write(self) -> None:
        if self.destination.kind == "append":
            self.append_table()


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
        elif self.config.destination.destination_type == "postgres_operational":
            tableWritter(self.process_name, self.config, self.settings, self.df, self.execution_date).write()
        elif self.config.destination.destination_type == "postgres_datawarehouse":
            tableWritter(self.process_name, self.config, self.settings, self.df, self.execution_date).write()