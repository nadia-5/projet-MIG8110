from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "product_category_name Datalake Process"

    def transformation(self):
        product_category_name_df = self.entity_map.get("datalake.product_category_name")

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = product_category_name_df