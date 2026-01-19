# Modelagem de Dados - MER/DER/DLD

## Modelo Conceitual

O modelo dimensional segue o padrão **Star Schema**, otimizado para consultas analíticas.

## Star Schema

```mermaid
erDiagram
    FATO_CRIMES ||--o{ DIM_DATE : "sk_date"
    FATO_CRIMES ||--o{ DIM_TIME : "sk_time"
    FATO_CRIMES ||--o{ DIM_AREA : "sk_area"
    FATO_CRIMES ||--o{ DIM_CRIME_TYPE : "sk_crime_type"
    FATO_CRIMES ||--o{ DIM_VICTIM : "sk_victim"
    FATO_CRIMES ||--o{ DIM_WEAPON : "sk_weapon"
    FATO_CRIMES ||--o{ DIM_PREMISE : "sk_premise"
    
    FATO_CRIMES {
        int sk_crime PK
        bigint nk_crime_id
        int sk_date FK
        int sk_time FK
        int sk_area FK
        int sk_crime_type FK
        int sk_victim FK
        int sk_weapon FK
        int sk_premise FK
        decimal latitude
        decimal longitude
        boolean is_violent
    }
    
    DIM_DATE {
        int sk_date PK
        date full_date
        int year
        int quarter
        int month
        string month_name
        int day_of_week
        string day_name
        boolean is_weekend
    }
    
    DIM_TIME {
        int sk_time PK
        int hour
        int minute
        string period_of_day
        boolean is_rush_hour
    }
    
    DIM_AREA {
        int sk_area PK
        int area_code
        string area_name
        string region
    }
    
    DIM_CRIME_TYPE {
        int sk_crime_type PK
        int crime_code
        string crime_description
        string crime_category
        boolean is_violent
        int severity_level
    }
    
    DIM_VICTIM {
        int sk_victim PK
        string age_group
        char sex
        char descent
        string descent_description
    }
    
    DIM_WEAPON {
        int sk_weapon PK
        int weapon_code
        string weapon_description
        string weapon_category
    }
    
    DIM_PREMISE {
        int sk_premise PK
        int premise_code
        string premise_description
        string premise_category
    }
```

## Descrição das Tabelas

### Tabela Fato

#### fato_crimes
Tabela central contendo os eventos de crimes.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| sk_crime | SERIAL | Surrogate Key (PK) |
| nk_crime_id | BIGINT | Natural Key (DR_NO) |
| sk_date | INTEGER | FK para dim_date |
| sk_time | INTEGER | FK para dim_time |
| sk_area | INTEGER | FK para dim_area |
| sk_crime_type | INTEGER | FK para dim_crime_type |
| sk_victim | INTEGER | FK para dim_victim |
| sk_weapon | INTEGER | FK para dim_weapon |
| sk_premise | INTEGER | FK para dim_premise |
| latitude | DECIMAL | Coordenada |
| longitude | DECIMAL | Coordenada |
| is_violent | BOOLEAN | Flag de crime violento |

### Tabelas Dimensão

#### dim_date
Calendário para análise temporal.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| sk_date | SERIAL | Surrogate Key (PK) |
| full_date | DATE | Data completa |
| year | INTEGER | Ano |
| quarter | INTEGER | Trimestre |
| month | INTEGER | Mês |
| month_name | VARCHAR | Nome do mês |
| week_of_year | INTEGER | Semana do ano |
| day_of_month | INTEGER | Dia do mês |
| day_of_week | INTEGER | Dia da semana |
| day_name | VARCHAR | Nome do dia |
| is_weekend | BOOLEAN | Fim de semana |

#### dim_time
Horas do dia para análise.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| sk_time | SERIAL | Surrogate Key (PK) |
| hour | INTEGER | Hora (0-23) |
| minute | INTEGER | Minuto |
| period_of_day | VARCHAR | Período (Manhã, Tarde, etc) |
| is_rush_hour | BOOLEAN | Horário de pico |

#### dim_area
Áreas geográficas da LAPD.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| sk_area | SERIAL | Surrogate Key (PK) |
| area_code | INTEGER | Código da área |
| area_name | VARCHAR | Nome da área |
| region | VARCHAR | Região (Central, Valley, etc) |

#### dim_crime_type
Tipos e categorias de crimes.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| sk_crime_type | SERIAL | Surrogate Key (PK) |
| crime_code | INTEGER | Código do crime |
| crime_description | VARCHAR | Descrição |
| crime_category | VARCHAR | Categoria |
| is_violent | BOOLEAN | Crime violento |
| severity_level | INTEGER | Nível de gravidade |

#### dim_victim
Perfil demográfico das vítimas.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| sk_victim | SERIAL | Surrogate Key (PK) |
| age_group | VARCHAR | Faixa etária |
| sex | CHAR | Sexo |
| descent | CHAR | Descendência (código) |
| descent_description | VARCHAR | Descendência (descrição) |

## Tabelas de Agregação

Para otimizar consultas frequentes:

| Tabela | Descrição |
|--------|-----------|
| `agg_crimes_area_period` | Crimes por área e período |
| `agg_crimes_type_year` | Crimes por tipo e ano |
| `agg_crime_hotspots` | Hotspots geográficos |

## Consultas Exemplo

### Total de crimes por área

```sql
SELECT 
    a.area_name,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN f.is_violent THEN 1 ELSE 0 END) as violent_crimes
FROM gold.fato_crimes f
JOIN gold.dim_area a ON f.sk_area = a.sk_area
GROUP BY a.area_name
ORDER BY total_crimes DESC;
```

### Crimes por período do dia

```sql
SELECT 
    t.period_of_day,
    COUNT(*) as total_crimes
FROM gold.fato_crimes f
JOIN gold.dim_time t ON f.sk_time = t.sk_time
GROUP BY t.period_of_day
ORDER BY total_crimes DESC;
```

### Perfil de vítimas por tipo de crime

```sql
SELECT 
    ct.crime_category,
    v.age_group,
    v.sex,
    COUNT(*) as total
FROM gold.fato_crimes f
JOIN gold.dim_crime_type ct ON f.sk_crime_type = ct.sk_crime_type
JOIN gold.dim_victim v ON f.sk_victim = v.sk_victim
GROUP BY ct.crime_category, v.age_group, v.sex
ORDER BY total DESC;
```
