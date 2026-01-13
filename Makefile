.PHONY: help build up down restart logs shell clean init-airflow

# Variáveis
COMPOSE = docker-compose
PROJECT_NAME = sbd2

help: ## Mostra esta mensagem de ajuda
	@echo "SBD2 - Crime Data Pipeline"
	@echo ""
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Constrói as imagens Docker
	$(COMPOSE) build

up: ## Inicia todos os serviços
	$(COMPOSE) up -d

down: ## Para todos os serviços
	$(COMPOSE) down

restart: down up ## Reinicia todos os serviços

logs: ## Mostra logs de todos os serviços
	$(COMPOSE) logs -f

logs-airflow: ## Mostra logs do Airflow
	$(COMPOSE) logs -f airflow-webserver airflow-scheduler

logs-spark: ## Mostra logs do Spark
	$(COMPOSE) logs -f spark-master spark-worker

shell-airflow: ## Acessa shell do container Airflow
	$(COMPOSE) exec airflow-webserver bash

shell-postgres: ## Acessa shell do PostgreSQL
	$(COMPOSE) exec postgres psql -U airflow -d airflow

shell-spark: ## Acessa shell do Spark
	$(COMPOSE) exec spark-master spark-shell

clean: ## Remove containers, volumes e imagens
	$(COMPOSE) down -v --rmi local
	docker system prune -f

init: build up ## Inicializa o projeto (build + up)
	@echo "Aguardando serviços iniciarem..."
	sleep 30
	@echo ""
	@echo "============================================"
	@echo "SBD2 - Crime Data Pipeline iniciado!"
	@echo "============================================"
	@echo ""
	@echo "Airflow UI:    http://localhost:8080 (admin/admin)"
	@echo "Spark UI:      http://localhost:8081"
	@echo "Jupyter Lab:   http://localhost:8888"
	@echo "PostgreSQL:    localhost:5432"
	@echo ""

trigger-pipeline: ## Dispara o pipeline completo
	$(COMPOSE) exec airflow-webserver airflow dags trigger crime_data_pipeline

status: ## Mostra status dos serviços
	$(COMPOSE) ps

test: ## Executa testes
	$(COMPOSE) exec airflow-webserver pytest /opt/airflow/tests/

docs-serve: ## Inicia servidor de documentação
	cd docs && mkdocs serve

docs-build: ## Gera documentação estática
	cd docs && mkdocs build
