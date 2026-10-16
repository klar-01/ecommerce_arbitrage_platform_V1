from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'data_engineer_v1',
    'depends_on_past': False,
    'start_date': datetime(2026, 10, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def task_extract_sold_listings():
    print(" [1/4] Extraction des ventes passées eBay (Sold listings)...")
    return True

def task_feature_engineering_nlp():
    print(" [2/4] Traitement NLP SBERT/Regex (Modèle exact, Condition: Used/New/Parts)...")
    return True

def task_train_lightgbm_catboost():
    print(" [3/4] Entraînement du modèle LightGBM / CatBoost (Médiane & Bornes 10%-90%)...")
    return True

def task_benchmark_and_promote():
    print(" [4/4] Évaluation R2/RMSE et mise à jour du modèle actif...")
    return True

dag = DAG(
    'airflow_lightgbm_retrain_v1',
    default_args=default_args,
    description='DAG MLOps V1: Ré-entraînement quotidien LightGBM / CatBoost avec données d\'arbitrage eBay',
    schedule_interval='0 2 * * *', # Daily at 02:00 AM
    catchup=False
)

t1 = PythonOperator(task_id='extract_sold_listings', python_callable=task_extract_sold_listings, dag=dag)
t2 = PythonOperator(task_id='feature_engineering_nlp', python_callable=task_feature_engineering_nlp, dag=dag)
t3 = PythonOperator(task_id='train_lightgbm_catboost', python_callable=task_train_lightgbm_catboost, dag=dag)
t4 = PythonOperator(task_id='benchmark_and_promote', python_callable=task_benchmark_and_promote, dag=dag)

t1 >> t2 >> t3 >> t4
