# Format de la Présentation : Plateforme d'Arbitrage E-Commerce V1

---

## I. Introduction
**Contexte & Problématique :**
Le marché du e-commerce (notamment eBay) est très dynamique mais souffre d'inefficiences : des vendeurs sous-évaluent souvent leurs produits par manque de connaissances ou besoin de liquidités. L'arbitrage consiste à repérer ces anomalies de prix pour acheter et revendre à profit.
Cependant, l'analyse manuelle est impossible à grande échelle et les coûts cachés (frais de port, commissions eBay de ~13.25%) transforment souvent de fausses bonnes affaires en pertes financières.

**Objectif du Projet :**
Concevoir et déployer une plateforme Big Data et Machine Learning bout-en-bout (V1) capable de détecter, évaluer et filtrer automatiquement les véritables opportunités d'arbitrage en temps réel.

---

## II. Architecture de la Solution
L'architecture repose sur une infrastructure micro-services 100% conteneurisée via Docker, garantissant modularité et scalabilité. Comme le prouve notre environnement de production ci-dessous, la stack est entièrement gérée via Docker Compose :

![Vue de la stack Docker](C:/Users/larabi.kdider/.gemini/antigravity/brain/3d98c104-5612-499c-af78-567914ca06ca/.user_uploaded/media_1791584314809_493af223.png)

**Détail de la Stack Déployée (`ecommerce_arbitrage_platform_v1`) :**
- **Couche Orchestration (Airflow 2.7.3) :** `airflow-webserver-v1` (Port 8086), `airflow-scheduler-v1`, appuyés par leur métabase `airflow-postgres-v1` (Port 5433).
- **Couche Streaming (Confluent 7.5.0) :** `kafka-v1` (Port 29093) géré par `zookeeper-v1` (Port 2182).
- **Couche Stockage NoSQL (Cassandra 4.1) :** `cassandra-v1` (Port 9043) optimisée pour les lectures analytiques rapides.
- **Couche Restitution (UI) :** `streamlit-dashboard-v1` (Port 8502) pour le tableau de bord interactif.
- **Couche Calcul Big Data (Spark 3.5.0) :** `spark-master-v1` (Port 4041) et `spark-worker-v1` (Port 8083), pouvant être démarrés à la demande pour les traitements massifs batch.

---

## III. Pipeline de Collecte et Ingestion
**1. Source de Données (eBay API) & Jeux de Données Historiques (CSV) :**
L'ingestion se fait de manière scriptée via l'API officielle REST d'eBay (`Buy/Browse API`) et s'appuie sur une base solide de données réelles :
- **Extraction des annonces actives (*Active Listings*) :** Pour la détection en direct des opportunités d'arbitrage.
- **Historique des ventes réelles passées (*Sold & Completed Listings*) :** Base de plus de 600 transactions réelles collectées et stockées dans 13 fichiers CSV dédiés (`data/sales_data/`), servant de vérité terrain (*Ground Truth*) pour calibrer le modèle LightGBM et évaluer la vitesse d'écoulement du stock.
- **Web Scraping Quotidien Multi-Sources (1x / jour) :** Orchestré par le DAG Airflow `airflow_daily_ebay_scraper_v1` chaque nuit à 03:00 UTC. Le scraper interroge dynamiquement la base de données Cassandra pour extraire les modèles enregistrés, puis interroge les **4 sites de référence du secteur industriel & électronique** :
  1. **AutomationDirect** (`automationdirect.com`) : Spécialiste transactionnel des PLC, VFD, moteurs, HMI et capteurs.
  2. **Radwell Canada** (`radwell.ca`) : Leader des pièces de remplacement, surplus neufs, reconditionnés et pièces obsolètes.
  3. **RS Canada** (`ca.rs-online.com`) : Grand distributeur multimarque de composants électriques et d'automatisation.
  4. **DigiKey Canada** (`digikey.ca`) : Référence pour les filtres techniques paramétriques et les prix par quantité.
  *(+ eBay Marketplace pour la comparaison des prix sur le marché secondaire).*
  Les nouvelles cotations et transactions sont immédiatement ajoutées aux fichiers CSV et synchronisées avec Cassandra DB.

**2. Ingestion en Streaming avec Kafka :**
Le producteur Python extrait les données par batch de 30 articles (pour assurer une robustesse statistique) et les publie sous format JSON dans le topic Kafka `ebay-raw-listings`. L'utilisation de Kafka permet un découplage total : l'API peut ingérer massivement sans faire saturer le reste du système.

---

## IV. Pipeline de Traitement
Le pipeline de traitement (consommateur Kafka) effectue trois tâches critiques :

**1. Nettoyage et Feature Engineering (NLP) :**
- Utilisation d'expressions régulières (Regex) et de modèles SBERT pour nettoyer les titres chaotiques et extraire le modèle exact du produit (ex: *MIC-770H-20A1*).
- Transformation de l'état (*Condition*) en scores pondérés (Brand New = 1.0, Refurbished = 0.85, Used = 0.70).

