from proct_olis.core.transformation import TransformationBase 
import polars as pl
import uuid  # ⬅️ Don't forget this import

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
            # 1. Normalize IDs to standard UUID format (36 chars)
            pl.col("customer_id")
              .map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8)
              .alias("customer_id"),
            
            pl.col("customer_code")
              .map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8)
              .alias("customer_code"),

            # 2. Cast Zip Code to String (prevents type error)
            pl.col("customer_zip_code").cast(pl.Utf8).alias("customer_zip_code"),
            
            pl.col("customer_city").str.to_lowercase().map_elements(self.utilities.remove_accents).alias("customer_city"),
            pl.col("customer_state").str.to_lowercase().alias("customer_state"),
        ).with_columns(
            pl.col("customer_city").replace(self.CITY_MAP, default=pl.col("customer_city")).alias("customer_city")
        )