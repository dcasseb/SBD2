# Dicionário de Dados - Crime Data

## 📋 Descrição

Dataset de crimes reportados na cidade de Los Angeles, EUA, desde 2020 até o presente.

## 📊 Metadados

| Propriedade | Valor |
|-------------|-------|
| **Fonte** | Los Angeles Open Data Portal |
| **Formato** | CSV |
| **Encoding** | UTF-8 |
| **Tamanho** | ~250 MB |
| **Registros** | ~1.000.000+ |
| **Período** | 2020 - Presente |

## 📑 Estrutura das Colunas

### Identificação

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `DR_NO` | INTEGER | Número único do relatório | 211507896 |

### Temporal

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `Date Rptd` | DATETIME | Data do reporte | 04/11/2021 12:00:00 AM |
| `DATE OCC` | DATETIME | Data da ocorrência | 11/07/2020 12:00:00 AM |
| `TIME OCC` | INTEGER | Hora (formato HHMM) | 0845 |

### Localização

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `AREA` | INTEGER | Código da área LAPD | 15 |
| `AREA NAME` | STRING | Nome da área | N Hollywood |
| `Rpt Dist No` | INTEGER | Distrito de reporte | 1502 |
| `LOCATION` | STRING | Endereço | 7800 BEEMAN AV |
| `Cross Street` | STRING | Rua transversal | N GAULT |
| `LAT` | FLOAT | Latitude | 34.2124 |
| `LON` | FLOAT | Longitude | -118.4092 |

### Crime

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `Crm Cd` | INTEGER | Código do crime | 354 |
| `Crm Cd Desc` | STRING | Descrição | THEFT OF IDENTITY |
| `Part 1-2` | INTEGER | Classificação | 1=Grave, 2=Menor |
| `Mocodes` | STRING | Modus operandi | 0377 |

### Vítima

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `Vict Age` | INTEGER | Idade | 31 |
| `Vict Sex` | CHAR | Sexo | M, F, X |
| `Vict Descent` | CHAR | Descendência | H (Hispanic) |

### Local do Crime

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `Premis Cd` | INTEGER | Código do local | 501 |
| `Premis Desc` | STRING | Descrição | SINGLE FAMILY DWELLING |

### Arma

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `Weapon Used Cd` | INTEGER | Código da arma | 200 |
| `Weapon Desc` | STRING | Descrição | KNIFE |

### Status

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `Status` | STRING | Código de status | IC |
| `Status Desc` | STRING | Descrição | Invest Cont |

## 🏷️ Códigos de Referência

### Descendência (Vict Descent)

| Código | Descrição |
|--------|-----------|
| A | Other Asian |
| B | Black |
| C | Chinese |
| F | Filipino |
| H | Hispanic/Latin/Mexican |
| I | American Indian |
| J | Japanese |
| K | Korean |
| O | Other |
| P | Pacific Islander |
| W | White |
| X | Unknown |

### Status do Caso

| Código | Descrição |
|--------|-----------|
| IC | Invest Cont (Investigação Continua) |
| AO | Adult Other |
| AA | Adult Arrest |
| JA | Juvenile Arrest |
| JO | Juvenile Other |
| CC | Unknown |

### Áreas LAPD

| Código | Nome |
|--------|------|
| 01 | Central |
| 02 | Rampart |
| 03 | Southwest |
| 04 | Hollenbeck |
| 05 | Harbor |
| 06 | Hollywood |
| 07 | Wilshire |
| 08 | West LA |
| ... | ... |

## ✨ Features Derivadas

Criadas durante o processamento ETL:

| Feature | Tipo | Descrição |
|---------|------|-----------|
| `YEAR` | INTEGER | Ano da ocorrência |
| `MONTH` | INTEGER | Mês da ocorrência |
| `DAY_OF_WEEK` | INTEGER | Dia da semana (0-6) |
| `HOUR` | INTEGER | Hora (0-23) |
| `IS_WEEKEND` | BOOLEAN | Final de semana |
| `PERIOD` | STRING | Período (Manhã, Tarde, etc) |
| `AGE_GROUP` | STRING | Faixa etária |
| `IS_VIOLENT` | BOOLEAN | Crime violento |
