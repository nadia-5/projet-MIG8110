from proct_olis.core.transformation import TransformationBase
import polars as pl
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Fact Orders DW Process"

    def transformation(self):
        orders = self.entity_map.get("operational.orders")
        items = self.entity_map.get("operational.items")
        fact = items.join(orders, on="order_id", how="inner")

        self.final_df = (
            fact.select([
                pl.col("order_id"),
                pl.col("customer_id"),
                pl.col("product_id"),  
                pl.col("seller_id"),  
                pl.col("status_id").alias("order_status_id"),
                pl.col("price"),
                pl.col("freight_value"),
                pl.lit(1).alias("num_items"),
                pl.col("purchase_date"),
                pl.col("approved_date"),
                pl.col("delivered_carrier_date"),
                pl.col("delivered_customer_date"),
                pl.col("estimated_delivery_date"),
                pl.col("purchase_date").dt.strftime("%Y%m%d").cast(pl.Int32, strict=False).alias("date_id"),
                pl.lit(datetime.now()).alias("inserted_at")
            ])
        )