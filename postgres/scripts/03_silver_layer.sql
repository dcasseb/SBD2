-- ============================================
-- DDL - Camada SILVER
-- Dados limpos, tipados e enriquecidos
-- ============================================

-- ============================================
-- TABELA PRINCIPAL: Crimes
-- ============================================
CREATE TABLE IF NOT EXISTS silver.crimes (
    crime_id BIGINT PRIMARY KEY,
    -- Datas e horários
    date_reported DATE NOT NULL,
    date_occurred DATE NOT NULL,
    time_occurred TIME,
    hour_occurred INTEGER CHECK (hour_occurred >= 0 AND hour_occurred <= 23),
    -- Localização
    area_code INTEGER NOT NULL,
    area_name VARCHAR(50),
    district_number INTEGER,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    location VARCHAR(255),
    cross_street VARCHAR(100),
    -- Crime
    crime_code INTEGER NOT NULL,
    crime_description VARCHAR(255),
    crime_part INTEGER CHECK (crime_part IN (1, 2)),
    -- Vítima
    victim_age INTEGER,
    victim_sex CHAR(1),
    victim_descent CHAR(1),
    -- Local do crime
    premise_code INTEGER,
    premise_description VARCHAR(255),
    -- Arma
    weapon_code INTEGER,
    weapon_description VARCHAR(100),
    -- Status
    status_code VARCHAR(10),
    status_description VARCHAR(50),
    -- Features derivadas
    year_occurred INTEGER,
    month_occurred INTEGER,
    day_of_week INTEGER CHECK (day_of_week >= 0 AND day_of_week <= 6),
    day_name VARCHAR(15),
    is_weekend BOOLEAN,
    period_of_day VARCHAR(20),
    is_violent BOOLEAN,
    crime_category VARCHAR(50),
    age_group VARCHAR(20),
    descent_description VARCHAR(50),
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DIMENSÕES (para normalização)
-- ============================================

-- Dimensão: Áreas
CREATE TABLE IF NOT EXISTS silver.dim_areas (
    area_code INTEGER PRIMARY KEY,
    area_name VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    total_crimes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensão: Tipos de Crime
CREATE TABLE IF NOT EXISTS silver.dim_crime_types (
    crime_code INTEGER PRIMARY KEY,
    crime_description VARCHAR(255) NOT NULL,
    crime_part INTEGER,
    is_violent BOOLEAN DEFAULT FALSE,
    crime_category VARCHAR(50),
    severity_level INTEGER,
    total_occurrences INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensão: Armas
CREATE TABLE IF NOT EXISTS silver.dim_weapons (
    weapon_code INTEGER PRIMARY KEY,
    weapon_description VARCHAR(100) NOT NULL,
    weapon_category VARCHAR(50),
    lethality_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensão: Locais (Premises)
CREATE TABLE IF NOT EXISTS silver.dim_premises (
    premise_code INTEGER PRIMARY KEY,
    premise_description VARCHAR(255) NOT NULL,
    premise_category VARCHAR(50),
    is_public BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimensão: Descendência/Etnia
CREATE TABLE IF NOT EXISTS silver.dim_descent (
    descent_code CHAR(1) PRIMARY KEY,
    descent_description VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Popular dim_descent
INSERT INTO silver.dim_descent (descent_code, descent_description) VALUES
    ('A', 'Asiático'),
    ('B', 'Negro'),
    ('C', 'Chinês'),
    ('D', 'Cambojano'),
    ('F', 'Filipino'),
    ('G', 'Guamense'),
    ('H', 'Hispânico/Latino'),
    ('I', 'Indígena Americano'),
    ('J', 'Japonês'),
    ('K', 'Coreano'),
    ('L', 'Laosiano'),
    ('O', 'Outro'),
    ('P', 'Ilhas do Pacífico'),
    ('S', 'Samoano'),
    ('U', 'Havaiano'),
    ('V', 'Vietnamita'),
    ('W', 'Branco'),
    ('X', 'Desconhecido'),
    ('Z', 'Indiano Asiático'),
    ('-', 'Não Informado')
ON CONFLICT (descent_code) DO NOTHING;

-- ============================================
-- ÍNDICES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_crimes_date ON silver.crimes(date_occurred);
CREATE INDEX IF NOT EXISTS idx_crimes_year_month ON silver.crimes(year_occurred, month_occurred);
CREATE INDEX IF NOT EXISTS idx_crimes_area ON silver.crimes(area_code);
CREATE INDEX IF NOT EXISTS idx_crimes_type ON silver.crimes(crime_code);
CREATE INDEX IF NOT EXISTS idx_crimes_location ON silver.crimes(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_crimes_violent ON silver.crimes(is_violent);
CREATE INDEX IF NOT EXISTS idx_crimes_category ON silver.crimes(crime_category);
CREATE INDEX IF NOT EXISTS idx_crimes_period ON silver.crimes(period_of_day);

-- ============================================
-- VIEWS ANALÍTICAS
-- ============================================

-- View: Análise Temporal
CREATE OR REPLACE VIEW silver.vw_crimes_temporal AS
SELECT 
    year_occurred,
    month_occurred,
    day_of_week,
    day_name,
    period_of_day,
    is_weekend,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN is_violent THEN 1 ELSE 0 END) as violent_crimes,
    ROUND(AVG(victim_age), 1) as avg_victim_age
FROM silver.crimes
WHERE victim_age > 0 AND victim_age < 100
GROUP BY year_occurred, month_occurred, day_of_week, day_name, period_of_day, is_weekend;

-- View: Análise por Área
CREATE OR REPLACE VIEW silver.vw_crimes_by_area AS
SELECT 
    area_code,
    area_name,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN is_violent THEN 1 ELSE 0 END) as violent_crimes,
    ROUND(100.0 * SUM(CASE WHEN is_violent THEN 1 ELSE 0 END) / COUNT(*), 2) as violent_pct,
    COUNT(DISTINCT crime_code) as unique_crime_types
FROM silver.crimes
GROUP BY area_code, area_name
ORDER BY total_crimes DESC;

-- View: Crimes Graves
CREATE OR REPLACE VIEW silver.vw_serious_crimes AS
SELECT *
FROM silver.crimes
WHERE crime_description ILIKE '%HOMICIDE%'
   OR crime_description ILIKE '%RAPE%'
   OR crime_description ILIKE '%KIDNAP%'
   OR crime_description ILIKE '%MANSLAUGHTER%'
   OR crime_description ILIKE '%SEXUAL PENETRATION%'
   OR crime_description ILIKE '%SODOMY%';

COMMENT ON VIEW silver.vw_serious_crimes IS 'Crimes graves: Homicídio, Estupro, Sequestro';
