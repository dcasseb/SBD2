"""
Módulo de Processamento de Dados
SBD2 - Sistemas de Banco de Dados 2
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List, Tuple


def load_crime_data(filepath: str, sample_size: Optional[int] = None) -> pd.DataFrame:
    """
    Carrega o dataset de crimes.
    
    Args:
        filepath: Caminho para o arquivo CSV
        sample_size: Número de linhas para amostragem (None para todas)
    
    Returns:
        DataFrame com os dados de crimes
    """
    if sample_size:
        df = pd.read_csv(filepath, nrows=sample_size)
    else:
        df = pd.read_csv(filepath)
    
    print(f"Dataset carregado: {df.shape[0]:,} linhas x {df.shape[1]} colunas")
    return df


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e converte colunas de data.
    
    Args:
        df: DataFrame original
    
    Returns:
        DataFrame com datas convertidas
    """
    df = df.copy()
    
    # Converter colunas de data
    date_columns = ['Date Rptd', 'DATE OCC']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    
    # Converter TIME OCC para formato de hora
    if 'TIME OCC' in df.columns:
        df['TIME OCC'] = df['TIME OCC'].astype(str).str.zfill(4)
        df['HOUR'] = df['TIME OCC'].str[:2].astype(int)
    
    return df


def handle_missing_values(df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
    """
    Trata valores ausentes no dataset.
    
    Args:
        df: DataFrame original
        strategy: 'drop' para remover, 'fill' para preencher
    
    Returns:
        DataFrame tratado
    """
    df = df.copy()
    
    if strategy == 'drop':
        # Remove linhas com valores críticos ausentes
        critical_cols = ['DR_NO', 'DATE OCC', 'Crm Cd', 'LAT', 'LON']
        df = df.dropna(subset=[c for c in critical_cols if c in df.columns])
    
    elif strategy == 'fill':
        # Preenche valores numéricos com mediana
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())
        
        # Preenche valores categóricos com 'Unknown'
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            df[col] = df[col].fillna('Unknown')
    
    return df


def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria features derivadas para análise.
    
    Args:
        df: DataFrame original
    
    Returns:
        DataFrame com novas features
    """
    df = df.copy()
    
    # Features temporais
    if 'DATE OCC' in df.columns and pd.api.types.is_datetime64_any_dtype(df['DATE OCC']):
        df['YEAR'] = df['DATE OCC'].dt.year
        df['MONTH'] = df['DATE OCC'].dt.month
        df['DAY_OF_WEEK'] = df['DATE OCC'].dt.dayofweek
        df['DAY_NAME'] = df['DATE OCC'].dt.day_name()
        df['IS_WEEKEND'] = df['DAY_OF_WEEK'].isin([5, 6]).astype(int)
    
    # Período do dia
    if 'HOUR' in df.columns:
        df['PERIOD'] = pd.cut(
            df['HOUR'],
            bins=[-1, 6, 12, 18, 24],
            labels=['Madrugada', 'Manhã', 'Tarde', 'Noite']
        )
    
    # Faixa etária da vítima
    if 'Vict Age' in df.columns:
        df['AGE_GROUP'] = pd.cut(
            df['Vict Age'],
            bins=[0, 18, 30, 45, 60, 100],
            labels=['Menor', 'Jovem', 'Adulto', 'Meia-idade', 'Idoso']
        )
    
    # Crime violento
    violent_codes = [110, 113, 121, 122, 210, 220, 230, 231, 235, 236, 250, 251]
    if 'Crm Cd' in df.columns:
        df['IS_VIOLENT'] = df['Crm Cd'].isin(violent_codes).astype(int)
    
    return df


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Gera um resumo estatístico do dataset.
    
    Args:
        df: DataFrame
    
    Returns:
        Dicionário com estatísticas
    """
    summary = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'missing_percentage': (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        'dtypes': df.dtypes.astype(str).to_dict()
    }
    
    return summary


def normalize_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza e valida coordenadas geográficas.
    
    Args:
        df: DataFrame
    
    Returns:
        DataFrame com coordenadas validadas
    """
    df = df.copy()
    
    # Remover coordenadas inválidas (0,0 ou fora de LA)
    if 'LAT' in df.columns and 'LON' in df.columns:
        valid_lat = (df['LAT'] > 33.5) & (df['LAT'] < 34.5)
        valid_lon = (df['LON'] > -119) & (df['LON'] < -117)
        df = df[valid_lat & valid_lon]
    
    return df


def encode_categorical(df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, dict]:
    """
    Codifica variáveis categóricas.
    
    Args:
        df: DataFrame
        columns: Lista de colunas para codificar
    
    Returns:
        Tuple com DataFrame codificado e dicionário de mapeamento
    """
    df = df.copy()
    encodings = {}
    
    for col in columns:
        if col in df.columns:
            df[f'{col}_encoded'] = df[col].astype('category').cat.codes
            encodings[col] = dict(enumerate(df[col].astype('category').cat.categories))
    
    return df, encodings
