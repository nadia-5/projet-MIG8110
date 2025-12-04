from proct_olis.core.transformation import TransformationBase
import polars as pl
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Dim Customer DW Process"

    def transformation(self):
        df = self.entity_map.get("operational.customer")
        
        self.final_df = (
            df.select([
                pl.col("customer_id"),
                pl.col("customer_code"), 
                pl.col("customer_city"),
                pl.col("customer_state"),
                pl.col("customer_zip_code"),
                pl.lit(datetime.now()).alias("valid_from"),
                pl.lit(None, dtype=pl.Datetime).alias("valid_to"),
                pl.lit(True).alias("is_current"),
                pl.lit("hash_placeholder").alias("rowhash")
            ])
        )