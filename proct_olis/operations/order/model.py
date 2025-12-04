from proct_olis.core.transformation import TransformationBase
import polars as pl


class Transformation(TransformationBase):
    process_name: str = "Order Transactional Database Process"

    def transformation(self):
        orders_df = self.entity_map.get("datalake.orders")

        if orders_df is None or orders_df.is_empty():
            self.final_df = pl.DataFrame()
            return

        # Map textual status → numeric status_id
        status_mapping = {
            "created": 1,
            "approved": 2,
            "invoiced": 3,
            "processing": 4,
            "shipped": 5,
            "delivered": 6,
            "unavailable": 7,
            "canceled": 8,
        }

        df = orders_df.with_columns(
            [
                pl.col("order_status")
                .replace(status_mapping)
                .fill_null(1)
                .alias("status_id"),
                pl.col("order_purchase_timestamp").alias("purchase_date"),
                pl.col("order_approved_at").alias("approved_date"),
                pl.col("order_estimated_delivery_date").alias(
                    "estimated_delivery_date"
                ),
                pl.col("order_delivered_carrier_date").alias(
                    "delivered_carrier_date"
                ),
                pl.col("order_delivered_customer_date").alias(
                    "delivered_customer_date"
                ),
            ]
        )

        self.final_df = (
            df.select(
                [
                    pl.col("order_id"),
                    pl.col("customer_id"),
                    pl.col("status_id"),
                    pl.col("purchase_date"),
                    pl.col("approved_date"),
                    pl.col("estimated_delivery_date"),
                    pl.col("delivered_carrier_date"),
                    pl.col("delivered_customer_date"),
                    pl.lit(self.execution_date).alias("inserted_at"),
                ]
            )
            .filter(pl.col("order_id").is_not_null())
        )
