from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Customer Datalake Process"

    def transformation(self):
        customers_df = self.entity_map.get("datalake.customers")

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = customers_df