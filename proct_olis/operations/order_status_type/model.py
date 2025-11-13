from proct_olis.core import TransformationBase 


class Transformation(TransformationBase):
    process_name: str = "Order Status Type Transactional Database Process"

    def transformation(self):
        order_status_type_df = self.entity_map.get("datalake.orders").unique()

        self.final_df = self.utilities.add_primary_key(order_status_type_df, "auto", self.config.destination.primary_key, self.config.destination.business_keys)