from proct_olis.core.transformation import TransformationBase
import polars as pl
import uuid # ⬅️ ADDED: Import uuid
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Product Seller Association Process"

    def transformation(self):
        items_df = self.entity_map.get("datalake.order_items")

        self.final_df = (
            items_df
            .select([
                # ⬇️ FIX: Normalize UUIDs
                pl.col("product_id")
                    .map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8)
                    .alias("product_id"),
                pl.col("seller_id")
                    .map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8)
                    .alias("seller_id"),
                
                pl.col("price").cast(pl.Float64)
            ])
            # The 'unique' operation must run AFTER normalization
            .unique(subset=["product_id", "seller_id"], keep="last")
            
            
        )