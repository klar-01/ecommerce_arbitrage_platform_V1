-- =======================================================
-- Cassandra Schema V1: Advanced E-Commerce Arbitrage & Dynamic Pricing
-- Architecture: eBay Buy/Browse REST API -> Feature Eng -> LightGBM/CatBoost -> Arbitrage Engine -> Streamlit V1
-- =======================================================

CREATE KEYSPACE IF NOT EXISTS ecommerce_arbitrage
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE ecommerce_arbitrage;

-- 1. Table des Alertes d'Arbitrage V1 (Avec Frais eBay ~13%, Inters de Confiance LightGBM & Score de Vélocité Ratio Ventes)
CREATE TABLE IF NOT EXISTS arbitrage_alerts (
    category text,
    arbitrage_score double,          -- Gain Net ($) après déduction du Prix Achat, Port, Taxes et Frais eBay ~13%
    product_id text,
    timestamp timestamp,
    title text,
    brand text,
    exact_model text,                -- Extrait via SBERT / Regex NLP
    condition_grade text,            -- New / Used / Parts
    listing_price double,            -- Prix d'achat d'annonce
    predicted_price double,          -- Prix Cible Médiane projeté par LightGBM/CatBoost
    price_min_interval double,       -- Borne inférieure de l'intervalle de confiance (10e centile)
    price_max_interval double,       -- Borne supérieure de l'intervalle de confiance (90e centile)
    ebay_fees double,                -- Frais de commission eBay (~13%)
    shipping_fee double,             -- Frais d'expédition & port
    profit_margin_pct double,        -- ROI (%) Net après tous les frais
    sales_velocity_score double,     -- Ratio: (Sold Listings / Active Listings)
    seller_id text,
    seller_feedback_score int,       -- Score du vendeur
    seller_feedback_pct double,      -- Pourcentage d'évaluations positives vendeur
    is_top_rated_seller boolean,     -- Vendeur Top Rated sur eBay
    listing_url text,
    status text,
    PRIMARY KEY ((category), arbitrage_score, product_id, timestamp)
) WITH CLUSTERING ORDER BY (arbitrage_score DESC, product_id ASC, timestamp DESC);

-- 2. Table des Ventes Passées (Sold Listings) pour Calcul du Score de Vélocité
CREATE TABLE IF NOT EXISTS ebay_sold_listings (
    category text,
    product_id text,
    sold_date timestamp,
    title text,
    exact_model text,
    final_sold_price double,
    seller_id text,
    PRIMARY KEY ((category), product_id, sold_date)
) WITH CLUSTERING ORDER BY (product_id ASC, sold_date DESC);

-- 3. Historique des Variations de Prix & Événements
CREATE TABLE IF NOT EXISTS product_price_history (
    product_id text,
    timestamp timestamp,
    category text,
    event_type text,
    listing_price double,
    previous_price double,
    views_count int,
    condition_grade text,
    seller_id text,
    PRIMARY KEY ((product_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- 4. Métriques de Marché Agrégées (PySpark Windowing Streaming)
CREATE TABLE IF NOT EXISTS category_pricing_metrics (
    category text,
    window_start timestamp,
    window_end timestamp,
    avg_listing_price double,
    avg_predicted_price double,
    total_listings_count bigint,
    arbitrage_opportunities_count bigint,
    updated_at timestamp,
    PRIMARY KEY ((category), window_start)
) WITH CLUSTERING ORDER BY (window_start DESC);
