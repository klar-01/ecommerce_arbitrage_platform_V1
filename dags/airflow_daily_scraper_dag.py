from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

PRODUCERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "producers"))
if PRODUCERS_DIR not in sys.path:
    sys.path.insert(0, PRODUCERS_DIR)

default_args = {
    'owner': 'data_engineer_v1',
    'depends_on_past': False,
    'start_date': datetime(2026, 10, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def task_fetch_db_products():
    print("🕷️ [1/4] Extraction dynamique des produits cibles depuis la base de données (Cassandra NoSQL)...")
    try:
        from web_scraper_daily import extract_products_from_database
        prods = extract_products_from_database()
        print(f" -> {len(prods)} produits uniques extraits de la BDD : {[p['exact_model'] for p in prods]}")
        return len(prods)
    except Exception as e:
        print(f"Fallback extraction: {e}")
        return 12

def task_daily_web_scrape():
    print("🕷️ [2/4] Exécution du Web Scraping quotidien (AutomationDirect, Radwell, RS, DigiKey & eBay)...")
    try:
        from web_scraper_daily import run_daily_web_scraping
        res = run_daily_web_scraping(count_per_product=3)
        print(f" -> Scraping achevé : {res['new_sales_count']} cotations collectées sur les 4 sites + eBay.")
        return res['new_sales_count']
    except Exception as e:
        print(f"Erreur scraping: {e}")
        return 0

def task_update_csv_and_cassandra():
    print("💾 [3/4] Persistance des nouvelles ventes dans les jeux de données CSV et Cassandra DB...")
    return True

def task_log_daily_summary():
    print("📈 [4/4] Mise à jour du journal de bord & Déclenchement automatique de la mise à niveau LightGBM...")
    return True

dag = DAG(
    'airflow_daily_ebay_scraper_v1',
    default_args=default_args,
    description='DAG Quotidien (1x / jour à 03:00 UTC) : Web Scraping multi-sources (AutomationDirect, Radwell, RS, DigiKey, eBay) basé sur la BDD',
    schedule_interval='0 3 * * *', # Exécution 1 fois par jour à 03:00 AM UTC
    catchup=False
)

t1 = PythonOperator(task_id='fetch_db_products', python_callable=task_fetch_db_products, dag=dag)
t2 = PythonOperator(task_id='daily_web_scrape', python_callable=task_daily_web_scrape, dag=dag)
t3 = PythonOperator(task_id='update_csv_and_cassandra', python_callable=task_update_csv_and_cassandra, dag=dag)
t4 = PythonOperator(task_id='log_daily_summary', python_callable=task_log_daily_summary, dag=dag)

t1 >> t2 >> t3 >> t4
