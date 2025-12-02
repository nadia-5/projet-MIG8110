from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="olis_etl_datalake",
    start_date=datetime(2025, 11, 18),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    customer_etl = BashOperator(
        task_id="datalake_customer",
        bash_command="transformation --module datalake --transformation_name customers"
    )

    geolocation_etl = BashOperator(
        task_id="datalake_geolocation",
        bash_command="transformation --module datalake --transformation_name geolocation"
    )

    order_items_etl = BashOperator(
        task_id="datalake_order_items",
        bash_command="transformation --module datalake --transformation_name order_items"
    )

    order_payments_etl = BashOperator(
        task_id="datalake_order_payments",
        bash_command="transformation --module datalake --transformation_name order_payments"
    )

    order_reviews_etl = BashOperator(
        task_id="datalake_order_reviews",
        bash_command="transformation --module datalake --transformation_name order_reviews"
    )

    order_orders_etl = BashOperator(
        task_id="datalake_orders",
        bash_command="transformation --module datalake --transformation_name orders"
    )

    order_product_category_name_etl = BashOperator(
        task_id="datalake_product_category_name",
        bash_command="transformation --module datalake --transformation_name product_category_name"
    )

    order_products_etl = BashOperator(
        task_id="datalake_products",
        bash_command="transformation --module datalake --transformation_name products"
    )

    order_sellers_etl = BashOperator(
        task_id="datalake_sellers_items",
        bash_command="transformation --module datalake --transformation_name sellers"
    )

    [customer_etl, geolocation_etl, order_items_etl, order_payments_etl, order_reviews_etl,
     order_orders_etl, order_product_category_name_etl, order_products_etl, order_sellers_etl]
