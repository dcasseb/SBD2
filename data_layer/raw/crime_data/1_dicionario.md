# Dicionário de Dados - Crime Data from 2020 to Present

## Descrição
Dataset de crimes reportados na cidade de Los Angeles, EUA, desde 2020 até o presente.

## Fonte
- **Origem**: Los Angeles Open Data Portal
- **URL**: https://data.lacity.org/
- **Formato**: CSV
- **Atualização**: Semanal

## Estrutura dos Dados

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| DR_NO | INTEGER | Número único do relatório de crime | 211507896 |
| Date Rptd | DATETIME | Data em que o crime foi reportado | 04/11/2021 |
| DATE OCC | DATETIME | Data em que o crime ocorreu | 11/07/2020 |
| TIME OCC | INTEGER | Horário de ocorrência (formato militar HHMM) | 0845 |
| AREA | INTEGER | Código da área da LAPD | 15 |
| AREA NAME | STRING | Nome da área geográfica | N Hollywood |
| Rpt Dist No | INTEGER | Número do distrito de reporte | 1502 |
| Part 1-2 | INTEGER | Classificação do crime (1=Grave, 2=Menor) | 2 |
| Crm Cd | INTEGER | Código do crime | 354 |
| Crm Cd Desc | STRING | Descrição do crime | THEFT OF IDENTITY |
| Mocodes | STRING | Códigos de modus operandi | 0377 |
| Vict Age | INTEGER | Idade da vítima | 31 |
| Vict Sex | STRING | Sexo da vítima (M/F/X) | M |
| Vict Descent | STRING | Descendência étnica da vítima | H (Hispanic) |
| Premis Cd | INTEGER | Código do tipo de local | 501 |
| Premis Desc | STRING | Descrição do local | SINGLE FAMILY DWELLING |
| Weapon Used Cd | INTEGER | Código da arma utilizada | 200 |
| Weapon Desc | STRING | Descrição da arma | KNIFE |
| Status | STRING | Código de status do caso | IC |
| Status Desc | STRING | Descrição do status | Invest Cont |
| Crm Cd 1-4 | INTEGER | Códigos de crimes adicionais | 354 |
| LOCATION | STRING | Endereço da ocorrência | 7800 BEEMAN AV |
| Cross Street | STRING | Rua transversal | N GAULT |
| LAT | FLOAT | Latitude | 34.2124 |
| LON | FLOAT | Longitude | -118.4092 |

## Códigos de Descendência (Vict Descent)

| Código | Descrição |
|--------|-----------|
| A | Other Asian |
| B | Black |
| C | Chinese |
| D | Cambodian |
| F | Filipino |
| G | Guamanian |
| H | Hispanic/Latin/Mexican |
| I | American Indian/Alaskan Native |
| J | Japanese |
| K | Korean |
| L | Laotian |
| O | Other |
| P | Pacific Islander |
| S | Samoan |
| U | Hawaiian |
| V | Vietnamese |
| W | White |
| X | Unknown |
| Z | Asian Indian |

## Status dos Casos

| Código | Descrição |
|--------|-----------|
| IC | Invest Cont (Investigação Continua) |
| AO | Adult Other |
| AA | Adult Arrest |
| JA | Juvenile Arrest |
| JO | Juvenile Other |
| CC | UNK |

## Volume de Dados

- **Período**: 2020 - Presente
- **Registros**: ~1.000.000+ linhas
- **Tamanho**: ~250 MB
