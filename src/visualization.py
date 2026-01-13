"""
Módulo de Visualização de Dados
SBD2 - Sistemas de Banco de Dados 2
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Configurações globais
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('husl')


def plot_crime_distribution(df: pd.DataFrame, 
                            column: str, 
                            top_n: int = 10,
                            figsize: Tuple[int, int] = (12, 6),
                            title: Optional[str] = None) -> plt.Figure:
    """
    Plota a distribuição de uma variável categórica.
    
    Args:
        df: DataFrame
        column: Coluna para análise
        top_n: Número de categorias para mostrar
        figsize: Tamanho da figura
        title: Título do gráfico
    
    Returns:
        Figura matplotlib
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    value_counts = df[column].value_counts().head(top_n)
    
    bars = ax.barh(range(len(value_counts)), value_counts.values)
    ax.set_yticks(range(len(value_counts)))
    ax.set_yticklabels(value_counts.index)
    ax.invert_yaxis()
    
    # Adicionar valores nas barras
    for i, (bar, val) in enumerate(zip(bars, value_counts.values)):
        ax.text(val + max(value_counts.values) * 0.01, i, f'{val:,}', 
                va='center', fontsize=9)
    
    ax.set_xlabel('Contagem')
    ax.set_title(title or f'Top {top_n} - {column}')
    
    plt.tight_layout()
    return fig


def plot_temporal_trends(df: pd.DataFrame, 
                         date_column: str,
                         figsize: Tuple[int, int] = (14, 8)) -> plt.Figure:
    """
    Plota tendências temporais de crimes.
    
    Args:
        df: DataFrame
        date_column: Coluna de data
        figsize: Tamanho da figura
    
    Returns:
        Figura matplotlib
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Crimes por mês
    monthly = df.groupby(df[date_column].dt.to_period('M')).size()
    axes[0, 0].plot(monthly.index.astype(str), monthly.values, marker='o', markersize=3)
    axes[0, 0].set_title('Crimes por Mês')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Crimes por dia da semana
    dow = df[date_column].dt.day_name().value_counts()
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow = dow.reindex(order)
    axes[0, 1].bar(dow.index, dow.values, color=sns.color_palette('husl', 7))
    axes[0, 1].set_title('Crimes por Dia da Semana')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Crimes por hora
    if 'HOUR' in df.columns:
        hourly = df.groupby('HOUR').size()
        axes[1, 0].bar(hourly.index, hourly.values, color='steelblue')
        axes[1, 0].set_title('Crimes por Hora do Dia')
        axes[1, 0].set_xlabel('Hora')
    
    # Crimes por ano
    yearly = df.groupby(df[date_column].dt.year).size()
    axes[1, 1].bar(yearly.index.astype(str), yearly.values, color='coral')
    axes[1, 1].set_title('Crimes por Ano')
    
    plt.tight_layout()
    return fig


def plot_geographic_distribution(df: pd.DataFrame,
                                  lat_col: str = 'LAT',
                                  lon_col: str = 'LON',
                                  figsize: Tuple[int, int] = (12, 10),
                                  sample_size: int = 10000) -> plt.Figure:
    """
    Plota distribuição geográfica dos crimes.
    
    Args:
        df: DataFrame
        lat_col: Coluna de latitude
        lon_col: Coluna de longitude
        figsize: Tamanho da figura
        sample_size: Tamanho da amostra para plot
    
    Returns:
        Figura matplotlib
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Amostrar dados para performance
    if len(df) > sample_size:
        df_sample = df.sample(sample_size, random_state=42)
    else:
        df_sample = df
    
    scatter = ax.scatter(
        df_sample[lon_col], 
        df_sample[lat_col],
        alpha=0.3,
        s=1,
        c='red'
    )
    
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Distribuição Geográfica dos Crimes em Los Angeles')
    
    plt.tight_layout()
    return fig


