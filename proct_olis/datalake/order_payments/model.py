from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Order Payments Datalake Process"

    def transformation(self):
        order_payments_df = self.entity_map.get("datalake.order_payments")

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = order_payments_df