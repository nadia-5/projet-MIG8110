from proct_olis.core.transformation import TransformationBase
import polars as pl

class Transformation(TransformationBase):
    process_name: str = "Order Status Type (Static Reference)"

    def transformation(self):
        # ✅ HARDCODE ALL Olist statuses (independent of daily data)
        ALL_STATUSES = [
            (1, "created", "Order created"),
            (2, "approved", "Order approved"),
            (3, "invoiced", "Order invoiced"), 
            (4, "processing", "Order processing"),
            (5, "shipped", "Order shipped"),
            (6, "delivered", "Order delivered"),
            (7, "unavailable", "Order unavailable"),
            (8, "canceled", "Order canceled")
        ]
        
        self.final_df = pl.DataFrame({
            "order_status_type_id": [row[0] for row in ALL_STATUSES],
            "order_status_type_code": [row[1] for row in ALL_STATUSES],
            "order_status_type_description": [row[2] for row in ALL_STATUSES],
            "inserted_at": [self.execution_date] * len(ALL_STATUSES)
        })
        
        print(f"✅ Loaded {self.final_df.height} STATIC order statuses (IDs 1-8)")
