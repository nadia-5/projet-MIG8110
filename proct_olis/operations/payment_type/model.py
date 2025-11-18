from proct_olis.core import TransformationBase 


class Transformation(TransformationBase):
    process_name: str = "Payment Type Transactional Database Process"

    def transformation(self):
        payment_type_df = self.entity_map.get("datalake.order_payments").unique()

        self.final_df = self.utilities.add_primary_key(payment_type_df, "auto", self.config.destination.primary_key, self.config.destination.business_keys)