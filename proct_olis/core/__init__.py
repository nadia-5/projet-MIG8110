from abc import abstractmethod
import polars as pl
from dataclasses import dataclass, field
from typing import Dict 
import inspect
from pathlib import Path
import ast

from proct_olis.core.config import Config, JsonTemplate
from proct_olis.core.reader import Reader
from proct_olis.settings import Settings
from proct_olis.core.writter import Writter
from proct_olis.core.utilities import Utilities
from datetime import datetime

@dataclass
class TransformationBase:
    entity_map: Dict[str, pl.DataFrame] = field(default_factory=dict[str, pl.DataFrame])
    final_df: pl.DataFrame | None = None
    config: Config | None = None
    settings: Settings | None = None
    process_name: str = ""
    extract_date: str = ""
    watermark_value: datetime | None = None

    def recursive_substitute(self, item, cfg):
        # Cas 1 : C'est un Dictionnaire -> on descend dedans
        if isinstance(item, dict):
            return {k: self.recursive_substitute(v, cfg) for k, v in item.items()}
        
        # Cas 2 : C'est une Liste -> on itère sur les éléments
        elif isinstance(item, list):
            return [self.recursive_substitute(i, cfg) for i in item]
        
        # Cas 3 : C'est une String -> On fait le Template
        elif isinstance(item, str):
            # On remplace les variables ${...}
            new_value = JsonTemplate(item).safe_substitute(cfg)
            
            # ASTUCE : Si le résultat ressemble à un dict/list (ex: "{'a':1}"), on le convertit
            # Cela corrige votre problème de string avec échappement
            try:
                trimmed = new_value.strip()
                if (trimmed.startswith("{") and trimmed.endswith("}")) or \
                (trimmed.startswith("[") and trimmed.endswith("]")):
                    # ast.literal_eval transforme une string formatée python en objet réel
                    return ast.literal_eval(new_value)
            except (ValueError, SyntaxError):
                pass # Ce n'était pas un dict, on garde la string normale
                
            return new_value
        
        # Cas 4 : Entiers, Booléens, None -> on ne touche pas
        else:
            return item

    def __post_init__(self):
        if not self.settings:
            self.settings = Settings()
        
        if not self.config:
            data = Config.load_config(Path(inspect.getfile(self.__class__)).with_name("config.yml").as_posix())
        
        if self.extract_date:
            cfg = {
                "execution_date": self.extract_date,
            }

            data = self.recursive_substitute(data, cfg)
            
        self.config = Config.from_data(data)
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
        writter = Writter(self.process_name, self.final_df, self.config, self.settings, self.watermark_value)
        writter.write()
    
    def process(self):
        try:
            self.read()
            self.transformation()
            self.write()
        except Exception as e:
            print(f"Error processing data: {e}")

