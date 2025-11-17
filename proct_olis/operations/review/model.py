from proct_olis.core import TransformationBase 
import polars as pl


class Transformation(TransformationBase):
    process_name: str = "Reviews Transactional Database Process"

    def transformation(self):
        self.final_df = self.entity_map.get("datalake.order_reviews").unique()