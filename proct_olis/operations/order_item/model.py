from proct_olis.core.transformation import TransformationBase 
import polars as pl
import uuid # ⬅️ ADD THIS IMPORT

class Transformation(TransformationBase):
    process_name: str = "Order Item Transactional Database Process"

    def transformation(self):

        df = self.entity_map.get("datalake.order_items")

        # Joining here is generally not recommended for transactional tables,
        # but if required for lookups, ensure IDs are normalized.

        df = (
            df.select(
                [
                    # ⬇️ FIX: Normalize all UUIDs
                    pl.col("order_id").map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8).alias("order_id"),
                    pl.col("item_id").alias("item_id"),
                    pl.col("product_id").map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8).alias("product_id"),
                    pl.col("seller_id").map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8).alias("seller_id"),
                    pl.col("shipping_limit_date").alias("shipping_limit_date"),
                    pl.col("price").alias("price"),
                    pl.col("freight_value").alias("freight_value"),
                ]
            )
        )

        self.final_df = df