from proct_olis.core import TransformationBase
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Order Payment Transactional Database Process"

    def transformation(self):

        # ---------- 1. Lire order_payments depuis le datalake ----------
        df = self.entity_map.get("datalake.order_payments")

        # ---------- 2. Lire payment_type depuis l'opérationnel ----------
        payment_type_df = self.entity_map.get("operational.payment_type")

        # ---------- 3. Join pour retrouver le payment_type_id ----------
        df = (
            df.join(
                payment_type_df,
                left_on="payment_type_code",
                right_on="payment_type_code",
                how="left",
            )
        )

        # ---------- 4. Sélection + conformisation ----------
        df = (
            df.select(
                pl.col("order_id"),
                pl.col("payment_seq"),
                pl.col("payment_type_id"),
                pl.col("installments"),
                pl.col("value"),
            )

        )

        self.final_df = df
