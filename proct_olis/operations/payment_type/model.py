from proct_olis.core.transformation import TransformationBase
import polars as pl


class Transformation(TransformationBase):
    process_name: str = "Payment Type Transactional Database Process"

    def transformation(self):
        # Read from datalake.order_payments (already mapped to payment_type_code)
        payments_df = self.entity_map.get("datalake.order_payments")

        # If no payments this day → nothing to insert
        if payments_df is None or payments_df.is_empty():
            self.final_df = pl.DataFrame()
            return

        # Use the existing column name in your parquet: payment_type_code
        payment_types = payments_df.select("payment_type_code").unique()

        # Map codes → IDs (adjust if you want different IDs)
        payment_mapping = {
            "credit_card": 1,
            "boleto": 2,
            "voucher": 3,
            "debit_card": 4,
            "not_defined": 5,
        }

        codes = payment_types["payment_type_code"].to_list()

        self.final_df = pl.DataFrame(
            {
                "payment_type_id": [payment_mapping.get(c, 999) for c in codes],
                "payment_type_code": codes,
                "payment_type_description": [f"Payment {c}" for c in codes],
                # inserted_at is added by the writer for operational tables [file:13]
            }
        )
