from proct_olis.core import TransformationBase
import polars as pl
import json
from datetime import datetime

class Transformation(TransformationBase):
    process_name: str = "Fact Orders DW Process"
    max_timestamp: datetime | None = None

    def transformation(self):
        # Load audit_log data
        orders_df = self.entity_map.get("audit.order")
        items_df = self.entity_map.get("audit.order_item")
        
        if orders_df is None or orders_df.is_empty() or items_df is None or items_df.is_empty():
            self.final_df = pl.DataFrame()
            return

        # Store max timestamp for watermark update
        max_order_ts = orders_df["action_tstamp_stm"].max()
        max_item_ts = items_df["action_tstamp_stm"].max()
        self.max_timestamp = max(max_order_ts, max_item_ts)
        self.watermark_value = self.max_timestamp

        # Parse JSONB row_data for orders
        order_schema = pl.Struct({
            "order_id": pl.Utf8,
            "customer_id": pl.Utf8,
            "status_id": pl.Int64,
            "purchase_date": pl.Utf8,
            "estimated_delivery_date": pl.Utf8,
            "approved_date": pl.Utf8,
            "delivered_carrier_date": pl.Utf8,
            "delivered_customer_date": pl.Utf8
        })

        parsed_orders = orders_df.with_columns(
            pl.col("row_data").map_elements(lambda x: json.loads(x) if x else {}, return_dtype=order_schema).alias("data")
        ).unnest("data")

        # Keep latest version per order
        deduplicated_orders = (
            parsed_orders
            .sort("action_tstamp_stm")
            .unique(subset=["order_id"], keep="last")
        )

        # Parse JSONB row_data for order_items
        item_schema = pl.Struct({
            "order_id": pl.Utf8,
            "item_id": pl.Int64,
            "product_id": pl.Utf8,
            "seller_id": pl.Utf8,
            "price": pl.Float64,
            "quantity": pl.Int64,
            "freight_value": pl.Float64
        })

        parsed_items = items_df.with_columns(
            pl.col("row_data").map_elements(lambda x: json.loads(x) if x else {}, return_dtype=item_schema).alias("data")
        ).unnest("data")

        # Keep latest version per order_item
        deduplicated_items = (
            parsed_items
            .sort("action_tstamp_stm")
            .unique(subset=["order_id", "item_id"], keep="last")
        )

        # Join orders and items
        fact = deduplicated_items.join(deduplicated_orders, on="order_id", how="inner")

        # Load dimensions for lookups
        dim_customer = self.entity_map.get("datawarehouse.dim_customer")
        dim_product = self.entity_map.get("datawarehouse.dim_product")
        dim_seller = self.entity_map.get("datawarehouse.dim_seller")
        dim_order_status = self.entity_map.get("datawarehouse.dim_order_status_type")
        dim_location = self.entity_map.get("datawarehouse.dim_location")

        # Filter current records for SCD2 dimensions
        if dim_customer is not None and not dim_customer.is_empty():
            dim_customer_current = dim_customer.filter(pl.col("is_current") == True)
            fact = fact.join(
                dim_customer_current.select(["customer_sk", "customer_id", "customer_zip_code", "customer_city", "customer_state"]),
                on="customer_id",
                how="left"
            )
        else:
            fact = fact.with_columns(
                pl.lit(None).cast(pl.Int32).alias("customer_sk"),
                pl.lit(None).alias("customer_zip_code"),
                pl.lit(None).alias("customer_city"),
                pl.lit(None).alias("customer_state")
            )

        if dim_product is not None and not dim_product.is_empty():
            dim_product_current = dim_product.filter(pl.col("is_current") == True)
            fact = fact.join(
                dim_product_current.select(["product_sk", "product_id"]),
                on="product_id",
                how="left"
            )
        else:
            fact = fact.with_columns(pl.lit(None).cast(pl.Int32).alias("product_sk"))

        if dim_seller is not None and not dim_seller.is_empty():
            dim_seller_current = dim_seller.filter(pl.col("is_current") == True)
            fact = fact.join(
                dim_seller_current.select(["seller_sk", "seller_id"]),
                on="seller_id",
                how="left"
            )
        else:
            fact = fact.with_columns(pl.lit(None).cast(pl.Int32).alias("seller_sk"))

        # Lookup order_status_sk (SCD1, no is_current filter needed)
        if dim_order_status is not None and not dim_order_status.is_empty():
            # Need to map status_id to order_status_type_code first
            # Assuming status_id maps to order_status_type_code somehow
            # For now, we'll use a simple mapping or skip this lookup
            fact = fact.with_columns(pl.lit(None).cast(pl.Int32).alias("order_status_sk"))
        else:
            fact = fact.with_columns(pl.lit(None).cast(pl.Int32).alias("order_status_sk"))

        # Lookup location_sk based on customer location
        if dim_location is not None and not dim_location.is_empty():
            fact = fact.join(
                dim_location.select(["location_sk", "zip_code_prefix", "city", "state"]),
                left_on=["customer_zip_code", "customer_city", "customer_state"],
                right_on=["zip_code_prefix", "city", "state"],
                how="left"
            )
        else:
            fact = fact.with_columns(pl.lit(None).cast(pl.Int32).alias("location_sk"))

        # Calculate date_id from purchase_date
        fact = fact.with_columns(
            pl.col("purchase_date").str.to_datetime("%Y-%m-%d %H:%M:%S", strict=False).alias("purchase_date_dt")
        )

        # Select final columns
        self.final_df = fact.select([
            pl.col("order_id").cast(pl.Utf8),
            pl.col("customer_sk").cast(pl.Int32),
            pl.col("product_sk").cast(pl.Int32),
            pl.col("seller_sk").cast(pl.Int32),
            pl.col("order_status_sk").cast(pl.Int32),
            pl.col("location_sk").cast(pl.Int32),
            pl.col("purchase_date_dt").dt.strftime("%Y%m%d").cast(pl.Int32, strict=False).alias("date_id"),
            pl.col("price").cast(pl.Float64),
            pl.col("freight_value").cast(pl.Float64),
            pl.col("quantity").cast(pl.Int32),
            (pl.col("price") * pl.col("quantity")).alias("total_item_price"),
            pl.col("freight_value").alias("total_freight"),
            pl.col("purchase_date_dt").alias("purchase_date"),
            pl.col("approved_date").str.to_datetime("%Y-%m-%d %H:%M:%S", strict=False).alias("approved_date"),
            pl.col("delivered_carrier_date").str.to_datetime("%Y-%m-%d %H:%M:%S", strict=False).alias("delivered_carrier_date"),
            pl.col("delivered_customer_date").str.to_datetime("%Y-%m-%d %H:%M:%S", strict=False).alias("delivered_customer_date"),
            pl.col("estimated_delivery_date").str.to_datetime("%Y-%m-%d %H:%M:%S", strict=False).alias("estimated_delivery_date")
        ])