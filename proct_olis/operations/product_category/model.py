from proct_olis.core.transformation import TransformationBase 
import polars as pl


class Transformation(TransformationBase):
    process_name: str = "Product Category Transactional Database Process"

    def transformation(self):
        category_translation_df = self.entity_map.get("datalake.product_category_name")
        product_df = self.entity_map.get("datalake.products").unique()

        self.final_df = (
            product_df
            .join(
                category_translation_df,
                left_on=pl.col("product_category_name"),
                right_on=pl.col("product_category_name"),
                how="left",
            )
            .select(
                pl.col("product_category_name"),
                pl.col("product_category_name_english").alias("translation_name_en"),
                pl.col("product_category_name_english").str.replace_all("_", " ").alias("product_category_description")
            )
        )