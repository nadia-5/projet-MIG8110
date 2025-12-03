from proct_olis.core.transformation import TransformationBase
import polars as pl
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Dim Seller Process"

    def transformation(self):
        df = self.entity_map.get("operational.seller")

        self.final_df = df.select([
            pl.col("seller_id"), # Attention au type (UUID vs INT) selon votre table cible
            pl.col("seller_state"),
            pl.col("seller_city"),
            pl.col("seller_zip_code"),
            
            # Champs SCD (Type 2)
            pl.lit(datetime.now()).alias("valid_from"),
            pl.lit(None, dtype=pl.Datetime).alias("valid_to"),
            pl.lit(True).alias("is_current"),
            pl.lit("hash").alias("rowhash")
        ])