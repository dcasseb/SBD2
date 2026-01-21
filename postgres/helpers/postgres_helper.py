"""
PostgreSQL Helper - Funções auxiliares para conexão e operações
"""

import os
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import pandas as pd


class PostgresHelper:
    """Classe auxiliar para operações com PostgreSQL"""
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 user: str = None,
                 password: str = None,
                 database: str = None):
        """
        Inicializa conexão com PostgreSQL.
        Utiliza variáveis de ambiente se parâmetros não forem fornecidos.
        """
        self.host = host or os.getenv('POSTGRES_HOST', 'localhost')
        self.port = port or int(os.getenv('POSTGRES_PORT', 5432))
        self.user = user or os.getenv('POSTGRES_USER', 'sbd2')
        self.password = password or os.getenv('POSTGRES_PASSWORD', 'sbd2_password')
        self.database = database or os.getenv('POSTGRES_DB', 'crime_data')
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexão"""
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = False):
        """Context manager para cursor"""
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Executa uma query e retorna resultados"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            return []
    
    def execute_query_df(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Executa uma query e retorna DataFrame"""
        with self.get_connection() as conn:
            return pd.read_sql(query, conn, params=params)
    
    def insert_dataframe(self, df: pd.DataFrame, table: str, schema: str = 'public'):
        """Insere DataFrame em uma tabela"""
        columns = list(df.columns)
        values = [tuple(row) for row in df.values]
        
        query = f"""
            INSERT INTO {schema}.{table} ({', '.join(columns)})
            VALUES %s
            ON CONFLICT DO NOTHING
        """
        
        with self.get_cursor() as cursor:
            execute_values(cursor, query, values)
        
        print(f"Inseridos {len(values)} registros em {schema}.{table}")
    
    def truncate_table(self, table: str, schema: str = 'public'):
        """Trunca uma tabela"""
        with self.get_cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {schema}.{table} CASCADE")
        print(f"Tabela {schema}.{table} truncada")
    
    def table_exists(self, table: str, schema: str = 'public') -> bool:
        """Verifica se tabela existe"""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            )
        """
        result = self.execute_query(query, (schema, table))
        return result[0][0] if result else False
    
    def get_table_count(self, table: str, schema: str = 'public') -> int:
        """Retorna contagem de registros"""
        query = f"SELECT COUNT(*) FROM {schema}.{table}"
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    def execute_ddl_file(self, filepath: str):
        """Executa arquivo DDL"""
        with open(filepath, 'r') as f:
            ddl = f.read()
        
        with self.get_cursor() as cursor:
            cursor.execute(ddl)
        
        print(f"DDL executado: {filepath}")


# Instância global
pg_helper = PostgresHelper()
