from proct_olis.core import TransformationBase 


class Transformation(TransformationBase):
    process_name: str = "Products Datalake Process"

    def transformation(self):
        orders_df = self.entity_map.get("datalake.orders")
        products_df = self.entity_map.get("datalake.products")
        order_items_df = self.entity_map.get("datalake.order_items")

        daily_order_items = order_items_df.filter(
            order_items_df["order_id"].is_in(orders_df["order_id"].unique())
        )

        daily_products = daily_order_items.filter(
            daily_order_items["product_id"].is_in(products_df["product_id"].unique())
        )

        # Exemple de transformation : sélection de colonnes spécifiques et renommage
        self.final_df = daily_products