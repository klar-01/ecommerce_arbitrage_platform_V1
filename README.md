# ⚡ Platform Dynamic Pricing & E-Commerce Arbitrage V1

## 📌 Architecture V1 & Pipeline End-to-End

```
[eBay Buy/Browse API] (Annonces actives & Ventes passées)
         │
         ▼
[Nettoyage & Feature Engineering]
   ├── SBERT / Regex (Modèle exact, Condition: Used/New/Parts)
   ├── Métriques vendeur (Feedback score, Top Rated)
   └── Frais d'expédition & taxes
         │
         ▼
[Modèle LightGBM / CatBoost] ──> Projection du prix cible (médiane & intervalles 10%-90%)
         │
         ▼
[Moteur d'Arbitrage (Heuristique + Filtre de marge)]
   ├── Marge nette = Prix marché projeté - (Prix achat + Port + Frais eBay ~13% + Marge cible)
   └── Score de vélocité (Ratio Sold / Active listings)
         │
         ▼
[Dashboard d'Alertes Streamlit V1] (Port 8502 & Cassandra DB)
```

## 🚀 Ports d'Écoute V1 (Zéro Conflit avec V0)
- **Streamlit Dashboard V1** : http://localhost:8502
- **Airflow Webserver V1** : http://localhost:8086 (Identifiants : `admin` / `admin`)
- **Spark Master UI V1** : http://localhost:8082
- **Kafka Broker V1** : `localhost:29093` / `kafka-v1:9093`
- **Cassandra NoSQL V1** : `localhost:9043`

## 🛠️ Démarrage Rapide

```bash
docker-compose up -d
```
