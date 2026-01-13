# SBD2 - Sistemas de Banco de Dados 2

## 📋 Descrição do Projeto

Este repositório contém o trabalho prático da disciplina de Sistemas de Banco de Dados 2 (SBD2) da Universidade de Brasília (UnB). O projeto utiliza o dataset **Crime Data from 2020 to Present** para realizar operações de:

- 🔧 **Engenharia de Dados**: Limpeza, transformação e preparação dos dados
- ⛏️ **Mineração de Dados**: Descoberta de padrões e conhecimento nos dados
- 📊 **Análise de Dados**: Visualizações e insights estatísticos

## 📁 Estrutura do Projeto

```
SBD2/
├── data/
│   ├── raw/                    # Dados brutos originais
│   └── processed/              # Dados processados e limpos
├── notebooks/
│   ├── 01_data_engineering.ipynb    # Engenharia de dados
│   ├── 02_data_mining.ipynb         # Mineração de dados
│   └── 03_data_analysis.ipynb       # Análise de dados
├── src/
│   ├── __init__.py
│   ├── data_processing.py      # Funções de processamento
│   ├── mining.py               # Funções de mineração
│   └── visualization.py        # Funções de visualização
├── outputs/
│   ├── figures/                # Gráficos e visualizações
│   └── reports/                # Relatórios gerados
├── requirements.txt            # Dependências do projeto
├── .gitignore                  # Arquivos ignorados pelo Git
└── README.md                   # Este arquivo
```

## 📊 Dataset

**Crime Data from 2020 to Present** - Dados de crimes reportados na cidade de Los Angeles, EUA.

### Principais Colunas:
| Coluna | Descrição |
|--------|-----------|
| DR_NO | Número do relatório de crime |
| Date Rptd | Data de reporte |
| DATE OCC | Data de ocorrência |
| TIME OCC | Horário de ocorrência |
| AREA | Código da área |
| AREA NAME | Nome da área |
| Crm Cd | Código do crime |
| Crm Cd Desc | Descrição do crime |
| Vict Age | Idade da vítima |
| Vict Sex | Sexo da vítima |
| Vict Descent | Descendência da vítima |
| Premis Desc | Descrição do local |
| Weapon Desc | Descrição da arma utilizada |
| LAT, LON | Coordenadas geográficas |

## 🚀 Como Executar

### 1. Clone o repositório
```bash
git clone https://github.com/dcasseb/SBD2.git
cd SBD2
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute os notebooks
```bash
jupyter notebook notebooks/
```

## 📦 Dependências

- Python 3.8+
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Jupyter

## 🔍 Etapas do Projeto

### 1. Engenharia de Dados
- Carregamento e inspeção inicial dos dados
- Tratamento de valores nulos
- Conversão de tipos de dados
- Normalização e padronização
- Criação de features derivadas

### 2. Mineração de Dados
- Análise de clusters (K-Means)
- Regras de associação (Apriori)
- Classificação de tipos de crime
- Detecção de anomalias

### 3. Análise de Dados
- Análise temporal de crimes
- Distribuição geográfica
- Análise por tipo de crime
- Perfil das vítimas
- Correlações e insights

## 👥 Autor

Desenvolvido para a disciplina SBD2 - UnB

## 📄 Licença

Este projeto está sob a licença MIT.
