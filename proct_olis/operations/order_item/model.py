from proct_olis.core.transformation import TransformationBase 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Order Item Transactional Database Process"

    def transformation(self):

        df = self.entity_map.get("datalake.order_items")

        seller_df = self.entity_map.get("operational.seller")
        product_df = self.entity_map.get("operational.product")


        df = (
            df.join(
                seller_df,
                left_on="seller_id",
                right_on="seller_id",
                how="left",
            )
            .join(
                product_df,
                left_on="product_id",
                right_on="product_id",
                how="left",
            )
        )

        df = (
            df.select(
                [
                    pl.col("order_id").alias("order_id"),
                    pl.col("item_id").alias("item_id"),
                    pl.col("product_id").alias("product_id"),
                    pl.col("seller_id").alias("seller_id"),
                    pl.col("shipping_limit_date").alias("shipping_limit_date"),
                    pl.col("price").alias("price"),
                    pl.col("freight_value").alias("freight_value"),
                ]
            )


        )

        self.final_df = df
