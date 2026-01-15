-- ============================================
-- Criação de Schemas - Crime Data LA
-- Arquitetura Medallion: Raw -> Silver -> Gold
-- ============================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Busca por similaridade

-- ============================================
-- SCHEMA RAW (Bronze) - Dados brutos
-- ============================================
CREATE SCHEMA IF NOT EXISTS raw;
COMMENT ON SCHEMA raw IS 'Camada Bronze - Dados brutos importados do CSV';

-- ============================================
-- SCHEMA SILVER - Dados limpos e normalizados
-- ============================================
CREATE SCHEMA IF NOT EXISTS silver;
COMMENT ON SCHEMA silver IS 'Camada Silver - Dados limpos, tipados e enriquecidos';

-- ============================================
-- SCHEMA GOLD - Data Mart Analítico
-- ============================================
CREATE SCHEMA IF NOT EXISTS gold;
COMMENT ON SCHEMA gold IS 'Camada Gold - Modelo dimensional para análise';

-- Conceder permissões
GRANT ALL PRIVILEGES ON SCHEMA raw TO sbd2;
GRANT ALL PRIVILEGES ON SCHEMA silver TO sbd2;
GRANT ALL PRIVILEGES ON SCHEMA gold TO sbd2;

-- Definir search_path padrão
ALTER USER sbd2 SET search_path TO gold, silver, raw, public;
