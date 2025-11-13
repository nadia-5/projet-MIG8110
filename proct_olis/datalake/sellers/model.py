from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Sellers Datalake Process"

    def transformation(self):
        sellers_df = self.entity_map.get("datalake.sellers")

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = sellers_df