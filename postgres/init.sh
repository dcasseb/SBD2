#!/bin/bash
# Script de inicialização do PostgreSQL
# Cria bancos de dados e esquemas necessários

set -e

echo "==================================="
echo "Inicializando banco de dados SBD2"
echo "==================================="

# Criar banco de dados do projeto
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Criar usuário do projeto
    CREATE USER sbd2 WITH PASSWORD 'sbd2_password';
    
    -- Criar banco de dados
    CREATE DATABASE crime_data OWNER sbd2;
    
    -- Conectar ao banco crime_data
    \c crime_data
    
    -- Criar schemas
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE SCHEMA IF NOT EXISTS silver;
    CREATE SCHEMA IF NOT EXISTS gold;
    
    -- Conceder permissões
    GRANT ALL PRIVILEGES ON SCHEMA raw TO sbd2;
    GRANT ALL PRIVILEGES ON SCHEMA silver TO sbd2;
    GRANT ALL PRIVILEGES ON SCHEMA gold TO sbd2;
    
    -- Criar extensões úteis
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    CREATE EXTENSION IF NOT EXISTS postgis;
    
    EOSQL

echo "Banco de dados inicializado com sucesso!"

# Executar DDL da camada Silver
if [ -f "/docker-entrypoint-initdb.d/silver_ddl.sql" ]; then
    psql -v ON_ERROR_STOP=1 --username "sbd2" --dbname "crime_data" -f /docker-entrypoint-initdb.d/silver_ddl.sql
fi

# Executar DDL da camada Gold
if [ -f "/docker-entrypoint-initdb.d/gold_ddl.sql" ]; then
    psql -v ON_ERROR_STOP=1 --username "sbd2" --dbname "crime_data" -f /docker-entrypoint-initdb.d/gold_ddl.sql
fi

echo "Schemas criados com sucesso!"
