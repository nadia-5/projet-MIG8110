from abc import abstractmethod
import polars as pl
from dataclasses import dataclass, field
from typing import Dict 
import inspect
from pathlib import Path

from proct_olis.core.config import Config
from proct_olis.core.reader import Reader
from proct_olis.settings import Settings
from proct_olis.core.writter import Writter
from proct_olis.core.utilities import Utilities

@dataclass
class TransformationBase:
    entity_map: Dict[str, pl.DataFrame] = field(default_factory=dict[str, pl.DataFrame])
    final_df: pl.DataFrame | None = None
    config: Config | None = None
    settings: Settings | None = None
    process_name: str = ""

    def __post_init__(self):
        if not self.settings:
            self.settings = Settings()
        
        if not self.config:
            self.config = Config.load_config(Path(inspect.getfile(self.__class__)).with_name("config.yml").as_posix())

        self.reader = Reader(self.process_name, self.config, self.settings)
        self.utilities = Utilities()
        self.pre_transformation()

    def pre_transformation(self):
        pass

    def save_file_path(self, bucket_name: str, base_file: pl.DataFrame, date: str = None) -> str:
        if date is None:
            path_save = f"s3://raw-data/{bucket_name}.parquet"
        else:
            annee = str(date.year).zfill(4)
            mois = str(date.month).zfill(2)
            jour = str(date.day).zfill(2)

            path_save = f"s3://raw-data/{annee}/{mois}/{jour}/{bucket_name}.parquet"

        # Écriture directe dans MinIO
        with self.fs.open(path_save, "wb") as f:
            base_file.write_parquet(f)
    
    def read(self):
        self.entity_map = self.reader.source_dataframes

    @abstractmethod
    def transformation(self):
        raise NotImplementedError

    def write(self):
        writter = Writter(self.process_name, self.final_df, self.config, self.settings)
        writter.write()
    
    def process(self):
        try:
            self.read()
            self.transformation()
            self.write()
        except Exception as e:
            print(f"Error processing data: {e}")
