# Como Subir o Projeto

## 📋 Pré-requisitos

- **Docker** 24.x ou superior
- **Docker Compose** 2.x ou superior
- **Git**
- **Make** (opcional, para usar comandos do Makefile)
- **8GB+ RAM** (recomendado para Spark)

## 🚀 Instalação Rápida

### 1. Clone o Repositório

```bash
git clone https://github.com/dcasseb/SBD2.git
cd SBD2
```

### 2. Configure as Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo (já incluído)
cp .env.example .env

# Edite se necessário
nano .env
```

### 3. Inicie os Serviços

=== "Com Make"
    ```bash
    make init
    ```

=== "Sem Make"
    ```bash
    docker-compose build
    docker-compose up -d
    ```

### 4. Aguarde a Inicialização

Os serviços levam aproximadamente 1-2 minutos para iniciar completamente.

```bash
# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f
```

## 🌐 Acessando os Serviços

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Spark UI** | http://localhost:8081 | - |
| **Jupyter** | http://localhost:8888 | Token no log |
| **PostgreSQL** | localhost:5432 | sbd2 / sbd2_password |

## 📦 Comandos Úteis

```bash
# Parar serviços
make down
# ou
docker-compose down

# Reiniciar serviços
make restart
# ou
docker-compose restart

# Ver logs do Jupyter
make logs-jupyter
# ou
docker-compose logs -f jupyter

# Ver logs do Spark
make logs-spark
# ou
docker-compose logs -f spark-master spark-worker

# Acessar shell do Jupyter
make shell-jupyter
# ou
docker-compose exec jupyter bash

# Acessar PostgreSQL
make shell-postgres
# ou
docker-compose exec postgres psql -U sbd2 -d crime_data

# Limpar tudo
make clean
# ou
docker-compose down -v --rmi local
```

## ▶️ Executando o Pipeline

### Via Jupyter Lab

1. Acesse http://localhost:8888
2. Use o token exibido no log do container
3. Navegue até a pasta `notebooks/`
4. Execute os notebooks na ordem:
   - `01_etl_raw_bronze.ipynb`
   - `02_bronze_to_silver.ipynb`
   - `03_silver_to_gold.ipynb`
   - `04_data_analysis.ipynb`

### Via Linha de Comando

```bash
# Acessar container do Jupyter
docker-compose exec jupyter bash

# Executar notebook via linha de comando
jupyter nbconvert --execute --to notebook notebooks/01_etl_raw_bronze.ipynb
```

## 🔧 Troubleshooting

### Container não inicia

```bash
# Verificar logs
docker-compose logs <service_name>

# Verificar recursos disponíveis
docker system df
```

### Spark sem memória

Aumente a memória no `docker-compose.yml`:

```yaml
spark-worker:
  environment:
    - SPARK_WORKER_MEMORY=4G
```

### Jupyter não encontra dados

Verifique se os volumes estão montados corretamente:

```bash
docker-compose exec jupyter ls -la /home/jovyan/data_layer
```
