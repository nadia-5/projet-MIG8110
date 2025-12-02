import sys
import os
import inspect
from pathlib import Path
from typing import Dict, Optional
import polars as pl

from proct_olis.core.config import Config
from proct_olis.core.reader import Reader
from proct_olis.core.destination import Destination
from proct_olis.core.writter import Writter
from proct_olis.core.utilities import Utilities
from proct_olis.settings import Settings

class TransformationBase:
    # On définit les valeurs par défaut
    process_name: str = ""
    
    def __init__(self, execution_date: Optional[str] = None):
        self.execution_date = execution_date
        self.entity_map: Dict[str, pl.DataFrame] = {}
        self.final_df: Optional[pl.DataFrame] = None
        self.config: Optional[Config] = None
        self.settings: Optional[Settings] = None
        self.reader: Optional[Reader] = None
        self.utilities = Utilities()

    def _init_resources(self):
        # Initialisation lazy (au moment du process) pour éviter les imports circulaires
        if not self.settings:
            self.settings = Settings()
        
        if not self.config:
            # Astuce pour trouver le fichier config.yml à côté du script enfant (model.py)
            child_class_file = sys.modules[self.__module__].__file__
            config_path = Path(child_class_file).with_name("config.yml").as_posix()
            
            # On utilise un reader temporaire ou la méthode statique si disponible
            # Ici on instancie Reader juste pour charger la config si besoin, ou on utilise Config directement
            # Supposons que Config.load_config existe comme dans votre code original
            self.config = Config.load_config(config_path)

        # Initialisation du VRAI Reader avec la date
        self.reader = Reader(
            process_name=self.process_name,
            config=self.config,
            settings=self.settings,
            execution_date=self.execution_date
        )

    def read(self):
        self._init_resources()
        # Le reader va chercher les fichiers (statiques ou datés selon execution_date)
        self.entity_map = self.reader.source_dataframes

    def transformation(self):
        raise NotImplementedError

    def write(self):
        writter = Writter(
            process_name=self.process_name, 
            df=self.final_df, 
            config=self.config, 
            settings=self.settings,
            execution_date=self.execution_date 
        )
        writter.write()
    
    def process(self):
        try:
            print(f"🔄 Exécution : {self.process_name} (Date: {self.execution_date})")
            self.read()
            self.transformation()
            self.write()
            print("✅ Terminé avec succès.")
        except Exception as e:
            print(f"❌ Erreur dans le process : {e}")
            raise e