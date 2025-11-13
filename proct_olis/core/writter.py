import s3fs 
import polars as pl
from dataclasses import dataclass
from proct_olis.core.config import Config
from proct_olis.core.session import Session
from proct_olis.settings import Settings
from abc import ABC, abstractmethod


class WritterBase(ABC):
    def __init__(self, process_name: str, config: Config, settings: Settings, df: pl.DataFrame):
        self.process_name = process_name
        self.destination = config.destination
        self.settings = settings
        self.df = df

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

    def calculate_hash_based_on_columns(self, df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
        concat_columns = pl.concat_str([pl.col(col).cast(pl.Utf8) for col in columns], separator="|")
        hash_column = concat_columns.apply(lambda x: hash(x))
        return df.with_column(hash_column.alias("hash_key"))
    
    def append_table(self, df: pl.DataFrame) -> None:
        query = f"""SELECT * FROM {self.destination.schema}.{self.destination.table}"""
        destination_table = self.calculate_hash_based_on_columns(pl.read_database(query, connection_uri=self.pg_conn), self.destination.business_keys)

        current_df = self.calculate_hash_based_on_columns(df, self.destination.business_keys)

        df_to_insert = current_df.join(destination_table, on="hash_key", how="anti")

        if not df_to_insert.is_empty():
            # Insérer les nouvelles lignes
            df_to_insert.drop("hash_key").write_database(
                table=f"{self.destination.schema}.{self.destination.table}",
                connection_uri=self.pg_conn,
                if_exists="append"
            )

    def write(self, df: pl.DataFrame) -> None:
        if self.destination.kind == "append":
            self.append_table(df)


class Writter:
    def __init__(self, process_name: str, df: pl.DataFrame, config: Config, settings: Settings):
        self.process_name = process_name
        self.config = config
        self.settings = settings
        self.df = df

    def write(self) -> None:
        if self.config.destination.destination_type == "s3":
            S3Writter(self.process_name, self.config, self.settings, self.df).write()
        elif self.config.destination.destination_type == "table":
            tableWritter(self.process_name, self.config, self.settings, self.df).write()