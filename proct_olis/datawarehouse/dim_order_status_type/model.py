from proct_olis.core.transformation import TransformationBase
import polars as pl
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Dim Order Status Process"

    def transformation(self):
        df = self.entity_map.get("operational.status")

        self.final_df = df.select([
            pl.col("order_status_type_id"),
            pl.col("order_status_type_code"),
            pl.col("order_status_type_description"),
            pl.lit(datetime.now()).alias("inserted_at"),
            pl.lit(datetime.now()).alias("updated_at"),
            pl.lit("hash").alias("rowhash")
        ])