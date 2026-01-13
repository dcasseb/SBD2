"""
Cliente PostgreSQL para Airflow
Plugin para facilitar operações com banco de dados nas DAGs
"""

from airflow.hooks.base import BaseHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from typing import List, Dict, Any


class CrimeDataPostgresClient:
    """Cliente especializado para o banco de dados de crimes"""
    
    def __init__(self, conn_id: str = 'postgres_crime_data'):
        self.conn_id = conn_id
        self._conn = None
    
    def get_connection(self):
        """Obtém conexão do Airflow"""
        if self._conn is None:
            conn_params = BaseHook.get_connection(self.conn_id)
            self._conn = psycopg2.connect(
                host=conn_params.host,
                port=conn_params.port,
                user=conn_params.login,
                password=conn_params.password,
                database=conn_params.schema
            )
        return self._conn
    
    def close(self):
        """Fecha conexão"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def load_dimension(self, df: pd.DataFrame, table: str, key_column: str):
        """Carrega tabela de dimensão com upsert"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        columns = list(df.columns)
        values = [tuple(row) for row in df.values]
        
        # Construir query de upsert
        placeholders = ', '.join(['%s'] * len(columns))
        update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != key_column])
        
        query = f"""
            INSERT INTO gold.{table} ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT ({key_column}) DO UPDATE SET {update_set}
        """
        
        cursor.executemany(query, values)
        conn.commit()
        cursor.close()
        
        return len(values)
    
    def load_fact(self, df: pd.DataFrame, table: str = 'fato_crimes'):
        """Carrega tabela fato"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        columns = list(df.columns)
        values = [tuple(row) for row in df.values]
        
        query = f"""
            INSERT INTO gold.{table} ({', '.join(columns)})
            VALUES %s
        """
        
        execute_values(cursor, query, values, page_size=1000)
        conn.commit()
        cursor.close()
        
        return len(values)
    
    def get_dimension_keys(self, table: str, natural_key: str, surrogate_key: str) -> Dict:
        """Obtém mapeamento de chaves naturais para surrogate keys"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT {natural_key}, {surrogate_key} FROM gold.{table}")
        mapping = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.close()
        return mapping
    
    def refresh_aggregations(self):
        """Atualiza tabelas de agregação"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Agregação por área e período
        cursor.execute("""
            TRUNCATE gold.agg_crimes_area_period;
            
            INSERT INTO gold.agg_crimes_area_period
            SELECT 
                sk_area,
                EXTRACT(YEAR FROM d.full_date) as year,
                EXTRACT(MONTH FROM d.full_date) as month,
                t.period_of_day,
                COUNT(*) as total_crimes,
                SUM(CASE WHEN f.is_violent THEN 1 ELSE 0 END) as violent_crimes,
                0 as property_crimes,
                AVG(v.age_group::int) as avg_victim_age
            FROM gold.fato_crimes f
            JOIN gold.dim_date d ON f.sk_date = d.sk_date
            JOIN gold.dim_time t ON f.sk_time = t.sk_time
            JOIN gold.dim_victim v ON f.sk_victim = v.sk_victim
            GROUP BY sk_area, EXTRACT(YEAR FROM d.full_date), 
                     EXTRACT(MONTH FROM d.full_date), t.period_of_day
        """)
        
        conn.commit()
        cursor.close()
        
        return True


class LoadDimensionOperator(BaseOperator):
    """Operador customizado para carregar dimensões"""
    
    @apply_defaults
    def __init__(self,
                 csv_path: str,
                 table_name: str,
                 key_column: str,
                 conn_id: str = 'postgres_crime_data',
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_path = csv_path
        self.table_name = table_name
        self.key_column = key_column
        self.conn_id = conn_id
    
    def execute(self, context):
        client = CrimeDataPostgresClient(self.conn_id)
        df = pd.read_csv(self.csv_path)
        
        count = client.load_dimension(df, self.table_name, self.key_column)
        client.close()
        
        self.log.info(f"Carregados {count} registros em {self.table_name}")
        return count
