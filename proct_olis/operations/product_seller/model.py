from proct_olis.core import TransformationBase 
import polars as pl
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Product Seller Association Process"

    def transformation(self):
        items_df = self.entity_map.get("datalake.order_items")

        self.final_df = (
            items_df
            .select([
                pl.col("product_id"),
                pl.col("seller_id"),
                pl.col("price").cast(pl.Float64)
            ])
            .unique(subset=["product_id", "seller_id"], keep="last")
            
            .with_columns(
                pl.lit(datetime.now()).alias("inserted_at")
            )
        )
