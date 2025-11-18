from proct_olis.core import TransformationBase 
import polars.functions as F 
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "geolocation Datalake Process"

    def transformation(self):
        geolocation_df = self.entity_map.get("datalake.geolocation")

        self.final_df = geolocation_df