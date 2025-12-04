from proct_olis.core import TransformationBase 


class Transformation(TransformationBase):
    process_name: str = "Order Payments Datalake Process"

    def transformation(self):
        orders_df = self.entity_map.get("datalake.orders")
        order_payments_df = self.entity_map.get("datalake.order_payments")

        daily_order_payments = order_payments_df.filter(
            order_payments_df["order_id"].is_in(orders_df["order_id"].unique())
        )

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = daily_order_payments