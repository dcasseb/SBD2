"""
DAG: Pipeline Principal de Crimes
Orquestra todo o fluxo de dados: Raw → Silver → Gold
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

default_args = {
    'owner': 'sbd2',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='crime_data_pipeline',
    default_args=default_args,
    description='Pipeline principal para processamento de dados de crimes',
    schedule_interval='@weekly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['crime_data', 'etl', 'main'],
) as dag:

    start = EmptyOperator(task_id='start')

    # Trigger DAG Bronze → Silver
    trigger_bronze_silver = TriggerDagRunOperator(
        task_id='trigger_bronze_silver',
        trigger_dag_id='bronze_to_silver',
        wait_for_completion=True,
        poke_interval=30,
    )

    # Trigger DAG Silver → Gold
    trigger_silver_gold = TriggerDagRunOperator(
        task_id='trigger_silver_gold',
        trigger_dag_id='silver_to_gold',
        wait_for_completion=True,
        poke_interval=30,
    )

    # Trigger DAG de Análise
    trigger_analysis = TriggerDagRunOperator(
        task_id='trigger_analysis',
        trigger_dag_id='crime_analysis',
        wait_for_completion=True,
        poke_interval=30,
    )

    end = EmptyOperator(task_id='end')

    # Definir fluxo
    start >> trigger_bronze_silver >> trigger_silver_gold >> trigger_analysis >> end
