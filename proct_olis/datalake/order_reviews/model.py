from proct_olis.core import TransformationBase 


class Transformation(TransformationBase):
    process_name: str = "Order Reviews Datalake Process"

    def transformation(self):
        orders_df = self.entity_map.get("datalake.orders")
        order_reviews_df = self.entity_map.get("datalake.order_reviews")

        daily_order_reviews = order_reviews_df.filter(
            order_reviews_df["order_id"].is_in(orders_df["order_id"].unique())
        )

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = daily_order_reviews