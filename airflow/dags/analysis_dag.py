"""
DAG: Crime Analysis
Executa análises e gera visualizações
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

default_args = {
    'owner': 'sbd2',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def generate_temporal_charts(**kwargs):
    """Gera gráficos de análise temporal"""
    df = pd.read_csv('/opt/airflow/data_layer/gold/agg_crimes_temporal.csv')
    
    output_dir = '/opt/airflow/data_layer/gold/charts'
    os.makedirs(output_dir, exist_ok=True)
    
    # Crimes por hora
    fig, ax = plt.subplots(figsize=(12, 6))
    hourly = df.groupby('hour')['total_crimes'].sum()
    ax.bar(hourly.index, hourly.values, color='steelblue')
    ax.set_xlabel('Hora do Dia')
    ax.set_ylabel('Total de Crimes')
    ax.set_title('Distribuição de Crimes por Hora')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/crimes_by_hour.png', dpi=150)
    plt.close()
    
    # Crimes por dia da semana
    fig, ax = plt.subplots(figsize=(10, 6))
    weekly = df.groupby(['day_of_week', 'day_name'])['total_crimes'].sum().reset_index()
    weekly = weekly.sort_values('day_of_week')
    ax.bar(weekly['day_name'], weekly['total_crimes'], color='coral')
    ax.set_xlabel('Dia da Semana')
    ax.set_ylabel('Total de Crimes')
    ax.set_title('Distribuição de Crimes por Dia da Semana')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/crimes_by_weekday.png', dpi=150)
    plt.close()
    
    print("Gráficos temporais gerados")


def generate_geographic_charts(**kwargs):
    """Gera gráficos de análise geográfica"""
    df = pd.read_csv('/opt/airflow/data_layer/gold/agg_crimes_by_area_year.csv')
    
    output_dir = '/opt/airflow/data_layer/gold/charts'
    os.makedirs(output_dir, exist_ok=True)
    
    # Top 10 áreas
    fig, ax = plt.subplots(figsize=(12, 8))
    top_areas = df.groupby('area_name')['total_crimes'].sum().sort_values(ascending=True).tail(10)
    ax.barh(top_areas.index, top_areas.values, color='teal')
    ax.set_xlabel('Total de Crimes')
    ax.set_title('Top 10 Áreas com Mais Crimes')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/top_areas.png', dpi=150)
    plt.close()
    
    # Crimes por ano
    fig, ax = plt.subplots(figsize=(10, 6))
    yearly = df.groupby('year')['total_crimes'].sum()
    ax.bar(yearly.index.astype(str), yearly.values, color='purple')
    ax.set_xlabel('Ano')
    ax.set_ylabel('Total de Crimes')
    ax.set_title('Total de Crimes por Ano')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/crimes_by_year.png', dpi=150)
    plt.close()
    
    print("Gráficos geográficos gerados")


def generate_victim_charts(**kwargs):
    """Gera gráficos de perfil de vítimas"""
    df = pd.read_csv('/opt/airflow/data_layer/gold/agg_victim_profile.csv')
    
    output_dir = '/opt/airflow/data_layer/gold/charts'
    os.makedirs(output_dir, exist_ok=True)
    
    # Por sexo
    fig, ax = plt.subplots(figsize=(8, 8))
    sex_counts = df.groupby('victim_sex')['total_crimes'].sum()
    ax.pie(sex_counts.values, labels=sex_counts.index, autopct='%1.1f%%')
    ax.set_title('Distribuição por Sexo da Vítima')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/victims_by_sex.png', dpi=150)
    plt.close()
    
    # Por faixa etária
    fig, ax = plt.subplots(figsize=(10, 6))
    age_counts = df.groupby('age_group')['total_crimes'].sum()
    ax.bar(age_counts.index.astype(str), age_counts.values, color='orange')
    ax.set_xlabel('Faixa Etária')
    ax.set_ylabel('Total de Crimes')
    ax.set_title('Crimes por Faixa Etária da Vítima')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/victims_by_age.png', dpi=150)
    plt.close()
    
    print("Gráficos de vítimas gerados")


with DAG(
    dag_id='crime_analysis',
    default_args=default_args,
    description='Executa análises e gera visualizações',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['crime_data', 'analysis', 'charts'],
) as dag:

    start = EmptyOperator(task_id='start')
    
    temporal_task = PythonOperator(
        task_id='generate_temporal_charts',
        python_callable=generate_temporal_charts,
        provide_context=True,
    )
    
    geographic_task = PythonOperator(
        task_id='generate_geographic_charts',
        python_callable=generate_geographic_charts,
        provide_context=True,
    )
    
    victim_task = PythonOperator(
        task_id='generate_victim_charts',
        python_callable=generate_victim_charts,
        provide_context=True,
    )
    
    end = EmptyOperator(task_id='end')
    
    start >> [temporal_task, geographic_task, victim_task] >> end
