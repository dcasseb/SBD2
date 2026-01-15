#!/bin/bash
# ============================================
# Script de inicialização do PostgreSQL
# Crime Data LA - SBD2
# ============================================

set -e

echo "==========================================="
echo "🚀 Inicializando banco de dados SBD2"
echo "   Crime Data from 2020 to Present"
echo "==========================================="

# Variáveis
PROJECT_USER="sbd2"
PROJECT_PASSWORD="sbd2_password"
PROJECT_DB="crime_data"

# ============================================
# 1. Criar usuário e banco de dados
# ============================================
echo "📦 Criando usuário e banco de dados..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Verificar e criar usuário
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${PROJECT_USER}') THEN
            CREATE USER ${PROJECT_USER} WITH PASSWORD '${PROJECT_PASSWORD}';
            RAISE NOTICE 'Usuário ${PROJECT_USER} criado com sucesso';
        ELSE
            RAISE NOTICE 'Usuário ${PROJECT_USER} já existe';
        END IF;
    END
    \$\$;
    
    -- Verificar e criar banco de dados
    SELECT 'CREATE DATABASE ${PROJECT_DB} OWNER ${PROJECT_USER}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${PROJECT_DB}')\gexec
    
EOSQL

echo "✅ Usuário e banco criados"

# ============================================
# 2. Configurar banco de dados do projeto
# ============================================
echo "🔧 Configurando banco de dados ${PROJECT_DB}..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${PROJECT_DB}" <<-EOSQL
    -- Extensões úteis
    CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Busca por similaridade
    
    -- Criar schemas
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE SCHEMA IF NOT EXISTS silver;
    CREATE SCHEMA IF NOT EXISTS gold;
    
    -- Conceder permissões
    GRANT ALL PRIVILEGES ON DATABASE ${PROJECT_DB} TO ${PROJECT_USER};
    GRANT ALL PRIVILEGES ON SCHEMA raw TO ${PROJECT_USER};
    GRANT ALL PRIVILEGES ON SCHEMA silver TO ${PROJECT_USER};
    GRANT ALL PRIVILEGES ON SCHEMA gold TO ${PROJECT_USER};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw TO ${PROJECT_USER};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA silver TO ${PROJECT_USER};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA gold TO ${PROJECT_USER};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA raw TO ${PROJECT_USER};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA silver TO ${PROJECT_USER};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA gold TO ${PROJECT_USER};
    
    -- Definir search_path
    ALTER USER ${PROJECT_USER} SET search_path TO gold, silver, raw, public;
    
EOSQL

echo "✅ Schemas criados: raw, silver, gold"

# ============================================
# 3. Executar scripts DDL
# ============================================
SCRIPTS_DIR="/docker-entrypoint-initdb.d/scripts"

if [ -d "$SCRIPTS_DIR" ]; then
    echo "📄 Executando scripts DDL..."
    
    for script in "$SCRIPTS_DIR"/*.sql; do
        if [ -f "$script" ]; then
            echo "   Executando: $(basename $script)"
            psql -v ON_ERROR_STOP=1 --username "${PROJECT_USER}" --dbname "${PROJECT_DB}" -f "$script"
        fi
    done
    
    echo "✅ Scripts DDL executados"
else
    echo "⚠️  Diretório de scripts não encontrado: $SCRIPTS_DIR"
fi

# ============================================
# 4. Verificar estrutura criada
# ============================================
echo ""
echo "📊 Verificando estrutura do banco..."

psql -v ON_ERROR_STOP=1 --username "${PROJECT_USER}" --dbname "${PROJECT_DB}" <<-EOSQL
    SELECT 
        schemaname as schema,
        COUNT(*) as tables
    FROM pg_tables 
    WHERE schemaname IN ('raw', 'silver', 'gold')
    GROUP BY schemaname
    ORDER BY schemaname;
EOSQL

echo ""
echo "==========================================="
echo "✅ Banco de dados inicializado com sucesso!"
echo ""
echo "📌 Informações de conexão:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: ${PROJECT_DB}"
echo "   User: ${PROJECT_USER}"
echo "   Password: ${PROJECT_PASSWORD}"
echo ""
echo "📊 Schemas disponíveis:"
echo "   - raw: Dados brutos do CSV"
echo "   - silver: Dados limpos e normalizados"
echo "   - gold: Data Mart analítico"
echo "==========================================="
