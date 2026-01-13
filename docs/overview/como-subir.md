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
| **Airflow** | http://localhost:8080 | admin / admin |
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

# Ver logs do Airflow
make logs-airflow
# ou
docker-compose logs -f airflow-webserver airflow-scheduler

# Acessar shell do Airflow
make shell-airflow
# ou
docker-compose exec airflow-webserver bash

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

### Via Interface Web (Airflow)

1. Acesse http://localhost:8080
2. Faça login com admin/admin
3. Na lista de DAGs, encontre `crime_data_pipeline`
4. Clique no toggle para habilitar a DAG
5. Clique no botão "Play" para executar

### Via Linha de Comando

```bash
# Acessar container do Airflow
docker-compose exec airflow-webserver bash

# Disparar pipeline
airflow dags trigger crime_data_pipeline

# Verificar status
airflow dags list-runs -d crime_data_pipeline
```

## 🔧 Troubleshooting

### Container não inicia

```bash
# Verificar logs
docker-compose logs <service_name>

# Verificar recursos disponíveis
docker system df
```

### Airflow não conecta ao PostgreSQL

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Reiniciar Airflow
docker-compose restart airflow-webserver airflow-scheduler
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
