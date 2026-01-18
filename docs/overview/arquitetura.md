# Arquitetura do Sistema

## 🏗️ Visão Geral

O projeto implementa uma arquitetura de **Data Lake** moderna, seguindo o padrão **Medallion Architecture** (Bronze → Silver → Gold), amplamente utilizado em projetos de Data Engineering.

## 📊 Diagrama de Arquitetura

```mermaid
flowchart TB
    subgraph Sources["📥 Fontes de Dados"]
        CSV[Crime Data CSV]
    end
    
    subgraph Processing["⚙️ Processamento"]
        Jupyter[Jupyter Notebooks]
        Spark[Apache Spark]
    end
    
    subgraph Storage["💾 Armazenamento"]
        subgraph Medallion["Medallion Architecture"]
            Bronze[🥉 Bronze/Raw]
            Silver[🥈 Silver]
            Gold[🥇 Gold]
        end
        Postgres[(PostgreSQL)]
    end
    
    subgraph Consumption["📊 Consumo"]
        Dashboards[Dashboards]
    end
    
    CSV --> Jupyter
    Jupyter --> Spark
    Spark --> Bronze
    Bronze --> Silver
    Silver --> Gold
    Gold --> Postgres
    Postgres --> Dashboards
```

## 🎨 Camadas do Data Lake

### 🥉 Bronze (Raw)
- **Descrição**: Dados brutos, exatamente como recebidos da fonte
- **Formato**: CSV original
- **Transformações**: Nenhuma
- **Uso**: Preservação do dado original para auditoria

### 🥈 Silver
- **Descrição**: Dados limpos, validados e enriquecidos
- **Formato**: Parquet particionado
- **Transformações**:
    - Limpeza de valores nulos
    - Conversão de tipos
    - Validação de coordenadas
    - Criação de features temporais
- **Uso**: Análises exploratórias

### 🥇 Gold
- **Descrição**: Dados modelados dimensionalmente (Star Schema)
- **Formato**: Parquet + PostgreSQL
- **Transformações**:
    - Modelo dimensional
    - Agregações pré-calculadas
    - Métricas de negócio
- **Uso**: Dashboards e relatórios

## 🔌 Componentes

### Jupyter Notebooks
- **Papel**: Execução dos pipelines ETL e análises
- **Notebooks**:
    - `01_etl_raw_bronze.ipynb` - ETL Raw → Bronze
    - `02_bronze_to_silver.ipynb` - ETL Bronze → Silver
    - `03_silver_to_gold.ipynb` - ETL Silver → Gold
    - `04_data_analysis.ipynb` - Análises e visualizações

### Apache Spark
- **Papel**: Processamento distribuído
- **Jobs**:
    - Limpeza de dados
    - Feature engineering
    - Agregações

### PostgreSQL
- **Papel**: Armazenamento estruturado
- **Schemas**:
    - `silver` - Dados limpos
    - `gold` - Data Mart dimensional

### Docker
- **Papel**: Containerização
- **Serviços**:
    - `postgres`
    - `spark-master`
    - `spark-worker`
    - `jupyter`

## 📁 Estrutura de Diretórios

```
SBD2/
├── data_layer/
│   ├── raw/            # Camada Bronze
│   ├── silver/         # Camada Silver
│   └── gold/           # Camada Gold
├── docs/               # Documentação MkDocs
├── notebooks/          # Notebooks de ETL e análise
├── postgres/           # Configurações PostgreSQL
├── spark_config/       # Configurações Spark
├── transformer/        # Jobs ETL (notebooks)
├── docker-compose.yml  # Orquestração de containers
└── Makefile            # Comandos de automação
```
