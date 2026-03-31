import argparse
import logging
import os
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, count, rank, expr
from pyspark.sql.window import Window

# Configuration des logs pour le traitement
logging.basicConfig(filename='processor.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def init_spark():
    return SparkSession.builder \
        .appName("OlistProcessor") \
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
        .getOrCreate()

def process_silver(spark, raw_dir, silver_dir):
    logging.info("Démarrage du traitement SilverLayer")
    
    try:
        # Chargement des couches Raw
        cust = spark.read.parquet(os.path.join(raw_dir, "olist_customers_dataset"))
        ord = spark.read.parquet(os.path.join(raw_dir, "olist_orders_dataset"))
        pay = spark.read.parquet(os.path.join(raw_dir, "olist_order_payments_dataset"))
        items = spark.read.parquet(os.path.join(raw_dir, "olist_order_items_dataset"))
        
        # Validation métier : 5 règles de nettoyage
        ord = ord.filter((col("order_status") == "delivered") & col("order_purchase_timestamp").isNotNull())
        pay = pay.filter(col("payment_value") > 0)
        items = items.filter(col("price") > 0)
        cust = cust.filter(col("customer_id").isNotNull())
        
        # Consolidation des données
        merged = ord.join(cust, "customer_id", "inner") \
                    .join(items, "order_id", "inner")

        # Utilisation de .cache() pour l'optimisation
        merged.cache()
        logging.info("Mise en cache du DataFrame de travail consolidé")
        
        # Agrégation : Ventes par commande et état
        orders_totals = merged.groupBy("order_id", "customer_unique_id", "customer_state").agg(
            spark_sum("price").alias("order_revenue"),
            count("product_id").alias("item_count")
        )

        # Window Function : Classement des meilleurs acheteurs par État
        buying_power = orders_totals.groupBy("customer_unique_id", "customer_state").agg(
            spark_sum("order_revenue").alias("lifetime_revenue")
        )
        
        window = Window.partitionBy("customer_state").orderBy(col("lifetime_revenue").desc())
        ranked = buying_power.withColumn("state_rank", rank().over(window))
        
        # Partitionnement Silver
        now = datetime.now()
        for col_name, value in [("year", now.year), ("month", now.month), ("day", now.day)]:
            ranked = ranked.withColumn(col_name, expr(str(value)))
            merged = merged.withColumn(col_name, expr(str(value)))

        # Exportation SilverLayer
        ranked.write.partitionBy("year", "month", "day").mode("overwrite").parquet(os.path.join(silver_dir, "customer_rankings"))
        merged.write.partitionBy("year", "month", "day").mode("overwrite").parquet(os.path.join(silver_dir, "order_items"))
        
        logging.info(f"Traitement SilverLayer terminé avec succès dans {silver_dir}")
        
    except Exception as e:
        logging.error(f"Erreur fatale au niveau du Processor Layer: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, help="Dossier source Raw layer")
    parser.add_argument("--silver", required=True, help="Dossier destination Silver layer")
    args = parser.parse_args()

    spark = init_spark()
    process_silver(spark, args.raw, args.silver)
    spark.stop()
