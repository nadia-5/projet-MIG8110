from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime



with DAG(
    dag_id="olis_etl_operationnel",
    start_date=datetime(2025, 11, 18),
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False,
    tags=["olist", "simulation"]
) as dag:
    
    base_cmd = "transformation --module operations --extract_date {{ dag_run.conf['simulation_date'] if dag_run and dag_run.conf and 'simulation_date' in dag_run.conf else ds }}"

    customer_etl = BashOperator(
        task_id="operations_customer",
        bash_command=f"{base_cmd} --module operations --transformation_name customer"
    )

    geolocation_etl = BashOperator(
        task_id="operations_geolocation",
        bash_command=f"{base_cmd} --module operations --transformation_name location"
    )

    order_items_etl = BashOperator(
        task_id="operations_order_items",
        bash_command=f"{base_cmd} --module operations --transformation_name order_item"
    )

    order_payments_etl = BashOperator(
        task_id="operations_order_payments",
        bash_command=f"{base_cmd} --module operations --transformation_name order_payment"
    )

    order_reviews_etl = BashOperator(
        task_id="operations_order_reviews",
        bash_command=f"{base_cmd} --module operations --transformation_name order_review"
    )

    order_orders_etl = BashOperator(
        task_id="operations_orders",
        bash_command=f"{base_cmd} --module operations --transformation_name order"
    )

    order_product_category_name_etl = BashOperator(
        task_id="operations_product_category",
        bash_command=f"{base_cmd} --module operations --transformation_name product_category"
    )

    order_products_etl = BashOperator(
        task_id="operations_products",
        bash_command=f"{base_cmd} --module operations --transformation_name product"
    )

    order_sellers_etl = BashOperator(
        task_id="operations_sellers_items",
        bash_command=f"{base_cmd} --module operations --transformation_name seller"
    )

    order_order_status_type_etl = BashOperator(
        task_id="operations_order_status",
        bash_command=f"{base_cmd} --module operations --transformation_name order_status_type"
    )
    
    
    [geolocation_etl,order_products_etl] >> order_sellers_etl
    [geolocation_etl,order_products_etl] >> customer_etl
    [geolocation_etl,order_products_etl] >> order_product_category_name_etl
    [geolocation_etl,order_products_etl] >> order_order_status_type_etl
    [order_sellers_etl,customer_etl,order_product_category_name_etl] >> order_items_etl
    [order_sellers_etl,customer_etl,order_product_category_name_etl] >> order_reviews_etl
    [order_sellers_etl,customer_etl,order_product_category_name_etl] >> order_payments_etl
    
  
    
