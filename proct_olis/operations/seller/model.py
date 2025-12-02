from proct_olis.core.transformation import TransformationBase 
import polars as pl


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
            pl.col("seller_id"),
            pl.col("seller_zip_code"),
            pl.col("seller_city").str.to_lowercase().map_elements(self.utilities.remove_accents).alias("seller_city"),
            pl.col("seller_state").str.to_lowercase().alias("seller_state"),
        ).with_columns(
                pl.col("seller_city").replace(self.CITY_MAP, default=pl.col("seller_city")).alias("seller_city")
            )
        
