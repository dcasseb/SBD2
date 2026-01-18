"""
Cliente PostgreSQL
Plugin para facilitar operações com banco de dados
"""

import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from typing import List, Dict, Any


class CrimeDataPostgresClient:
    """Cliente especializado para o banco de dados de crimes"""
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 user: str = None,
                 password: str = None,
                 database: str = None):
        self.host = host or os.environ.get('POSTGRES_HOST', 'localhost')
        self.port = port or int(os.environ.get('POSTGRES_PORT', 5432))
        self.user = user or os.environ.get('POSTGRES_USER', 'sbd2')
        self.password = password or os.environ.get('POSTGRES_PASSWORD', 'sbd2_password')
        self.database = database or os.environ.get('POSTGRES_DB', 'crime_data')
        self._conn = None
    
    def get_connection(self):
        """Obtém conexão com PostgreSQL"""
        if self._conn is None:
            self._conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
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


def load_dimension_from_csv(csv_path: str, table_name: str, key_column: str, **conn_kwargs):
    """Função helper para carregar dimensão a partir de CSV"""
    client = CrimeDataPostgresClient(**conn_kwargs)
    df = pd.read_csv(csv_path)
    
    count = client.load_dimension(df, table_name, key_column)
    client.close()
    
    print(f"Carregados {count} registros em {table_name}")
    return count
