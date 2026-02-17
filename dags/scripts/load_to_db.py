from airflow.providers.postgres.hooks.postgres import PostgresHook
import csv
import os
import logging

logger = logging.getLogger(__name__)

def load_curated(**context):

    execution_date = context["ds"]
    file_path = "/opt/airflow/dags/data/curated/sales_curated.csv"

    logger.info("Starting curated load to Postgres")
    logger.info(f"Execution date: {execution_date}")
    logger.info(f"Looking for file: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"Curated file missing: {file_path}")
        raise FileNotFoundError(f"Missing curated file: {file_path}")

    hook = PostgresHook(postgres_conn_id="postgres_localhost")

    create_sql = """
    CREATE TABLE IF NOT EXISTS curated_sales(
        id INT,
        name TEXT,
        amount INT,
        amount_with_tax INT,
        load_date DATE,
        PRIMARY KEY(id, load_date)
    );
    """

    delete_sql = "DELETE FROM curated_sales WHERE load_date=%s"

    insert_sql = """
    INSERT INTO curated_sales(id,name,amount,amount_with_tax,load_date)
    VALUES (%s,%s,%s,%s,%s)
    """

    try:
        with hook.get_conn() as conn:
            with conn.cursor() as cur:

                logger.info("Ensuring table exists")
                cur.execute(create_sql)

                logger.info("Deleting existing rows for execution date")
                cur.execute(delete_sql, (execution_date,))

                logger.info("Reading curated CSV")
                with open(file_path, "r") as f:
                    reader = csv.DictReader(f)

                    rows = [
                        (
                            r["id"],
                            r["name"],
                            r["amount"],
                            r["amount_with_tax"],
                            execution_date
                        )
                        for r in reader
                    ]

                logger.info(f"Inserting {len(rows)} rows into curated_sales")
                cur.executemany(insert_sql, rows)

            conn.commit()

        logger.info("Load completed successfully")

    except Exception:
        logger.error("Load to Postgres failed", exc_info=True)
        raise