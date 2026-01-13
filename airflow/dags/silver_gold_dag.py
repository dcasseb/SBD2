"""
DAG: Silver to Gold
Transforma dados da camada Silver para Gold (Data Mart)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import pandas as pd
import os

default_args = {
    'owner': 'sbd2',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def load_to_postgres(**kwargs):
    """Carrega dados Silver para PostgreSQL"""
    import psycopg2
    from psycopg2.extras import execute_values
    
    # Conexão
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'postgres'),
        port=os.getenv('POSTGRES_PORT', 5432),
        user=os.getenv('SBD2_POSTGRES_USER', 'sbd2'),
        password=os.getenv('SBD2_POSTGRES_PASSWORD', 'sbd2_password'),
        database=os.getenv('SBD2_POSTGRES_DB', 'crime_data')
    )
    
    # Carregar dimensões
    dim_areas = pd.read_csv('/opt/airflow/data_layer/silver/dim_areas.csv')
    dim_crimes = pd.read_csv('/opt/airflow/data_layer/silver/dim_crime_types.csv')
    
    cursor = conn.cursor()
    
    # Inserir áreas
    for _, row in dim_areas.iterrows():
        cursor.execute("""
            INSERT INTO gold.dim_area (area_code, area_name)
            VALUES (%s, %s)
            ON CONFLICT (area_code) DO NOTHING
        """, (row['area_code'], row['area_name']))
    
    # Inserir tipos de crime
    for _, row in dim_crimes.iterrows():
        cursor.execute("""
            INSERT INTO gold.dim_crime_type (crime_code, crime_description)
            VALUES (%s, %s)
            ON CONFLICT (crime_code) DO NOTHING
        """, (row['crime_code'], row['crime_description']))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Dimensões carregadas no PostgreSQL")


def create_aggregations(**kwargs):
    """Cria agregações para a camada Gold"""
    silver_path = '/opt/airflow/data_layer/silver/crimes_silver.csv'
    df = pd.read_csv(silver_path, parse_dates=['DATE OCC'])
    
    # Agregação: Crimes por Área e Ano
    agg_area_year = df.groupby(['AREA', 'AREA NAME', 'YEAR']).agg({
        'DR_NO': 'count',
        'IS_VIOLENT': 'sum',
        'Vict Age': 'mean'
    }).reset_index()
    agg_area_year.columns = ['area_code', 'area_name', 'year', 'total_crimes', 'violent_crimes', 'avg_victim_age']
    agg_area_year.to_csv('/opt/airflow/data_layer/gold/agg_crimes_by_area_year.csv', index=False)
    
    # Agregação: Crimes por Tipo e Período
    agg_type_period = df.groupby(['Crm Cd', 'Crm Cd Desc', 'PERIOD']).agg({
        'DR_NO': 'count',
        'IS_VIOLENT': 'sum'
    }).reset_index()
    agg_type_period.columns = ['crime_code', 'crime_description', 'period', 'total_crimes', 'violent_crimes']
    agg_type_period.to_csv('/opt/airflow/data_layer/gold/agg_crimes_by_type_period.csv', index=False)
    
    # Agregação: Crimes por Hora e Dia da Semana
    agg_temporal = df.groupby(['HOUR', 'DAY_OF_WEEK', 'DAY_NAME']).agg({
        'DR_NO': 'count',
        'IS_VIOLENT': 'sum'
    }).reset_index()
    agg_temporal.columns = ['hour', 'day_of_week', 'day_name', 'total_crimes', 'violent_crimes']
    agg_temporal.to_csv('/opt/airflow/data_layer/gold/agg_crimes_temporal.csv', index=False)
    
    # Agregação: Perfil de Vítimas
    agg_victims = df.groupby(['Vict Sex', 'AGE_GROUP', 'Vict Descent']).agg({
        'DR_NO': 'count',
        'IS_VIOLENT': 'sum'
    }).reset_index()
    agg_victims.columns = ['victim_sex', 'age_group', 'victim_descent', 'total_crimes', 'violent_crimes']
    agg_victims.to_csv('/opt/airflow/data_layer/gold/agg_victim_profile.csv', index=False)
    
    # Agregação: Hotspots geográficos (grid de 0.01 graus)
    df['grid_lat'] = (df['LAT'] * 100).round() / 100
    df['grid_lon'] = (df['LON'] * 100).round() / 100
    
    agg_hotspots = df.groupby(['grid_lat', 'grid_lon', 'YEAR']).agg({
        'DR_NO': 'count',
        'IS_VIOLENT': 'sum'
    }).reset_index()
    agg_hotspots.columns = ['grid_lat', 'grid_lon', 'year', 'total_crimes', 'violent_crimes']
    agg_hotspots.to_csv('/opt/airflow/data_layer/gold/agg_crime_hotspots.csv', index=False)
    
    print(f"Agregações criadas: 5 tabelas")
    return True


def create_summary_report(**kwargs):
    """Cria relatório resumo"""
    silver_path = '/opt/airflow/data_layer/silver/crimes_silver.csv'
    df = pd.read_csv(silver_path, parse_dates=['DATE OCC'])
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_records': len(df),
        'date_range': {
            'start': df['DATE OCC'].min().isoformat(),
            'end': df['DATE OCC'].max().isoformat()
        },
        'total_areas': df['AREA'].nunique(),
        'total_crime_types': df['Crm Cd'].nunique(),
        'violent_crimes_pct': (df['IS_VIOLENT'].sum() / len(df) * 100),
        'top_areas': df['AREA NAME'].value_counts().head(5).to_dict(),
        'top_crimes': df['Crm Cd Desc'].value_counts().head(5).to_dict()
    }
    
    import json
    with open('/opt/airflow/data_layer/gold/summary_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print("Relatório resumo criado")
    return report


with DAG(
    dag_id='silver_to_gold',
    default_args=default_args,
    description='Transforma dados Silver para camada Gold (Data Mart)',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['crime_data', 'etl', 'silver', 'gold'],
) as dag:

    start = EmptyOperator(task_id='start')
    
    aggregations_task = PythonOperator(
        task_id='create_aggregations',
        python_callable=create_aggregations,
        provide_context=True,
    )
    
    load_postgres_task = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_to_postgres,
        provide_context=True,
    )
    
    report_task = PythonOperator(
        task_id='create_summary_report',
        python_callable=create_summary_report,
        provide_context=True,
    )
    
    end = EmptyOperator(task_id='end')
    
    start >> aggregations_task >> [load_postgres_task, report_task] >> end
