from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime



with DAG(
    dag_id="olis_etl_operationnel",
    start_date=datetime(2025, 11, 24),
    schedule_interval="@daily",
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    customer_etl = BashOperator(
        task_id="operations_customer",
        bash_command="transformation --module operations --transformation_name customer"
    )

    geolocation_etl = BashOperator(
        task_id="operations_geolocation",
        bash_command="transformation --module operations --transformation_name location"
    )

    order_items_etl = BashOperator(
        task_id="operations_order_items",
        bash_command="transformation --module operations --transformation_name order_item"
    )

    order_payments_etl = BashOperator(
        task_id="operations_order_payments",
        bash_command="transformation --module operations --transformation_name order_payment"
    )

    order_reviews_etl = BashOperator(
        task_id="operations_order_reviews",
        bash_command="transformation --module operations --transformation_name order_review"
    )

    order_orders_etl = BashOperator(
        task_id="operations_orders",
        bash_command="transformation --module operations --transformation_name order"
    )

    order_product_category_name_etl = BashOperator(
        task_id="operations_product_category",
        bash_command="transformation --module operations --transformation_name product_category"
    )

    order_products_etl = BashOperator(
        task_id="operations_products",
        bash_command="transformation --module operations --transformation_name product"
    )

    order_sellers_etl = BashOperator(
        task_id="operations_sellers_items",
        bash_command="transformation --module operations --transformation_name seller"
    )
    
    
    [geolocation_etl,order_products_etl] >> order_sellers_etl
    [geolocation_etl,order_products_etl] >>customer_etl
    [geolocation_etl,order_products_etl] >>order_product_category_name_etl
    [order_sellers_etl,customer_etl,order_product_category_name_etl] >> order_items_etl
    [order_sellers_etl,customer_etl,order_product_category_name_etl] >>order_reviews_etl
    [order_sellers_etl,customer_etl,order_product_category_name_etl] >>order_payments_etl
    
  
    
