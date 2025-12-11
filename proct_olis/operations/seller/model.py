from proct_olis.core.transformation import TransformationBase 
import polars as pl
import uuid

class Transformation(TransformationBase):
    process_name: str = "Seller Transactional Database Process"

    CITY_MAP = {
        "trajano de morais": "trajano de moraes",
        "senador la roque": "senador la rocque",
        "buritirana": "buritirama",
        "estrela d oeste": "estrela d’oeste",
        "estrela doeste": "estrela d’oeste",
    }

    def transformation(self):
        self.final_df = self.entity_map.get("datalake.sellers").select(
            # 1. Normalize UUID (Fixes duplicate key error)
            pl.col("seller_id")
              .map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8)
              .alias("seller_id"),
            
            # 2. Cast Zip Code to String (Fixes 'cannot compare string with numeric' error)
            pl.col("seller_zip_code").cast(pl.Utf8).alias("seller_zip_code"),
            
            pl.col("seller_city").str.to_lowercase().map_elements(self.utilities.remove_accents).alias("seller_city"),
            pl.col("seller_state").str.to_lowercase().alias("seller_state"),
        ).with_columns(
            pl.col("seller_city").replace(self.CITY_MAP, default=pl.col("seller_city")).alias("seller_city")
        )