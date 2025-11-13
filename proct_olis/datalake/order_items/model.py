from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Order Items Datalake Process"

    def transformation(self):
        order_items_df = self.entity_map.get("datalake.order_items")

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = order_items_df