# Rapport Final & Présentation — Plateforme d'Arbitrage E-Commerce V1

---

## 📄 Slide 1 : Page de Garde
**Titre :** Conception & Déploiement d'une Plateforme Big Data & ML pour l'Arbitrage E-commerce (V1)
**Objectif :** Détection automatisée d'opportunités d'achat-revente rentables sur eBay.
**Composants Clés :** Ingestion Streaming, Feature Engineering SBERT/Regex, Régression Quantile LightGBM, Moteur de Marge Nette.
**Environnement :** Docker (Kafka, Cassandra, Streamlit, Airflow).

---

## 📄 Slide 2 : Résumé Exécutif (Executive Summary)
**La Vision :**
Sur des places de marché comme eBay, des milliers d'articles sont mis en vente chaque jour à des prix sous-évalués en raison d'erreurs d'estimation des vendeurs, de descriptions incomplètes ou d'un besoin de liquidité immédiate.
**La Solution V1 :**
La plateforme d'arbitrage V1 est un moteur de traitement en temps quasi-réel qui aspire 30 annonces cibles par produit, nettoie leurs données (NLP), évalue leur véritable valeur de marché via l'Intelligence Artificielle (LightGBM), déduit mathématiquement l'ensemble des frais de revente (13.25%), et pousse les opportunités de profit garanties vers un Dashboard pour action humaine immédiate.

---

## 📄 Slide 3 : Contexte & La Problématique de l'Arbitrage
L'arbitrage e-commerce est le processus qui consiste à acheter un actif sur un marché (ex. annonce mal titrée) pour le revendre immédiatement sur le même marché (avec un titre clair) ou sur un autre marché à un prix supérieur.
**Les Défis Techniques :**
1. **Bruit Textuel :** Les vendeurs nomment mal leurs produits (ex: *Advantech PC* au lieu de *MIC-770H-20A1*).
2. **Coûts Cachés :** Ignorer les frais de port, de taxes et les 13.25% de commission eBay conduit à des marges négatives.
3. **Risque de Liquidité :** Acheter un produit pas cher est inutile s'il faut 6 mois pour le revendre.

---

## 📄 Slide 4 : Objectifs Technologiques de la Version V1
Pour surmonter ces défis, la V1 de la plateforme a implémenté le socle Big Data suivant :
- **Automatisation Totale de l'Ingestion** : Suppression du scraping manuel via l'API officielle REST.
- **Micro-Services & Conteneurisation** : Architecture 100% isolée via Docker pour éviter les conflits systèmes.
- **Rigueur Financière** : Intégration d'un Moteur de Calcul Financier pour rejeter toute fausse bonne affaire.
- **Sécurité et Contrôle** : Dashboard interactif protégé par mots de passe ("admin123") avec filtrage stricte (Catégorie ➡️ Produit).

---

## 📄 Slide 5 : Architecture Globale Big Data & Docker
L'architecture repose sur un pipeline de données en streaming (Streaming Data Pipeline) découplé.
*   **Port 8086 :** Apache Airflow (Orchestration des DAGs de recherche).
*   **Port 9093 :** Apache Kafka (Message Broker pour le transit des données brutes).
*   **Port 2182 :** Zookeeper (Gestion du cluster Kafka).
*   **Port 9043 :** Apache Cassandra (Base NoSQL orientée colonnes pour le stockage ultra-rapide des alertes).
*   **Port 8502 :** Streamlit Dashboard (Interface Analytique).

Ce découplage permet au système de scaler indépendamment l'ingestion, le calcul et l'affichage.

---

## 📄 Slide 6 : Étape 1 - L'Ingestion des Données via API eBay
*Composant : `ebay_api_producer.py`*
- La plateforme utilise l'API `eBay Buy/Browse` pour récupérer les **Active Listings** (pour chercher les achats potentiels) et les **Sold Listings** (pour analyser les ventes historiques).
- **Batch Processing :** Le système est configuré pour ingérer des lots de **30 articles simultanément** par produit. Cela garantit une base d'échantillonnage suffisante pour les algorithmes statistiques.
- Les données brutes (Titre, Condition, Prix, Port) sont packagées en JSON et envoyées au broker Kafka.

---

## 📄 Slide 7 : Étape 2 - L'Approche Streaming avec Kafka
*Composant : `kafka-v1` (Topic: `ebay-raw-listings`)*
Pourquoi Kafka ?
Dans un système d'arbitrage en temps réel, l'ingestion de milliers d'annonces API peut paralyser la base de données. Kafka agit comme un "tampon" (buffer) élastique.
Les annonces eBay arrivent dans le Topic Kafka. Le moteur ML consomme ces messages à son propre rythme (Asynchronous Processing). Cela garantit qu'**aucune donnée d'opportunité n'est perdue**, même lors de pics de trafic.

---

