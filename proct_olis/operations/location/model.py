from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl
class Transformation(TransformationBase):
    process_name: str = "Location Transactional Database Process"

    CITY_MAP = {
        "trajano de morais": "trajano de moraes",
        "senador la roque": "senador la rocque",
        "buritirana": "buritirama",
        "estrela d oeste": "estrela d’oeste",
        "estrela doeste": "estrela d’oeste",
    }

    def transformation(self):
        location_df = (
            self.entity_map.get("datalake.ref_geolocation")
            .select(
                pl.col("zip_code_prefix"),
                pl.col("city").str.to_lowercase().map_elements(self.utilities.remove_accents).alias("city"),
                pl.col("state").str.to_lowercase().alias("state"),
            )
            .with_columns(
                pl.col("city").replace(self.CITY_MAP, default=pl.col("city")).alias("city")
            )
            .unique()
        )

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = self.utilities.add_primary_key(location_df, "auto", self.config.destination.primary_key, self.config.destination.business_keys)