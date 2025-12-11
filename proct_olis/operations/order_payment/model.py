from proct_olis.core.transformation import TransformationBase 
import polars as pl
import uuid # ⬅️ ADDED: Import uuid

class Transformation(TransformationBase):
    process_name: str = "Order Payment Transactional Database Process"

    def transformation(self):

        df = self.entity_map.get("datalake.order_payments")
        payment_type_df = self.entity_map.get("operational.payment_type")

        df = (
            df.join(
                payment_type_df,
                left_on="payment_type_code",
                right_on="payment_type_code",
                how="left",
            )
        )

        df = (
            df.select(
                # ⬇️ FIX: Normalize UUID
                pl.col("order_id")
                    .map_elements(lambda x: str(uuid.UUID(x)), return_dtype=pl.Utf8)
                    .alias("order_id"),
                
                pl.col("payment_seq").cast(pl.Int32, strict=False),
                pl.col("payment_type_id").cast(pl.Int32, strict=False),
                pl.col("installments").cast(pl.Int32, strict=False),
                pl.col("value").cast(pl.Float64, strict=False),
            )

        )

        self.final_df = df