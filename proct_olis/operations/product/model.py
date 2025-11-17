from proct_olis.core import TransformationBase 
import polars as pl


class Transformation(TransformationBase):
    process_name: str = "Product Transactional Database Process"

    def transformation(self):
        product_category_df = self.entity_map.get("operational.product_category")
        product_df = self.entity_map.get("datalake.products")

        self.final_df = (
            product_df
            .join(
                product_category_df,
                left_on=pl.col("product_category_name"),
                right_on=pl.col("product_category_name"),
                how="left",
            )
            .select(
                pl.col("product_id"),
                pl.col("product_category_id"),
                pl.col("name_length"),
                pl.col("description_length"),
                pl.col("photos_qty"),
                pl.col("weight_g"),
                pl.col("length_cm"),
                pl.col("height_cm"),
                pl.col("width_cm"),
            )
        )