**2. Modélisation ML (LightGBM) :**
- Entraînement d'un modèle de Régression Quantile (LightGBM / CatBoost).
- Prédiction du Juste Prix Médian ($Quantile_{50\%}$) et de l'intervalle de confiance (10% - 90%) pour mesurer la volatilité.

**3. Moteur Financier d'Arbitrage :**
- Calcul de la **Marge Nette** = Juste Prix Projeté - (Prix Achat + Port + Frais eBay de 13.25%).
- Calcul du **Score de Vélocité** (Ratio Vendus / Actifs) pour évaluer la liquidité de l'article.

---

## V. Chaîne CI/CD (Intégration et Déploiement Continus)
Pour garantir la robustesse du code et des modèles en production, une chaîne CI/CD (ex: GitLab CI ou GitHub Actions) est mise en place :
- **Continuous Integration (CI) :** À chaque `git push`, exécution de tests unitaires (PyTest) sur les formules d'arbitrage et le nettoyage NLP, et vérification du code (Linting/Flake8).
- **Continuous Delivery (CD) :** Construction automatique des images Docker (`docker build`) pour les différents services (Streamlit, Kafka, Airflow, ML Worker).
- **MLOps :** Versioning du modèle LightGBM et validation automatique de ses performances de prédiction avant tout déploiement en production.

---

## VI. Résultats Obtenus
- **Plateforme Fonctionnelle et Isolée :** La V1 tourne avec succès sur son propre environnement Docker (Port 8502 pour l'UI).
- **Précision Financière :** Les biais de calcul sont éliminés grâce à l'intégration stricte des frais eBay (13.25%) et des frais de port.
- **Filtrage Intelligent à 3 Niveaux (Onglet 1) :** Sélection fluide par `Catégorie` ➡️ `État / Condition de l'Objet` (Brand New, Like New, Very Good, Used, Refurbished) ➡️ `Produit Spécifique`.
- **Ingestion Multi-Pays & Conditions en Temps Réel (Onglet 2) :** Recherche configurable sur les places de marché eBay internationales (Canada CAD, États-Unis USD, France EUR, Royaume-Uni GBP, Allemagne EUR) avec sélection de l'état de l'item.
- **Section Dédiée aux Ventes Réelles & CSV (Onglet 3) :** Intégration d'un onglet complet permettant d'explorer 570 transactions effectives, avec dispersion chronologique des prix, Boxplots selon l'état du matériel, analyse de liquidité (délai de vente en jours) et centre de téléchargement direct des 13 fichiers CSV.
- **Fiche Descriptive & Générateur d'Annonce eBay Pro (Onglet 4) :** Module de rédaction technique à haute conversion pour matériel industriel et IT. Intègre un compteur temps réel de longueur de titre SEO (limite stricte de 80 caractères pour l'algorithme Cassini), la génération automatisée des 6 sections stratégiques, la suggestion intelligente de Codes SH douaniers et l'export direct en HTML/Markdown.
- **Zone Administrateur Sécurisée (Onglet 5) :** Espace protégé pour la gestion des catégories autorisées, des identifiants API eBay et des rôles d'accès.

---

## VII. Difficultés et Solutions
1. **Difficulté :** La qualité médiocre et très variable des titres d'annonces rédigés par les vendeurs.
   **Solution :** Implémentation d'un module NLP robuste (Regex + SBERT) pour forcer l'identification exacte du produit et rejeter les faux positifs.
2. **Difficulté :** L'incertitude du marché et la volatilité des prix.
   **Solution :** Abandon d'une moyenne de prix classique au profit d'une **Régression Quantile**, offrant un intervalle de confiance pour évaluer le risque.
3. **Difficulté :** Éviter les mises à jour complexes dans Cassandra (contraintes de clés primaires).
   **Solution :** Modélisation minutieuse de la clé de partition `((category), arbitrage_score, product_id, timestamp)` pour insérer de nouvelles données chronologiques optimisées pour la lecture sans avoir à faire d'updates lourds.

---

## VIII. Compétences Acquises
Ce projet a permis de développer et consolider une stack technologique complète :
- **Data Engineering / Big Data :** Apache Kafka (Streaming), Apache Airflow (Orchestration DAGs), Apache Cassandra (Modélisation NoSQL).
- **Data Science / MLOps :** Feature Engineering textuel (NLP), Algorithmes d'arbres boostés (LightGBM/CatBoost), Régression Quantile.
- **Software Engineering & DevOps :** Architecture Micro-services, Docker / Docker-Compose, conception de chaînes CI/CD, Streamlit.
- **Expertise Métier :** Modélisation financière (Arbitrage, Marges Nettes, Liquidité).

---

## IX. Conclusion
La Plateforme d'Arbitrage E-Commerce V1 démontre avec succès la viabilité technique d'un système automatisé de détection d'opportunités. Elle réussit à fusionner le traitement de flux massifs (Kafka), la modélisation intelligente (LightGBM) et un moteur de risque financier rigoureux. 
**Perspectives :** Les prochaines étapes incluent le déploiement sur le cloud (AWS/GCP), l'activation de l'automatisation complète via Airflow, et l'intégration de Deep Learning pour l'analyse des images d'annonces.
