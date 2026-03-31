import argparse
import logging
import os
import sqlite3
import pandas as pd
from pyspark.sql import SparkSession

# Configuration des logs pour les datamarts
logging.basicConfig(filename='datamart.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def init_spark():
    return SparkSession.builder.appName("OlistGold").getOrCreate()

def build_gold(spark, silver_dir, out_db="datamart.db"):
    logging.info("Structuration Gold Layer")
    
    try:
        rankings = spark.read.parquet(os.path.join(silver_dir, "customer_rankings"))
        orders = spark.read.parquet(os.path.join(silver_dir, "order_items"))
        
        # Datamart Dimensions
        pd_rankings = rankings.toPandas()
        
        # Datamart Faits : Revenus agrégés par date et produit
        fact_sales = orders.groupBy("order_purchase_timestamp", "product_id").agg(
            {"price": "sum"}
        ).withColumnRenamed("sum(price)", "revenue")
        pd_sales = fact_sales.toPandas()
        
        # KPIs globaux par État
        kpi_state = orders.groupBy("customer_state").agg(
            {"price": "sum", "order_id": "count"}
        ).withColumnRenamed("sum(price)", "total_sales").withColumnRenamed("count(order_id)", "sales_volume")
        pd_kpi_state = kpi_state.toPandas()

        # Exportation RDBMS SQLite
        conn = sqlite3.connect(out_db)
        pd_rankings.to_sql("dim_rankings", conn, if_exists="replace", index=False)
        pd_sales.to_sql("fact_sales", conn, if_exists="replace", index=False)
        pd_kpi_state.to_sql("kpi_state", conn, if_exists="replace", index=False)
        conn.close()
        
        logging.info(f"SQLite datamart peuplé avec succès : {out_db}")
        
    except Exception as e:
        logging.error(f"Erreur lors du build du datamart: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--silver", required=True, help="Dossier source Silver layer")
    parser.add_argument("--db", required=True, help="Chemin destination de la base SQLite")
    args = parser.parse_args()

    spark = init_spark()
    build_gold(spark, args.silver, args.db)
    spark.stop()
