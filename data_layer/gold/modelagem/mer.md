# Modelo Entidade-Relacionamento (MER) - Camada Gold

## Descrição
Modelo dimensional (Star Schema) para análise de dados de crimes em Los Angeles.

## Diagrama Conceitual

```
                    ┌─────────────┐
                    │  dim_date   │
                    │─────────────│
                    │ sk_date     │
                    │ full_date   │
                    │ year        │
                    │ month       │
                    │ day_of_week │
                    │ is_weekend  │
                    └──────┬──────┘
                           │
    ┌─────────────┐        │        ┌─────────────┐
    │  dim_area   │        │        │  dim_time   │
    │─────────────│        │        │─────────────│
    │ sk_area     │        │        │ sk_time     │
    │ area_code   │        │        │ hour        │
    │ area_name   │        │        │ period_day  │
    │ region      │        │        │ is_rush     │
    └──────┬──────┘        │        └──────┬──────┘
           │               │               │
           │     ┌─────────┴─────────┐     │
           └─────┤   fato_crimes     ├─────┘
                 │───────────────────│
                 │ sk_crime          │
                 │ nk_crime_id       │
                 │ latitude          │
                 │ longitude         │
                 │ is_violent        │
           ┌─────┤                   ├─────┐
           │     └─────────┬─────────┘     │
           │               │               │
    ┌──────┴──────┐        │        ┌──────┴──────┐
    │dim_crime_type│       │        │ dim_weapon  │
    │─────────────│        │        │─────────────│
    │ sk_crime_type│       │        │ sk_weapon   │
    │ crime_code  │        │        │ weapon_code │
    │ description │        │        │ description │
    │ is_violent  │        │        │ lethality   │
    └─────────────┘        │        └─────────────┘
                           │
                    ┌──────┴──────┐
                    │ dim_victim  │
                    │─────────────│
                    │ sk_victim   │
                    │ age_group   │
                    │ sex         │
                    │ descent     │
                    └─────────────┘
```

## Tabela Fato

### fato_crimes
Tabela central contendo os fatos de cada crime registrado.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| sk_crime | SERIAL | Surrogate Key |
| nk_crime_id | BIGINT | Natural Key (DR_NO) |
| sk_area | INTEGER | FK para dim_area |
| sk_crime_type | INTEGER | FK para dim_crime_type |
| sk_weapon | INTEGER | FK para dim_weapon |
| sk_premise | INTEGER | FK para dim_premise |
| sk_date | INTEGER | FK para dim_date |
| sk_time | INTEGER | FK para dim_time |
| sk_victim | INTEGER | FK para dim_victim |
| latitude | DECIMAL | Coordenada de latitude |
| longitude | DECIMAL | Coordenada de longitude |
| is_violent | BOOLEAN | Flag de crime violento |

## Tabelas Dimensão

### dim_area
Áreas geográficas da LAPD.

### dim_crime_type
Tipos e categorias de crimes.

### dim_weapon
Armas utilizadas em crimes.

### dim_premise
Tipos de locais onde ocorreram crimes.

### dim_date
Dimensão de data (calendário).

### dim_time
Dimensão de tempo (horas do dia).

### dim_victim
Perfil demográfico das vítimas.

## Granularidade
- **Fato**: Um registro por crime reportado
- **Temporal**: Data e hora da ocorrência

## Métricas Derivadas
- Total de crimes por período
- Taxa de crimes violentos
- Crimes por área/região
- Distribuição temporal
- Perfil de vítimas
