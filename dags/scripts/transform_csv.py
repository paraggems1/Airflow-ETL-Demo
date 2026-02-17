import csv
import os
import logging

# Airflow automatically captures Python logging output
logger = logging.getLogger(__name__)

def transform_sales():

    input_file = "/opt/airflow/dags/data/raw/sales_raw.csv"
    output_file = "/opt/airflow/dags/data/curated/sales_curated.csv"

    logger.info("Starting sales transformation")
    logger.info(f"Input file: {input_file}")
    logger.info(f"Output file: {output_file}")

    # ensure curated folder exists
    os.makedirs("/opt/airflow/dags/data/curated", exist_ok=True)

    row_count = 0

    try:
        with open(input_file, "r") as infile, open(output_file, "w", newline="") as outfile:

            reader = csv.DictReader(infile)
            fieldnames = ["id","name","amount","amount_with_tax"]

            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for r in reader:
                amount = int(r["amount"])
                amount_with_tax = int(amount * 1.1)

                writer.writerow({
                    "id": r["id"],
                    "name": r["name"].upper(),
                    "amount": amount,
                    "amount_with_tax": amount_with_tax
                })

                row_count += 1

        logger.info(f"Transformation completed successfully. Rows processed: {row_count}")

    except Exception as e:
        logger.error("Transformation failed", exc_info=True)
        raise