from proct_olis.core import TransformationBase
import polars as pl
import json
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Dim Customer DW Process"
    max_timestamp: datetime | None = None

    def transformation(self):
        df = self.entity_map.get("audit.logged_actions")
        
        if df is None or df.is_empty():
            self.final_df = pl.DataFrame()
            return

        # Store max timestamp for watermark update (Writer will handle it)
        self.max_timestamp = df["action_tstamp_stm"].max()
        self.watermark_value = self.max_timestamp

        # Parse JSONB row_data
        # We define the schema for the struct
        json_schema = pl.Struct({
            "customer_id": pl.Utf8,
            "customer_code": pl.Utf8,
            "customer_zip_code": pl.Utf8,
            "customer_city": pl.Utf8,
            "customer_state": pl.Utf8
        })

        parsed_df = df.with_columns(
             pl.col("row_data").map_elements(lambda x: json.loads(x) if x else {}, return_dtype=json_schema).alias("data")
        ).unnest("data")
        
        # Depending on Polars version, map_elements might be slow or return Struct directly.
        # But assuming robustness for 'row_data' column.
        # We need specific columns: customer_id, customer_code, city, state, zip
        
        # Keep the latest version per customer
        # Sort by timestamp and distinct
        deduplicated = (
            parsed_df
            .sort("action_tstamp_stm")
            .unique(subset=["customer_id"], keep="last")
        )

        # Select business columns for SCD2 comparison
        # Note: dim_customer needs: customer_id (NK), customer_code, customer_city, customer_state, customer_zip_code
        self.final_df = (
            deduplicated.select([
                pl.col("customer_id").cast(pl.Utf8),
                pl.col("customer_code").cast(pl.Utf8), 
                pl.col("customer_city").cast(pl.Utf8),
                pl.col("customer_state").cast(pl.Utf8),
                pl.col("customer_zip_code").cast(pl.Utf8)
            ])
        )