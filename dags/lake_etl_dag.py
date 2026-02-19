from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging

from scripts.transform_csv import transform_sales
from scripts.load_to_db import load_curated

logger = logging.getLogger(__name__)

default_args = {
    "owner": "parag",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

logger.info("Loading DAG: etl_raw_to_curated_to_db_demo")

with DAG(
    dag_id="etl_raw_to_curated_to_db_demo_v03",
    default_args=default_args,
    start_date=datetime(2026,2,1),
    schedule="@daily",
    catchup=False,
    tags=["etl","lake","demo"],
) as dag:

    logger.info("Creating transform task")
    transform = PythonOperator(
        task_id="transform_raw_to_curated",
        python_callable=transform_sales
    )

    logger.info("Creating load task")
    load = PythonOperator(
        task_id="load_curated_to_postgres",
        python_callable=load_curated
    )

    logger.info("Setting task dependency: transform >> load")
    transform >> load
