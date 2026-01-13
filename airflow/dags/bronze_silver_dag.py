"""
DAG: Bronze to Silver
Processa dados brutos (raw) e transforma para a camada Silver
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import pandas as pd
import os

default_args = {
    'owner': 'sbd2',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def load_raw_data(**kwargs):
    """Carrega dados brutos do CSV"""
    raw_path = '/opt/airflow/data_layer/raw/crime_data/Crime_Data_from_2020_to_Present.csv'
    
    # Carregar com tipos otimizados
    dtype_dict = {
        'DR_NO': 'int64',
        'AREA': 'int32',
        'Rpt Dist No': 'int32',
        'Part 1-2': 'int32',
        'Crm Cd': 'int32',
        'Vict Age': 'float32',
        'Premis Cd': 'float32',
        'Weapon Used Cd': 'float32',
    }
    
    df = pd.read_csv(raw_path, dtype=dtype_dict, low_memory=False)
    
    # Salvar contagem para XCom
    kwargs['ti'].xcom_push(key='raw_count', value=len(df))
    
    print(f"Dados brutos carregados: {len(df):,} registros")
    return len(df)


def clean_data(**kwargs):
    """Limpa e valida os dados"""
    raw_path = '/opt/airflow/data_layer/raw/crime_data/Crime_Data_from_2020_to_Present.csv'
    
    df = pd.read_csv(raw_path, low_memory=False)
    initial_count = len(df)
    
    # Converter datas
    df['Date Rptd'] = pd.to_datetime(df['Date Rptd'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    df['DATE OCC'] = pd.to_datetime(df['DATE OCC'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    
    # Remover registros sem data de ocorrência
    df = df.dropna(subset=['DATE OCC', 'DR_NO', 'Crm Cd'])
    
    # Validar coordenadas (Los Angeles)
    df = df[(df['LAT'] > 33.5) & (df['LAT'] < 34.5)]
    df = df[(df['LON'] > -119) & (df['LON'] < -117)]
    
    # Validar idade
    df = df[(df['Vict Age'] >= 0) & (df['Vict Age'] <= 120) | (df['Vict Age'].isna())]
    
    final_count = len(df)
    removed = initial_count - final_count
    
    # Salvar temporário
    temp_path = '/opt/airflow/data_layer/silver/temp_cleaned.csv'
    df.to_csv(temp_path, index=False)
    
    print(f"Limpeza concluída: {removed:,} registros removidos ({removed/initial_count*100:.2f}%)")
    kwargs['ti'].xcom_push(key='clean_count', value=final_count)
    
    return final_count


def create_features(**kwargs):
    """Cria features derivadas"""
    temp_path = '/opt/airflow/data_layer/silver/temp_cleaned.csv'
    df = pd.read_csv(temp_path, parse_dates=['Date Rptd', 'DATE OCC'])
    
    # Features temporais
    df['YEAR'] = df['DATE OCC'].dt.year
    df['MONTH'] = df['DATE OCC'].dt.month
    df['DAY_OF_WEEK'] = df['DATE OCC'].dt.dayofweek
    df['DAY_NAME'] = df['DATE OCC'].dt.day_name()
    df['IS_WEEKEND'] = df['DAY_OF_WEEK'].isin([5, 6]).astype(int)
    
    # Hora do dia
    df['TIME OCC'] = df['TIME OCC'].astype(str).str.zfill(4)
    df['HOUR'] = df['TIME OCC'].str[:2].astype(int)
    
    # Período do dia
    def get_period(hour):
        if 0 <= hour < 6:
            return 'Madrugada'
        elif 6 <= hour < 12:
            return 'Manhã'
        elif 12 <= hour < 18:
            return 'Tarde'
        else:
            return 'Noite'
    
    df['PERIOD'] = df['HOUR'].apply(get_period)
    
    # Faixa etária
    bins = [0, 18, 30, 45, 60, 120]
    labels = ['Menor', 'Jovem', 'Adulto', 'Meia-idade', 'Idoso']
    df['AGE_GROUP'] = pd.cut(df['Vict Age'], bins=bins, labels=labels)
    
    # Crime violento
    violent_codes = [110, 113, 121, 122, 210, 220, 230, 231, 235, 236, 250, 251]
    df['IS_VIOLENT'] = df['Crm Cd'].isin(violent_codes).astype(int)
    
    # Salvar na camada Silver
    silver_path = '/opt/airflow/data_layer/silver/crimes_silver.csv'
    df.to_csv(silver_path, index=False)
    
    # Limpar temporário
    os.remove(temp_path)
    
    print(f"Features criadas: {len(df.columns)} colunas")
    kwargs['ti'].xcom_push(key='silver_count', value=len(df))
    
    return len(df)


def create_dimensions(**kwargs):
    """Cria tabelas de dimensão"""
    silver_path = '/opt/airflow/data_layer/silver/crimes_silver.csv'
    df = pd.read_csv(silver_path)
    
    # Dimensão: Áreas
    dim_areas = df[['AREA', 'AREA NAME']].drop_duplicates()
    dim_areas.columns = ['area_code', 'area_name']
    dim_areas.to_csv('/opt/airflow/data_layer/silver/dim_areas.csv', index=False)
    
    # Dimensão: Tipos de Crime
    dim_crimes = df[['Crm Cd', 'Crm Cd Desc']].drop_duplicates()
    dim_crimes.columns = ['crime_code', 'crime_description']
    dim_crimes.to_csv('/opt/airflow/data_layer/silver/dim_crime_types.csv', index=False)
    
    # Dimensão: Armas
    dim_weapons = df[['Weapon Used Cd', 'Weapon Desc']].dropna().drop_duplicates()
    dim_weapons.columns = ['weapon_code', 'weapon_description']
    dim_weapons.to_csv('/opt/airflow/data_layer/silver/dim_weapons.csv', index=False)
    
    # Dimensão: Locais
    dim_premises = df[['Premis Cd', 'Premis Desc']].dropna().drop_duplicates()
    dim_premises.columns = ['premise_code', 'premise_description']
    dim_premises.to_csv('/opt/airflow/data_layer/silver/dim_premises.csv', index=False)
    
    print(f"Dimensões criadas: Áreas={len(dim_areas)}, Crimes={len(dim_crimes)}, Armas={len(dim_weapons)}, Locais={len(dim_premises)}")


with DAG(
    dag_id='bronze_to_silver',
    default_args=default_args,
    description='Transforma dados brutos (Bronze) para camada Silver',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['crime_data', 'etl', 'bronze', 'silver'],
) as dag:

    start = EmptyOperator(task_id='start')
    
    load_task = PythonOperator(
        task_id='load_raw_data',
        python_callable=load_raw_data,
        provide_context=True,
    )
    
    clean_task = PythonOperator(
        task_id='clean_data',
        python_callable=clean_data,
        provide_context=True,
    )
    
    features_task = PythonOperator(
        task_id='create_features',
        python_callable=create_features,
        provide_context=True,
    )
    
    dimensions_task = PythonOperator(
        task_id='create_dimensions',
        python_callable=create_dimensions,
        provide_context=True,
    )
    
    end = EmptyOperator(task_id='end')
    
    start >> load_task >> clean_task >> features_task >> dimensions_task >> end
