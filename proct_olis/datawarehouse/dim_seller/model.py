from proct_olis.core import TransformationBase
import polars as pl
import json
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Dim Seller DW Process"
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
            "seller_id": pl.Utf8,
            "seller_city": pl.Utf8,
            "seller_state": pl.Utf8,
            "seller_zip_code": pl.Utf8
        })

        parsed_df = df.with_columns(
             pl.col("row_data").map_elements(lambda x: json.loads(x) if x else {}, return_dtype=json_schema).alias("data")
        ).unnest("data")
        
        # Keep the latest version per seller
        deduplicated = (
            parsed_df
            .sort("action_tstamp_stm")
            .unique(subset=["seller_id"], keep="last")
        )

        # Select business columns for SCD2 comparison
        self.final_df = (
            deduplicated.select([
                pl.col("seller_id").cast(pl.Utf8),
                pl.col("seller_city").cast(pl.Utf8),
                pl.col("seller_state").cast(pl.Utf8),
                pl.col("seller_zip_code").cast(pl.Utf8)
            ])
        )