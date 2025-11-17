from proct_olis.core import TransformationBase 
import polars as pl


class Transformation(TransformationBase):
    process_name: str = "Order Transactional Database Process"

    def transformation(self):
        order_status_type_df = self.entity_map.get("operational.order_status_type")
        order_df = self.entity_map.get("datalake.orders")

        self.final_df = (
            order_df
            .join(
                order_status_type_df,
                left_on=pl.col("order_status").cast(pl.Utf8),
                right_on=pl.col("order_status_type_code").cast(pl.Utf8),
                how="left",
            )
            .select(
                pl.col("order_id"),
                pl.col("customer_id"),
                pl.col("order_status_type_id").alias("status_id"),
                pl.col("purchase_date").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S", strict=False),
                pl.col("estimated_delivery_date").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S", strict=False),
                pl.col("approved_date").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S", strict=False),
                pl.col("delivered_carrier_date").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S", strict=False),
                pl.col("delivered_customer_date").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S", strict=False)
            )
            .with_columns(
                (
                    pl.col("order_id").str.slice(0, 8) + "-" +
                    pl.col("order_id").str.slice(8, 4) + "-" +
                    pl.col("order_id").str.slice(12, 4) + "-" +
                    pl.col("order_id").str.slice(16, 4) + "-" +
                    pl.col("order_id").str.slice(20, 12)
                ).alias("order_id")
            )
            .with_columns(
                (
                    pl.col("customer_id").str.slice(0, 8) + "-" +
                    pl.col("customer_id").str.slice(8, 4) + "-" +
                    pl.col("customer_id").str.slice(12, 4) + "-" +
                    pl.col("customer_id").str.slice(16, 4) + "-" +
                    pl.col("customer_id").str.slice(20, 12)
                ).alias("customer_id")
            )
        )