from proct_olis.core import TransformationBase
import polars as pl
import json
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Dim Location DW Process"
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
            "zip_code_prefix": pl.Utf8,
            "city": pl.Utf8,
            "state": pl.Utf8
        })

        parsed_df = df.with_columns(
             pl.col("row_data").map_elements(lambda x: json.loads(x) if x else {}, return_dtype=json_schema).alias("data")
        ).unnest("data")
        
        # Keep the latest version per location (SCD1 - overwrite)
        deduplicated = (
            parsed_df
            .sort("action_tstamp_stm")
            .unique(subset=["zip_code_prefix", "city", "state"], keep="last")
        )

        # Select business columns for SCD1 comparison
        self.final_df = (
            deduplicated.select([
                pl.col("zip_code_prefix").cast(pl.Utf8),
                pl.col("city").cast(pl.Utf8),
                pl.col("state").cast(pl.Utf8)
            ])
        )