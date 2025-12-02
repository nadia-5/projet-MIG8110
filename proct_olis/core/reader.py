from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Dict, Optional, TYPE_CHECKING
import polars as pl
import yaml

from proct_olis.core.config import Config
from proct_olis.core.source import Source
from proct_olis.core.session import Session

if TYPE_CHECKING:
    from proct_olis.settings import Settings

class BaseReader(ABC):
    @abstractmethod
    def getDataFrameSources(self, execution_date: Optional[str] = None) -> Dict[str, pl.DataFrame]:
        raise NotImplementedError

class S3Reader(BaseReader):
    def __init__(self, sources: Dict[str, Source], settings: Settings):
        self.fs = Session(settings, kind="s3").s3
        self.settings = settings
        self.sources = sources
        
    def getDataFrameSources(self, execution_date: Optional[str] = None) -> Dict[str, pl.DataFrame]:
        entity_map = {}
        for _name, source in self.sources.items():
            bucket_name = source.bucket_name
            file_name = source.file_name
            file_extension = source.file_extension
            
            # --- LOGIQUE DE CHEMIN DYNAMIQUE ---
            # Cas 1 : Fichier commun (ex: common/geolocation)
            if file_name.startswith("common/"):
                path_read = f"s3://{bucket_name}/{file_name}.{file_extension}"
            
            # Cas 2 : Fichier quotidien avec date fournie (ex: daily_data/2016-10-04/orders)
            elif execution_date:
                path_read = f"s3://{bucket_name}/daily_data/{execution_date}/{file_name}.{file_extension}"
            
            # Cas 3 : Fichier statique à la racine (Fallback)
            else:
                path_read = f"s3://{bucket_name}/{file_name}.{file_extension}"

            print(f"📥 Lecture S3 ({_name}): {path_read}")

            try:
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

                if source.columns:
                    original_cols = list(source.columns.keys())
                    aliases = list(source.columns.values())
                    df = df.select(original_cols).rename(dict(zip(original_cols, aliases)))

                entity_map[_name] = df
            
            except Exception as e:
                print(f"⚠️ Erreur lecture {_name} ({path_read}): {e}")
                # Retourne un DataFrame vide pour ne pas planter le script
                entity_map[_name] = pl.DataFrame()

        return entity_map
    

class DatabaseReader(BaseReader):
    def __init__(self, sources: Dict[str, Source], settings: Settings, kind: str):
        self.settings = settings
        self.sources = sources
        self.pg_conn = Session(settings, kind=kind).pg_conn

    def getDataFrameSources(self, execution_date: Optional[str] = None) -> Dict[str, pl.DataFrame]:
        entity_map = {}
        for _name, source in self.sources.items():
            table_name = source.table
            schema = source.schema if source.schema else "public"
            query = f"SELECT * FROM {schema}.{table_name}"

            if source.filter_statement:
                query += f" WHERE {source.filter_statement}"

            try:
                df = pl.read_database_uri(query=query, uri=self.pg_conn)

                if source.columns:
                    original_cols = list(source.columns.keys())
                    aliases = list(source.columns.values())
                    df = df.select(original_cols).rename(dict(zip(original_cols, aliases)))

                entity_map[_name] = df
            except Exception as e:
                print(f"⚠️ Erreur lecture DB {_name}: {e}")
                entity_map[_name] = pl.DataFrame()

        return entity_map
        
@dataclass  
class Reader:
    process_name: str
    config: Config
    settings: Settings
    execution_date: Optional[str] = None
    source_dataframes: Dict[str, pl.DataFrame] = field(default_factory=dict)

    def __post_init__(self):
        # Si config est None (mode loader), on ne fait rien
        if self.config is None:
            return

        if self.config.datalake_sources:
            self.source_dataframes.update(
                S3Reader(self.config.datalake_sources, self.settings).getDataFrameSources(self.execution_date)
            )
        if self.config.operational_sources:
            self.source_dataframes.update(
                DatabaseReader(self.config.operational_sources, self.settings, "postgres_operational").getDataFrameSources(self.execution_date)
            )
        if self.config.datawarehouse_sources:
            self.source_dataframes.update(
                DatabaseReader(self.config.datawarehouse_sources, self.settings, "postgres_datawarehouse").getDataFrameSources(self.execution_date)
            )
    
    def load_config(self, path: str) -> Config:
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        
        # Adaptation selon la structure de votre classe Config
        if hasattr(Config, 'from_dict'):
             return Config.from_dict(config_data)
        return Config(**config_data)