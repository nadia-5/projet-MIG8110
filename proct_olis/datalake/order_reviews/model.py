from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Order Reviews Datalake Process"

    def transformation(self):
        order_reviews_df = self.entity_map.get("datalake.order_reviews")

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = order_reviews_df