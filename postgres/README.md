# PostgreSQL - Crime Data LA

Este diretório contém os scripts e configurações para o banco de dados PostgreSQL do projeto.

## 📁 Estrutura

```
postgres/
├── init_db.sh              # Script de inicialização do banco
├── load_data.py            # Script Python para carregar dados do CSV
├── scripts/
│   ├── 01_create_schemas.sql   # Criação dos schemas
│   ├── 02_raw_layer.sql        # DDL da camada Raw (Bronze)
│   ├── 03_silver_layer.sql     # DDL da camada Silver
│   └── 04_gold_layer.sql       # DDL da camada Gold
└── helpers/
    └── postgres_helper.py      # Funções auxiliares
```

## 🚀 Subindo o Banco

### Via Docker Compose (recomendado)

```bash
# Na raiz do projeto
docker-compose up -d postgres

# Verificar logs
docker logs -f sbd2_postgres
```

### Verificar se está funcionando

```bash
# Conectar ao banco
docker exec -it sbd2_postgres psql -U sbd2 -d crime_data

# Listar schemas
\dn

# Listar tabelas
\dt raw.*
\dt silver.*
\dt gold.*
```

## 📊 Arquitetura do Banco

### Schemas (Arquitetura Medallion)

| Schema | Descrição | Uso |
|--------|-----------|-----|
| `raw` | Dados brutos do CSV | Importação direta, sem transformação |
| `silver` | Dados limpos e enriquecidos | Análises e consultas |
| `gold` | Data Mart dimensional | Dashboards e BI |

### Modelo de Dados - Silver

```
silver.crimes (tabela principal)
├── crime_id (PK)
├── date_occurred, time_occurred
├── area_code, area_name
├── crime_code, crime_description
├── victim_age, victim_sex, victim_descent
├── latitude, longitude
├── is_violent, crime_category
└── period_of_day, age_group

silver.dim_areas
silver.dim_crime_types
silver.dim_weapons
silver.dim_premises
silver.dim_descent
```

### Modelo de Dados - Gold (Star Schema)

```
gold.fato_crimes (Tabela Fato)
├── sk_crime (PK)
├── sk_date → dim_date
├── sk_time → dim_time
├── sk_area → dim_area
├── sk_crime_type → dim_crime_type
├── sk_weapon → dim_weapon
├── sk_premise → dim_premise
└── sk_victim_profile → dim_victim_profile

Agregações:
├── agg_crimes_area_month
├── agg_crimes_type_year
├── agg_crime_hotspots
└── agg_serious_crimes
```

## 📥 Carregando Dados

### Opção 1: Script Python

```bash
# Ativar ambiente virtual
.\.venv\Scripts\activate

# Executar script de carga
python postgres/load_data.py
```

### Opção 2: COPY direto (mais rápido)

```sql
-- Conectar ao banco
\c crime_data

-- Importar CSV para tabela raw
COPY raw.crime_data (
    dr_no, date_rptd, date_occ, time_occ, area, area_name,
    rpt_dist_no, part_1_2, crm_cd, crm_cd_desc, mocodes,
    vict_age, vict_sex, vict_descent, premis_cd, premis_desc,
    weapon_used_cd, weapon_desc, status, status_desc,
    crm_cd_1, crm_cd_2, crm_cd_3, crm_cd_4,
    location, cross_street, lat, lon
)
FROM '/data/crime_data.csv'
WITH (FORMAT CSV, HEADER TRUE);
```

## 🔍 Consultas Úteis

### Resumo por ano

```sql
SELECT 
    year_occurred,
    COUNT(*) as total,
    SUM(CASE WHEN is_violent THEN 1 ELSE 0 END) as violentos
FROM silver.crimes
GROUP BY year_occurred
ORDER BY year_occurred;
```

### Top 10 crimes

```sql
SELECT crime_description, COUNT(*) as total
FROM silver.crimes
GROUP BY crime_description
ORDER BY total DESC
LIMIT 10;
```

### Crimes graves

```sql
SELECT * FROM silver.vw_serious_crimes
LIMIT 100;
```

### Áreas mais perigosas

```sql
SELECT * FROM silver.vw_crimes_by_area
LIMIT 10;
```

## 🔐 Credenciais

| Parâmetro | Valor |
|-----------|-------|
| Host | localhost |
| Port | 5432 |
| Database | crime_data |
| User | sbd2 |
| Password | sbd2_password |

### String de Conexão

```
postgresql://sbd2:sbd2_password@localhost:5432/crime_data
```

### Python (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='crime_data',
    user='sbd2',
    password='sbd2_password'
)
```

### SQLAlchemy

```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://sbd2:sbd2_password@localhost:5432/crime_data')
```
