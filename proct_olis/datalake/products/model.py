from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Products Datalake Process"

    def transformation(self):
        products_df = self.entity_map.get("datalake.products")

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = products_df