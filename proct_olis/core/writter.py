import polars as pl
from proct_olis.core.config import Config
from proct_olis.core.session import Session
from proct_olis.settings import Settings
from abc import ABC, abstractmethod
from proct_olis.core.utilities import Utilities
from datetime import datetime


class WritterBase(ABC):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame):
        self.process_name = process_name
        self.destination = config.destination
        self.settings = settings
        self.df = df
        self.utilities = Utilities()
        self.current_datetime = datetime.now()

    @abstractmethod
    def write(self):
        raise NotImplementedError


class S3Writter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame):
        super().__init__(process_name, config, settings, df)
        self.fs = Session(settings, self.destination.destination_type).s3

    def write(self) -> None:
        if not self.destination.date_bucket:
            path_save = f"s3://{self.destination.bucket_name}/{self.destination.file_name}"
        else:
            date = pl.Date.strptime(self.destination.date_bucket, fmt="%Y-%m-%d").to_python_date()
            annee = str(date.year).zfill(4)
            mois = str(date.month).zfill(2)
            jour = str(date.day).zfill(2)

            path_save = f"s3://{self.destination.bucket_name}/{annee}/{mois}/{jour}/{self.destination.file_name}"

        # Écriture directe dans MinIO
        with self.fs.open(path_save, "wb") as f:
            self.df.write_parquet(f)

class tableWritter(WritterBase):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame):
        super().__init__(process_name, config, settings, df)
        self.pg_conn = Session(self.settings, kind=self.destination.destination_type).pg_conn
    
    def append_table(self) -> None:
        query = f"""SELECT * FROM {self.destination.schema}.{self.destination.table}"""
        historical_df = pl.read_database_uri(query=query, uri=self.pg_conn)

        print(historical_df.head())

        if self.destination.business_keys:
            business_keys = self.destination.business_keys
        else:
            excluded_columns = [self.destination.primary_key, "created_at", "updated_at"]
            business_keys = [col for col in historical_df.columns if col not in excluded_columns]
    
        destination_table = (
            self.utilities.calculate_hash_based_on_columns(historical_df, business_keys)
        )

        current_df = self.utilities.calculate_hash_based_on_columns(self.df, business_keys)

        df_to_insert = (
            current_df
            .join(destination_table, on="hash_key", how="anti")
        )

        # Ajout des metadonnées
        df_to_insert = df_to_insert.with_columns(
            pl.lit(self.current_datetime).alias("created_at")
        )

        if not df_to_insert.is_empty():
            # Insérer les nouvelles lignes
            df_to_insert.drop("hash_key").write_database(
                table_name=f"{self.destination.schema}.{self.destination.table}",
                connection=self.pg_conn,
                if_table_exists="append"
            )

    def write(self) -> None:
        if self.destination.kind == "append":
            self.append_table()


class Writter:
    def __init__(self, process_name: str, df: pl.DataFrame, config: Config, settings: Settings):
        self.process_name = process_name
        self.config = config
        self.settings = settings
        self.df = df

    def write(self) -> None:
        if self.config.destination.destination_type == "s3":
            S3Writter(self.process_name, self.config, self.settings, self.df).write()
        elif self.config.destination.destination_type == "postgres_operational":
            tableWritter(self.process_name, self.config, self.settings, self.df).write()