"""
Módulo de Mineração de Dados
SBD2 - Sistemas de Banco de Dados 2
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, silhouette_score
from typing import Tuple, Optional, List


def perform_clustering(df: pd.DataFrame, 
                       features: List[str], 
                       n_clusters: int = 5,
                       method: str = 'kmeans') -> Tuple[pd.DataFrame, object]:
    """
    Realiza clustering nos dados.
    
    Args:
        df: DataFrame com os dados
        features: Lista de features para clustering
        n_clusters: Número de clusters (para KMeans)
        method: 'kmeans' ou 'dbscan'
    
    Returns:
        Tuple com DataFrame atualizado e modelo
    """
    df = df.copy()
    
    # Preparar dados
    X = df[features].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    if method == 'kmeans':
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = model.fit_predict(X_scaled)
    elif method == 'dbscan':
        model = DBSCAN(eps=0.5, min_samples=5)
        clusters = model.fit_predict(X_scaled)
    
    df.loc[X.index, 'Cluster'] = clusters
    
    # Calcular silhouette score
    if len(set(clusters)) > 1:
        score = silhouette_score(X_scaled, clusters)
        print(f"Silhouette Score: {score:.3f}")
    
    return df, model


def find_optimal_clusters(df: pd.DataFrame, 
                          features: List[str], 
                          max_clusters: int = 10) -> List[float]:
    """
    Encontra o número ótimo de clusters usando o método do cotovelo.
    
    Args:
        df: DataFrame
        features: Lista de features
        max_clusters: Número máximo de clusters para testar
    
    Returns:
        Lista com inertias para cada k
    """
    X = df[features].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    inertias = []
    for k in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
        print(f"K={k}: Inertia={kmeans.inertia_:.2f}")
    
    return inertias


def detect_anomalies(df: pd.DataFrame, 
                     features: List[str], 
                     contamination: float = 0.1) -> pd.DataFrame:
    """
    Detecta anomalias nos dados usando Isolation Forest.
    
    Args:
        df: DataFrame
        features: Lista de features
        contamination: Proporção esperada de anomalias
    
    Returns:
        DataFrame com coluna de anomalias
    """
    df = df.copy()
    
    X = df[features].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    df.loc[X.index, 'Is_Anomaly'] = iso_forest.fit_predict(X_scaled)
    df['Is_Anomaly'] = df['Is_Anomaly'].map({1: 0, -1: 1})
    
    n_anomalies = df['Is_Anomaly'].sum()
    print(f"Anomalias detectadas: {n_anomalies:,} ({n_anomalies/len(df)*100:.2f}%)")
    
    return df


def classify_crime_type(df: pd.DataFrame, 
                        features: List[str], 
                        target: str,
                        test_size: float = 0.2) -> Tuple[object, dict]:
    """
    Treina um classificador para prever tipo de crime.
    
    Args:
        df: DataFrame
        features: Lista de features
        target: Coluna alvo
        test_size: Proporção do conjunto de teste
    
    Returns:
        Tuple com modelo treinado e métricas
    """
    df_clean = df[features + [target]].dropna()
    
    X = df_clean[features]
    y = df_clean[target]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    report = classification_report(y_test, y_pred, output_dict=True)
    
    print("Acurácia:", report['accuracy'])
    
    return model, report


def get_feature_importance(model, feature_names: List[str]) -> pd.DataFrame:
    """
    Retorna a importância das features do modelo.
    
    Args:
        model: Modelo treinado
        feature_names: Nomes das features
    
    Returns:
        DataFrame com importância das features
    """
    importance = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    return importance


def apply_pca(df: pd.DataFrame, 
              features: List[str], 
              n_components: int = 2) -> Tuple[np.ndarray, object]:
    """
    Aplica PCA para redução de dimensionalidade.
    
    Args:
        df: DataFrame
        features: Lista de features
        n_components: Número de componentes
    
    Returns:
        Tuple com dados transformados e modelo PCA
    """
    X = df[features].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)
    
    print(f"Variância explicada: {pca.explained_variance_ratio_.sum()*100:.2f}%")
    
    return X_pca, pca


def association_rules_prep(df: pd.DataFrame, 
                           columns: List[str]) -> pd.DataFrame:
    """
    Prepara dados para análise de regras de associação.
    
    Args:
        df: DataFrame
        columns: Colunas categóricas para análise
    
    Returns:
        DataFrame binário para análise de associação
    """
    df_prep = df[columns].copy()
    
    # One-hot encoding
    df_encoded = pd.get_dummies(df_prep, prefix_sep='=')
    
    return df_encoded


def temporal_pattern_analysis(df: pd.DataFrame, 
                              date_col: str, 
                              value_col: str) -> pd.DataFrame:
    """
    Analisa padrões temporais nos dados.
    
    Args:
        df: DataFrame
        date_col: Coluna de data
        value_col: Coluna para agregar
    
    Returns:
        DataFrame com análise temporal
    """
    df = df.copy()
    
    # Agregação por período
    daily = df.groupby(df[date_col].dt.date)[value_col].count()
    weekly = df.groupby(df[date_col].dt.isocalendar().week)[value_col].count()
    monthly = df.groupby(df[date_col].dt.to_period('M'))[value_col].count()
    
    patterns = {
        'daily_mean': daily.mean(),
        'daily_std': daily.std(),
        'weekly_mean': weekly.mean(),
        'monthly_mean': monthly.mean()
    }
    
    return pd.DataFrame([patterns])
