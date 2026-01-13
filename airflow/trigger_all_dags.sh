#!/bin/bash
# Script para disparar todas as DAGs em sequência

echo "==================================="
echo "SBD2 - Disparando Pipeline de Crimes"
echo "==================================="

# Verificar se Airflow está rodando
if ! curl -s http://localhost:8080/health > /dev/null; then
    echo "Erro: Airflow não está acessível"
    exit 1
fi

# Disparar DAG principal
echo "Disparando pipeline principal..."
airflow dags trigger crime_data_pipeline

echo ""
echo "Pipeline disparado com sucesso!"
echo "Acesse http://localhost:8080 para acompanhar a execução"
