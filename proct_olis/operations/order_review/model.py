from proct_olis.core import TransformationBase 
import polars as pl


class Transformation(TransformationBase):
    process_name: str = "Reviews Transactional Database Process"

    def transformation(self):
        order_review_df = self.entity_map.get("datalake.order_reviews")

        self.final_df = (
            order_review_df
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
                    pl.col("review_id").str.slice(0, 8) + "-" +
                    pl.col("review_id").str.slice(8, 4) + "-" +
                    pl.col("review_id").str.slice(12, 4) + "-" +
                    pl.col("review_id").str.slice(16, 4) + "-" +
                    pl.col("review_id").str.slice(20, 12)
                ).alias("review_id")
            )
        )