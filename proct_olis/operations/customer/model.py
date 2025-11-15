from proct_olis.core import TransformationBase 
import polars as pl


class Transformation(TransformationBase):
    process_name: str = "Customer Transactional Database Process"

    CITY_MAP = {
        "trajano de morais": "trajano de moraes",
        "senador la roque": "senador la rocque",
        "buritirana": "buritirama",
        "estrela d oeste": "estrela d’oeste",
        "estrela doeste": "estrela d’oeste",
    }

    def transformation(self):
        self.final_df = self.entity_map.get("datalake.customers").select(
            pl.col("customer_id"),
            pl.col("customer_code"),
            pl.col("customer_zip_code"),
            pl.col("customer_city").str.to_lowercase().map_elements(self.utilities.remove_accents).alias("customer_city"),
            pl.col("customer_state").str.to_lowercase().alias("customer_state"),
        ).with_columns(
                pl.col("customer_city").replace(self.CITY_MAP, default=pl.col("customer_city")).alias("customer_city")
            )
        
