from proct_olis.core import TransformationBase
import polars as pl
import json
from datetime import datetime

class DimProductSellerPrice(TransformationBase):
    process_name: str = "Dim Product Seller Price DW Process"
    max_timestamp: datetime | None = None

    def transformation(self):
        df = self.entity_map.get("audit.logged_actions")
        
        if df is None or df.is_empty():
            self.final_df = pl.DataFrame()
            return

        # Store max timestamp for watermark update
        self.max_timestamp = df["action_tstamp_stm"].max()
        self.watermark_value = self.max_timestamp

        # Parse JSONB row_data
        json_schema = pl.Struct({
            "product_id": pl.Utf8,
            "seller_id": pl.Utf8,
            "price": pl.Float64
        })

        parsed_df = df.with_columns(
             pl.col("row_data").map_elements(lambda x: json.loads(x) if x else {}, return_dtype=json_schema).alias("data")
        ).unnest("data")
        
        # Keep the latest version per product-seller pair
        deduplicated = (
            parsed_df
            .sort("action_tstamp_stm")
            .unique(subset=["product_id", "seller_id"], keep="last")
        )

        # Select business columns for SCD2 comparison
        self.final_df = (
            deduplicated.select([
                pl.col("product_id").cast(pl.Utf8),
                pl.col("seller_id").cast(pl.Utf8),
                pl.col("price").cast(pl.Float64)
            ])
        )
