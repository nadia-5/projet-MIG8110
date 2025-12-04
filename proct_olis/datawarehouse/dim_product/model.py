from proct_olis.core.transformation import TransformationBase
import polars as pl
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Dim Product Process"

    def transformation(self):
        prod = self.entity_map.get("operational.product")
        cat = self.entity_map.get("operational.category")

        # Jointure pour récupérer le nom de la catégorie
        df = prod.join(cat, on="product_category_id", how="left")

        self.final_df = df.select([
            pl.col("product_id"),
            pl.col("product_category_name").alias("product_category"),
            pl.col("name_length"),
            pl.col("description_length"),
            pl.col("photos_qty"),
            pl.col("weight_g"),
            pl.col("length_cm"),
            pl.col("height_cm"),
            pl.col("width_cm"),
            
            # Champs SCD (Type 2)
            pl.lit(datetime.now()).alias("valid_from"),
            pl.lit(None, dtype=pl.Datetime).alias("valid_to"),
            pl.lit(True).alias("is_current"),
            pl.lit("hash").alias("rowhash")
        ])