def plot_heatmap(df: pd.DataFrame, 
                 x_col: str, 
                 y_col: str,
                 figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Plota heatmap de duas variáveis categóricas.
    
    Args:
        df: DataFrame
        x_col: Coluna para eixo X
        y_col: Coluna para eixo Y
        figsize: Tamanho da figura
    
    Returns:
        Figura matplotlib
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    cross_tab = pd.crosstab(df[y_col], df[x_col])
    
    sns.heatmap(cross_tab, cmap='YlOrRd', annot=True, fmt='d', ax=ax)
    ax.set_title(f'Heatmap: {y_col} vs {x_col}')
    
    plt.tight_layout()
    return fig


def plot_victim_profile(df: pd.DataFrame, 
                        figsize: Tuple[int, int] = (14, 10)) -> plt.Figure:
    """
    Plota perfil das vítimas.
    
    Args:
        df: DataFrame
        figsize: Tamanho da figura
    
    Returns:
        Figura matplotlib
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Distribuição de idade
    if 'Vict Age' in df.columns:
        age_data = df['Vict Age'][(df['Vict Age'] > 0) & (df['Vict Age'] < 100)]
        axes[0, 0].hist(age_data, bins=50, edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('Distribuição de Idade das Vítimas')
        axes[0, 0].set_xlabel('Idade')
        axes[0, 0].axvline(age_data.median(), color='red', linestyle='--', label=f'Mediana: {age_data.median():.0f}')
        axes[0, 0].legend()
    
    # Distribuição por sexo
    if 'Vict Sex' in df.columns:
        sex_counts = df['Vict Sex'].value_counts()
        axes[0, 1].pie(sex_counts.values, labels=sex_counts.index, autopct='%1.1f%%')
        axes[0, 1].set_title('Distribuição por Sexo')
    
    # Distribuição por descendência
    if 'Vict Descent' in df.columns:
        descent_counts = df['Vict Descent'].value_counts().head(10)
        axes[1, 0].barh(descent_counts.index, descent_counts.values)
        axes[1, 0].set_title('Top 10 Descendências')
        axes[1, 0].invert_yaxis()
    
    # Faixa etária se disponível
    if 'AGE_GROUP' in df.columns:
        age_group = df['AGE_GROUP'].value_counts()
        axes[1, 1].bar(age_group.index.astype(str), age_group.values, color='teal')
        axes[1, 1].set_title('Crimes por Faixa Etária')
        axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig


def plot_cluster_analysis(X_pca: np.ndarray, 
                           clusters: np.ndarray,
                           figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
    """
    Visualiza resultados de clustering.
    
    Args:
        X_pca: Dados transformados por PCA
        clusters: Labels dos clusters
        figsize: Tamanho da figura
    
    Returns:
        Figura matplotlib
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis', 
                         alpha=0.6, s=10)
    plt.colorbar(scatter, label='Cluster')
    
    ax.set_xlabel('Componente Principal 1')
    ax.set_ylabel('Componente Principal 2')
    ax.set_title('Visualização de Clusters (PCA)')
    
    plt.tight_layout()
    return fig


def plot_correlation_matrix(df: pd.DataFrame, 
                            figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
    """
    Plota matriz de correlação.
    
    Args:
        df: DataFrame
        figsize: Tamanho da figura
    
    Returns:
        Figura matplotlib
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr()
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, cmap='RdBu_r', center=0, 
                annot=True, fmt='.2f', ax=ax)
    
    ax.set_title('Matriz de Correlação')
    
    plt.tight_layout()
    return fig


def save_figure(fig: plt.Figure, 
                filename: str, 
                output_dir: str = 'outputs/figures',
                dpi: int = 300) -> None:
    """
    Salva figura em arquivo.
    
    Args:
        fig: Figura matplotlib
        filename: Nome do arquivo
        output_dir: Diretório de saída
        dpi: Resolução
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    print(f"Figura salva: {filepath}")
