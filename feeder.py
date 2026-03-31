import argparse
import logging
import os
from datetime import datetime
from pyspark.sql import SparkSession

# Configuration des logs pour l'ingestion
logging.basicConfig(filename='feeder.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def init_spark():
    return SparkSession.builder \
        .appName("OlistFeeder") \
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
        .getOrCreate()

def ingest_data(spark, input_file, output_path):
    table = os.path.basename(input_file).replace('.csv', '')
    logging.info(f"Ingestion de la table {table}")
    
    try:
        df = spark.read.csv(input_file, header=True, inferSchema=True)
        
        # Partitionnement temporel dynamique
        now = datetime.now()
        df = df.withColumn('year', spark.sql.functions.lit(now.year)) \
               .withColumn('month', spark.sql.functions.lit(now.month)) \
               .withColumn('day', spark.sql.functions.lit(now.day))

        target = os.path.join(output_path, table)
        df.write.partitionBy("year", "month", "day").mode("append").parquet(target)
        logging.info(f"Table {table} ingérée avec succès")
        
    except Exception as e:
        logging.error(f"Erreur lors de l'ingestion de {table}: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Dossier source des fichiers CSV")
    parser.add_argument("--raw", required=True, help="Dossier destination Raw layer")
    args = parser.parse_args()

    spark = init_spark()
    
    # Tables critiques pour l'analyse Olist
    datasets = [
        "olist_customers_dataset.csv",
        "olist_orders_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_products_dataset.csv",
        "olist_order_items_dataset.csv"
    ]

    for ds in datasets:
        full_path = os.path.join(args.source, ds)
        if os.path.exists(full_path):
            ingest_data(spark, full_path, args.raw)
        else:
            logging.error(f"Fichier manquant : {full_path}")

    spark.stop()
