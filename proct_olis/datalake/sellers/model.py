from proct_olis.core import TransformationBase 


class Transformation(TransformationBase):
    process_name: str = "Sellers Datalake Process"

    def transformation(self):
        orders_df = self.entity_map.get("datalake.orders")
        order_items_df = self.entity_map.get("datalake.order_items")
        sellers_df = self.entity_map.get("datalake.sellers")

        daily_order_items = order_items_df.filter(
            order_items_df["order_id"].is_in(orders_df["order_id"].unique())
        )

        daily_sellers = sellers_df.filter(
            sellers_df["seller_id"].is_in(daily_order_items["seller_id"].unique())
        )

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = daily_sellers