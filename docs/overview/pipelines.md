# Pipelines ETL

## 🔄 Visão Geral

O projeto possui 4 DAGs (Directed Acyclic Graphs) no Apache Airflow:

```mermaid
flowchart TB
    A[crime_data_pipeline] --> B[bronze_to_silver]
    B --> C[silver_to_gold]
    C --> D[crime_analysis]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

## 📋 Descrição das DAGs

### 1. crime_data_pipeline (Principal)

**Frequência**: Semanal (`@weekly`)

DAG orquestradora que dispara as demais DAGs em sequência.

```python
start >> bronze_to_silver >> silver_to_gold >> crime_analysis >> end
```

### 2. bronze_to_silver

**Frequência**: Sob demanda

Transforma dados brutos para a camada Silver.

```mermaid
flowchart LR
    A[load_raw_data] --> B[clean_data]
    B --> C[create_features]
    C --> D[create_dimensions]
```

#### Tasks:

| Task | Descrição |
|------|-----------|
| `load_raw_data` | Carrega CSV bruto |
| `clean_data` | Limpa valores nulos e inválidos |
| `create_features` | Cria features derivadas |
| `create_dimensions` | Gera tabelas de dimensão |

### 3. silver_to_gold

**Frequência**: Sob demanda

Transforma dados Silver para Data Mart (Gold).

```mermaid
flowchart LR
    A[create_aggregations] --> B[load_to_postgres]
    A --> C[create_summary_report]
    B --> D[end]
    C --> D
```

#### Tasks:

| Task | Descrição |
|------|-----------|
| `create_aggregations` | Cria tabelas agregadas |
| `load_to_postgres` | Carrega dimensões no PostgreSQL |
| `create_summary_report` | Gera relatório JSON |

### 4. crime_analysis

**Frequência**: Sob demanda

Gera visualizações e análises.

```mermaid
flowchart LR
    A[start] --> B[temporal_charts]
    A --> C[geographic_charts]
    A --> D[victim_charts]
    B --> E[end]
    C --> E
    D --> E
```

#### Tasks:

| Task | Descrição |
|------|-----------|
| `generate_temporal_charts` | Gráficos temporais |
| `generate_geographic_charts` | Gráficos geográficos |
| `generate_victim_charts` | Gráficos de perfil de vítimas |

## 🔧 Configurações

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `POSTGRES_HOST` | Host do PostgreSQL | postgres |
| `POSTGRES_PORT` | Porta do PostgreSQL | 5432 |
| `SBD2_POSTGRES_USER` | Usuário do banco | sbd2 |
| `SBD2_POSTGRES_PASSWORD` | Senha do banco | sbd2_password |
| `SBD2_POSTGRES_DB` | Nome do banco | crime_data |

### Caminhos de Dados

| Caminho | Descrição |
|---------|-----------|
| `/opt/airflow/data_layer/raw` | Dados brutos |
| `/opt/airflow/data_layer/silver` | Dados limpos |
| `/opt/airflow/data_layer/gold` | Data Mart |

## 📊 Métricas

As DAGs geram métricas que são armazenadas via XCom:

- `raw_count`: Total de registros brutos
- `clean_count`: Total após limpeza
- `silver_count`: Total na camada Silver

## 🔍 Monitoramento

### Via Interface Airflow

1. Acesse http://localhost:8080
2. Navegue para a DAG desejada
3. Clique em "Graph" para ver o fluxo
4. Clique em uma task para ver logs

### Via Linha de Comando

```bash
# Listar execuções
airflow dags list-runs -d crime_data_pipeline

# Ver logs de uma task
airflow tasks logs bronze_to_silver clean_data 2024-01-01
```
