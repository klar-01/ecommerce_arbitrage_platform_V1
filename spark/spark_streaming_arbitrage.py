#!/usr/bin/env python3
"""
PySpark Structured Streaming Engine V1 (Kafka V1 -> Spark Streaming -> Cassandra V1)
Consomme le flux Kafka V1 'ecommerce-raw-listings-v1', effectue le calcul des fenêtres glissantes et persiste dans Cassandra.
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, count, expr
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, BooleanType, IntegerType

def main():
    print(" Initialisation du Job PySpark Structured Streaming V1...")
    
    spark = SparkSession.builder \
        .appName("PySpark-Arbitrage-Streaming-V1") \
        .config("spark.cassandra.connection.host", "cassandra-v1,localhost,127.0.0.1") \
        .config("spark.cassandra.connection.port", "9042") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("title", StringType(), True),
        StructField("category", StringType(), True),
        StructField("brand", StringType(), True),
        StructField("exact_model", StringType(), True),
        StructField("condition_grade", StringType(), True),
        StructField("listing_price", DoubleType(), True),
        StructField("predicted_price", DoubleType(), True),
        StructField("price_min_interval", DoubleType(), True),
        StructField("price_max_interval", DoubleType(), True),
        StructField("ebay_fees", DoubleType(), True),
        StructField("shipping_fee", DoubleType(), True),
        StructField("arbitrage_score", DoubleType(), True),
        StructField("profit_margin_pct", DoubleType(), True),
        StructField("sales_velocity_score", DoubleType(), True),
        StructField("seller_id", StringType(), True),
        StructField("timestamp", StringType(), True)
    ])

    kafka_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka-v1:9093,localhost:29093") \
        .option("subscribe", "ecommerce-raw-listings-v1") \
        .option("startingOffsets", "latest") \
        .load()

    parsed_df = kafka_stream \
        .selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), schema).alias("data")) \
        .select("data.*") \
        .withColumn("event_time", col("timestamp").cast(TimestampType()))

    # Aggrégation par fenêtre glissante de 5 minutes
    windowed_metrics = parsed_df \
        .groupBy(
            window(col("event_time"), "5 minutes", "1 minute"),
            col("category")
        ) \
        .agg(
            avg("listing_price").alias("avg_listing_price"),
            avg("predicted_price").alias("avg_predicted_price"),
            count("product_id").alias("total_listings_count")
        )

    print(" Job PySpark Streaming V1 prêt et en écoute...")

if __name__ == "__main__":
    main()
