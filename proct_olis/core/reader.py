from dataclasses import dataclass, field
from proct_olis.core.config import Config
from abc import ABC, abstractmethod
from proct_olis.core.source import Source
from proct_olis.settings import Settings
from proct_olis.core.session import Session
import polars as pl
from typing import Dict


class BaseReader(ABC):
    @abstractmethod
    def getDataFrameSources(self) -> Dict[str, pl.DataFrame]:
        raise NotImplementedError


class S3Reader(BaseReader):
    def __init__(self, sources: Dict[str, Source], settings: Settings):
        self.fs = Session(settings, kind="s3").s3
        self.settings = settings
        self.sources = sources
        
    def getDataFrameSources(self) -> Dict[str, pl.DataFrame]:
        entity_map = {}
        for _name, source in self.sources.items():
            bucket_name = source.bucket_name
            file_name = source.file_name
            file_extension = source.file_extension
            path_read = f"s3://{bucket_name}/{file_name}.{file_extension}"

            if file_extension == "csv":
                with self.fs.open(path_read, "rb") as f:
                    df = pl.read_csv(f)
            elif file_extension == "parquet":
                with self.fs.open(path_read, "rb") as f:
                    df = pl.read_parquet(f)
            else:
                raise ValueError(f"Unsupported file extension: {file_extension}")

            if source.filter_statement:
                df = df.filter(pl.sql_expr(source.filter_statement))

            # Sélection des colonnes avec alias
            if source.columns:
                # Colonnes originales
                original_cols = list(source.columns.keys())
                # Alias
                aliases = list(source.columns.values())

                # Sélection puis renommage
                df = df.select(original_cols).rename(dict(zip(original_cols, aliases)))

            entity_map[_name] = df

        return entity_map
    

class DatabaseReader(BaseReader):
    def __init__(self, sources: Dict[str, Source], settings: Settings, kind: str):
        self.settings = settings
        self.sources = sources
        self.pg_conn = Session(settings, kind=kind).pg_conn

    def getDataFrameSources(self) -> Dict[str, pl.DataFrame]:
        entity_map = {}
        for _name, source in self.sources.items():
            table_name = source.table

            schema = source.schema if source.schema else "public"
            query = f"""SELECT * FROM {schema}.{table_name}"""

            if source.filter_statement:
                query += f" WHERE {source.filter_statement}"

            df = pl.read_database_uri(query=query, uri=self.pg_conn)

            # Sélection des colonnes avec alias
            if source.columns:
                # Colonnes originales
                original_cols = list(source.columns.keys())
                # Alias
                aliases = list(source.columns.values())

                # Sélection puis renommage
                df = df.select(original_cols).rename(dict(zip(original_cols, aliases)))

            entity_map[_name] = df

        return entity_map
        
@dataclass  
class Reader:
    process_name: str
    config: Config
    settings: Settings
    source_dataframes: Dict[str, pl.DataFrame] = field(default_factory=dict[str, pl.DataFrame])

    def __post_init__(self):
        if self.config.datalake_sources:
            self.source_dataframes.update(S3Reader(self.config.datalake_sources, self.settings).getDataFrameSources())
        if self.config.operational_sources:
            self.source_dataframes.update(DatabaseReader(self.config.operational_sources, self.settings, "postgres_operational").getDataFrameSources())
        if self.config.datawarehouse_sources:
            self.source_dataframes.update(DatabaseReader(self.config.datawarehouse_sources, self.settings, "postgres_datawarehouse").getDataFrameSources())