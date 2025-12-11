from proct_olis.core import TransformationBase
import polars as pl
import json
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Dim Product DW Process"
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
            "product_category_id": pl.Int64,
            "name_length": pl.Int64,
            "description_length": pl.Int64,
            "photos_qty": pl.Int64,
            "weight_g": pl.Int64,
            "length_cm": pl.Int64,
            "height_cm": pl.Int64,
            "width_cm": pl.Int64
        })

        parsed_df = df.with_columns(
             pl.col("row_data").map_elements(lambda x: json.loads(x) if x else {}, return_dtype=json_schema).alias("data")
        ).unnest("data")
        
        # Keep the latest version per product
        deduplicated = (
            parsed_df
            .sort("action_tstamp_stm")
            .unique(subset=["product_id"], keep="last")
        )

        # Load product_category lookup table
        category_df = self.entity_map.get("operational.product_category")
        
        # Join with product_category to get category name
        if category_df is not None and not category_df.is_empty():
            joined_df = deduplicated.join(
                category_df,
                on="product_category_id",
                how="left"
            )
        else:
            # If no category data, add null column
            joined_df = deduplicated.with_columns(
                pl.lit(None).alias("product_category_name")
            )

        # Select business columns for SCD2 comparison
        self.final_df = (
            joined_df.select([
                pl.col("product_id").cast(pl.Utf8),
                pl.col("product_category_name").cast(pl.Utf8).alias("product_category"),
                pl.col("name_length").cast(pl.Int64),
                pl.col("description_length").cast(pl.Int64),
                pl.col("photos_qty").cast(pl.Int64),
                pl.col("weight_g").cast(pl.Int64),
                pl.col("length_cm").cast(pl.Int64),
                pl.col("height_cm").cast(pl.Int64),
                pl.col("width_cm").cast(pl.Int64)
            ])
        )