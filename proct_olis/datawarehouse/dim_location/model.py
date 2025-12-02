from proct_olis.core.transformation import TransformationBase
import polars as pl
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Dim Location Process"

    def transformation(self):
        df = self.entity_map.get("operational.location")

        self.final_df = (
            df.select([
                pl.col("location_id"),
                pl.col("zip_code_prefix"),
                pl.col("city"),
                pl.col("state"),
                pl.lit(datetime.now()).alias("inserted_at"),
                pl.lit(datetime.now()).alias("updated_at"),
                pl.lit("hash").alias("rowhash")
            ])
            # Dédoublonnage au cas où la source aurait des doublons non gérés
            .unique(subset=["zip_code_prefix", "city", "state"], keep="first")
        )