## 📄 Slide 8 : Étape 3 - Nettoyage NLP et Normalisation textuelle
*Composant : `feature_engineering.py`*
Les titres eBay sont chaotiques. Le système applique des expressions régulières (Regex) avancées et des transformateurs SBERT (Sentence-BERT).
**Objectifs de cette étape :**
- **Extraction du MPN (Manufacturer Part Number) :** Garantir que nous comparons des "pommes avec des pommes".
- **Nettoyage du bruit :** Retirer les termes marketing inutiles ("FAST SHIPPING", "L@@K", "MINT").

---

## 📄 Slide 9 : Étape 4 - Feature Engineering & Indicateurs
La plateforme traduit le contexte non-structuré en variables mathématiques (Features) :
1. **Condition Grade (État physique) :**
   - Brand New = Coefficient 1.00
   - Refurbished = Coefficient 0.85
   - Used = Coefficient 0.70
   - For Parts = Coefficient 0.35
2. **Trust Score (Confiance Vendeur) :** Calculé via le logarithme du nombre de feedbacks combiné au pourcentage d'évaluations positives, afin de pénaliser le risque d'arnaque.

---

## 📄 Slide 10 : Étape 5 - Modélisation ML avec LightGBM Quantile
*Composant : `lightgbm_pricing_model.py`*
Au lieu d'utiliser une simple moyenne de prix (qui est faussée par les valeurs extrêmes), la plateforme utilise une **Régression Quantile via LightGBM et CatBoost**.
- **Quantile 50% (Médiane) :** Définit le "Juste Prix de Marché" (Fair Price). C'est le prix de revente projeté de manière conservatrice.
- **Quantile 10% (Borne Basse) et 90% (Borne Haute) :** Définissent l'intervalle de confiance. Un intervalle très large indique une forte volatilité, un intervalle resserré indique une opportunité très sûre.

---

## 📄 Slide 11 : Étape 6 - Le Moteur Financier d'Arbitrage (Le Coeur)
*Composant : `arbitrage_engine.py`*
Le modèle calcule strictement la Marge Nette selon cette formule :
**Marge Nette** = Juste Prix Projeté (ML) - Coût Total d'Acquisition.
**Coût Total** = Prix de l'annonce + Frais de port + Frais de Commission eBay (13.25% du prix de vente + $0.30) + Taxes (si applicables).
Si la Marge Nette est inférieure au *Target Margin* (ex: 20% de profit), l'opportunité est ignorée.

---

## 📄 Slide 12 : Étape 7 - La Métrique de Risque (Score de Vélocité)
*Ratio Sell-Through*
Une forte marge n'est intéressante que si le produit se revend vite.
**Formule de Vélocité :** `Nombre d'objets vendus (Sold) / Nombre d'objets actifs (Active)`
- Un ratio > 1.0 signifie qu'il y a plus de demande que d'offre (Marché Haussier, revente très rapide).
- Un ratio < 0.2 signifie que le produit est stagnant. L'opportunité est rejetée pour cause de risque d'illiquidité.

---

## 📄 Slide 13 : Étape 8 - Persistance via Cassandra (Base NoSQL)
*Composant : `cassandra-v1` (Keyspace: `arbitrage_platform`)*
Toutes les opportunités filtrées et jugées valides sont insérées en une milliseconde dans Apache Cassandra.
**Conception du Schéma de données (Data Modeling) :**
`PRIMARY KEY ((category), arbitrage_score, product_id, timestamp)`
Cette clé de partition permet de regrouper physiquement sur le disque toutes les alertes d'une même "Catégorie" et de les pré-trier directement par "Score d'arbitrage décroissant", offrant des temps de réponse sub-millisecondes pour le Dashboard.

---

## 📄 Slide 14 : Étape 9 - Le Dashboard V1 & Analyse Comparative
*Composant : `app.py` (Port 8502)*
L'outil d'exploitation (Streamlit) offre les fonctionnalités suivantes :
- **Analyse de lot 30 items :** Comparaison instantanée via des nuages de points (Scatter Plot : Achat vs Fair Price).
- **Navigation Intelligente :** Cascade filtrée "Catégorie -> Produit" (ex: Industrial -> MIC-770H).
- **Exécution Directe :** Intégration de liens officiels cliquables redirigeant instantanément vers l'URL de l'annonce sur eBay pour acheter l'article avant la concurrence.

---

## 📄 Slide 15 : Bilan, Succès de la V1 et Perspectives (V2)
**Succès Actuels :**
- L'infrastructure Big Data complète tourne sans aucun conflit de port sur l'environnement.
- Les biais mathématiques (oubli des frais de port/eBay) sont totalement éradiqués.
**Perspectives Futures :**
- **Orchestration Automatisée :** Activation d'Airflow pour planifier des tâches cron automatiques chaque heure (Schedule /5 min).
- **Scaling ML :** Déploiement de modèles Deep Learning NLP plus massifs.
- **Alerting Push :** Envoi automatique des alertes validées par Telegram/Discord.

---
**Fin du Rapport.**
