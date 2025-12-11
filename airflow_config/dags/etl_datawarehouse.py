from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


with DAG(
    dag_id="olis_etl_datawarehouse",
    start_date=datetime(2025, 11, 18),
    schedule_interval=timedelta(minutes=4),
    catchup=False,
    is_paused_upon_creation=False,
    tags=["olist", "datawarehouse", "analytics"]
) as dag:
    
    base_cmd = "transformation --module datawarehouse --extract_date {{ ds }}"

    # Dimensions
    dim_customer_etl = BashOperator(
        task_id="dw_dim_customer",
        bash_command=f"{base_cmd} --transformation_name dim_customer"
    )

    dim_product_etl = BashOperator(
        task_id="dw_dim_product",
        bash_command=f"{base_cmd} --transformation_name dim_product"
    )

    dim_seller_etl = BashOperator(
        task_id="dw_dim_seller",
        bash_command=f"{base_cmd} --transformation_name dim_seller"
    )

    dim_location_etl = BashOperator(
        task_id="dw_dim_location",
        bash_command=f"{base_cmd} --transformation_name dim_location"
    )

    dim_order_status_type_etl = BashOperator(
        task_id="dw_dim_order_status_type",
        bash_command=f"{base_cmd} --transformation_name dim_order_status_type"
    )

    # Table de fait
    fact_orders_etl = BashOperator(
        task_id="dw_fact_orders",
        bash_command=f"{base_cmd} --transformation_name fact_orders"
    )

    # Dépendances : toutes les dimensions doivent être chargées avant la table de fait
    [dim_customer_etl, dim_product_etl, dim_seller_etl, dim_location_etl, dim_order_status_type_etl] >> fact_orders_etl
