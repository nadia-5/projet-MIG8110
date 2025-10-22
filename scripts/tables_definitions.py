tables = [
    {
        "name": "geolocation",
        "columns": [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state"
        ],
        "primary_key": "geolocation_zip_code_prefix",
        "foreign_keys": []
    },
    {
        "name": "customers",
        "columns": [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state"
        ],
        "primary_key": "customer_id",
        "foreign_keys": [
            ("customer_zip_code_prefix", "geolocation", "geolocation_zip_code_prefix")
        ]
    },
    {
        "name": "sellers",
        "columns": [
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state"
        ],
        "primary_key": "seller_id",
        "foreign_keys": [
            ("seller_zip_code_prefix", "geolocation", "geolocation_zip_code_prefix")
        ]
    },
    {
        "name": "products",
        "columns": [
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm"
        ],
        "primary_key": "product_id",
        "foreign_keys": []
    },
    {
        "name": "orders",
        "columns": [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ],
        "primary_key": "order_id",
        "foreign_keys": [
            ("customer_id", "customers", "customer_id")
        ]
    },
    {
        "name": "order_items",
        "columns": [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value"
        ],
        "primary_key": ["order_id", "order_item_id"],
        "foreign_keys": [
            ("order_id", "orders", "order_id"),
            ("product_id", "products", "product_id"),
            ("seller_id", "sellers", "seller_id")
        ]
    },
    {
        "name": "order_payments",
        "columns": [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value"
        ],
        "primary_key": ["order_id", "payment_sequential"],
        "foreign_keys": [
            ("order_id", "orders", "order_id")
        ]
    },
    {
        "name": "order_reviews",
        "columns": [
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp"
        ],
        "primary_key": "review_id",
        "foreign_keys": [
            ("order_id", "orders", "order_id")
        ]
    }
]
