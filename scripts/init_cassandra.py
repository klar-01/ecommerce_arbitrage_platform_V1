#!/usr/bin/env python3
"""
Initialisation des tables CQL dans Cassandra V1
"""
import time
from cassandra.cluster import Cluster

CASSANDRA_HOSTS = ['cassandra-v1', 'localhost', '127.0.0.1']

def init_cassandra_v1():
    print(" Connexion à Cassandra V1 pour l'initialisation du schéma...")
    session = None
    for host in CASSANDRA_HOSTS:
        try:
            cluster = Cluster([host], port=9042)
            session = cluster.connect()
            print(f" Connecté à Cassandra sur {host}")
            break
        except Exception:
            continue

    if not session:
        print(" Impossible de se connecter à Cassandra V1.")
        return

    schema_cql = """
    CREATE KEYSPACE IF NOT EXISTS ecommerce_arbitrage
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

    USE ecommerce_arbitrage;

    CREATE TABLE IF NOT EXISTS arbitrage_alerts (
        category text,
        arbitrage_score double,
        product_id text,
        timestamp timestamp,
        title text,
        brand text,
        exact_model text,
        condition_grade text,
        listing_price double,
        predicted_price double,
        price_min_interval double,
        price_max_interval double,
        ebay_fees double,
        shipping_fee double,
        profit_margin_pct double,
        sales_velocity_score double,
        seller_id text,
        seller_feedback_score int,
        seller_feedback_pct double,
        is_top_rated_seller boolean,
        listing_url text,
        status text,
        PRIMARY KEY ((category), arbitrage_score, product_id, timestamp)
    ) WITH CLUSTERING ORDER BY (arbitrage_score DESC, product_id ASC, timestamp DESC);
    """

    for statement in schema_cql.split(';'):
        stmt = statement.strip()
        if stmt:
            try:
                session.execute(stmt)
            except Exception as e:
                print(f"Avertissement CQL : {e}")

    print(" Schéma Cassandra V1 initialisé avec succès !")

if __name__ == "__main__":
    init_cassandra_v1()
