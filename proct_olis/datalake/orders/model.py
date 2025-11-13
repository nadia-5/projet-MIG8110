from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Orders Datalake Process"

    def transformation(self):
        orders_df = self.entity_map.get("datalake.orders")

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = orders_df