# Como Obter os Dados

## 📊 Dataset: Crime Data from 2020 to Present

O dataset é muito grande (~244 MB) para ser armazenado diretamente no GitHub.

### Download Direto

1. Acesse: https://data.lacity.org/Public-Safety/Crime-Data-from-2020-to-Present/2nrs-mtv8/about_data

2. Clique em **Export** → **CSV**

3. Salve o arquivo como:
   ```
   data_layer/raw/crime_data/Crime_Data_from_2020_to_Present.csv
   ```

### Via Linha de Comando

```bash
# Usando curl
curl -L -o data_layer/raw/crime_data/Crime_Data_from_2020_to_Present.csv \
  "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"

# Ou usando wget
wget -O data_layer/raw/crime_data/Crime_Data_from_2020_to_Present.csv \
  "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"
```

### Via Python

```python
import pandas as pd

url = "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"
df = pd.read_csv(url)
df.to_csv("data_layer/raw/crime_data/Crime_Data_from_2020_to_Present.csv", index=False)
```

## ✅ Verificação

Após o download, verifique se o arquivo existe:

```bash
ls -lh data_layer/raw/crime_data/Crime_Data_from_2020_to_Present.csv
```

O arquivo deve ter aproximadamente **244 MB** e mais de **1 milhão de linhas**.
