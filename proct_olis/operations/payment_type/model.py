from proct_olis.core import TransformationBase
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Payment Type Transactional Database Process"

    def transformation(self):
        # 1. Charger la colonne renommée depuis config.yml
        df = self.entity_map.get("datalake.order_payments").select("payment_type_code").unique()
        # 2. Générer la clé primaire auto
        self.final_df = df.with_row_index(name=self.config.destination.primary_key, offset=1)


        
