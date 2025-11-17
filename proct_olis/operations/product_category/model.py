from proct_olis.core import TransformationBase 
import polars as pl


class Transformation(TransformationBase):
    process_name: str = "Product Category Transactional Database Process"

    def transformation(self):
        category_translation_df = self.entity_map.get("datalake.ref_product_category_name_translation")
        product_df = self.entity_map.get("datalake.products").unique()

        self.final_df = (
            product_df
            .join(
                category_translation_df,
                left_on=pl.col("product_category_name"),
                right_on=pl.col("category_name_es"),
                how="left",
            )
            .select(
                pl.col("product_category_name"),
                pl.col("category_name_en").alias("translation_name_en"),
                pl.col("category_name_en").str.replace_all("_", " ").alias("product_category_description")
            )
        )