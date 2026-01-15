-- ============================================
-- DDL - Camada GOLD (Data Mart)
-- Modelo Dimensional para Análise
-- ============================================

-- ============================================
-- DIMENSÕES
-- ============================================

-- Dimensão: Data
CREATE TABLE IF NOT EXISTS gold.dim_date (
    sk_date SERIAL PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE
);

-- Dimensão: Tempo
CREATE TABLE IF NOT EXISTS gold.dim_time (
    sk_time SERIAL PRIMARY KEY,
    hour INTEGER NOT NULL UNIQUE,
    period_of_day VARCHAR(20) NOT NULL,
    is_rush_hour BOOLEAN NOT NULL,
    time_range VARCHAR(20) NOT NULL
);

-- Popular dim_time
INSERT INTO gold.dim_time (hour, period_of_day, is_rush_hour, time_range)
SELECT 
    h,
    CASE 
        WHEN h >= 6 AND h < 12 THEN 'Manhã'
        WHEN h >= 12 AND h < 18 THEN 'Tarde'
        WHEN h >= 18 AND h < 24 THEN 'Noite'
        ELSE 'Madrugada'
    END,
    h IN (7, 8, 9, 17, 18, 19),
    LPAD(h::text, 2, '0') || ':00-' || LPAD(((h+1) % 24)::text, 2, '0') || ':00'
FROM generate_series(0, 23) AS h
ON CONFLICT (hour) DO NOTHING;

-- Dimensão: Área
CREATE TABLE IF NOT EXISTS gold.dim_area (
    sk_area SERIAL PRIMARY KEY,
    area_code INTEGER NOT NULL UNIQUE,
    area_name VARCHAR(50) NOT NULL,
    region VARCHAR(50)
);

-- Dimensão: Tipo de Crime
CREATE TABLE IF NOT EXISTS gold.dim_crime_type (
    sk_crime_type SERIAL PRIMARY KEY,
    crime_code INTEGER NOT NULL UNIQUE,
    crime_description VARCHAR(255) NOT NULL,
    crime_category VARCHAR(50),
    is_violent BOOLEAN DEFAULT FALSE,
    is_serious BOOLEAN DEFAULT FALSE,
    severity_level INTEGER
);

-- Dimensão: Arma
CREATE TABLE IF NOT EXISTS gold.dim_weapon (
    sk_weapon SERIAL PRIMARY KEY,
    weapon_code INTEGER UNIQUE,
    weapon_description VARCHAR(100),
    weapon_category VARCHAR(50),
    lethality_level INTEGER
);

-- Inserir "Sem Arma" como padrão
INSERT INTO gold.dim_weapon (weapon_code, weapon_description, weapon_category, lethality_level)
VALUES (0, 'SEM ARMA', 'Nenhuma', 0)
ON CONFLICT (weapon_code) DO NOTHING;

-- Dimensão: Local (Premise)
CREATE TABLE IF NOT EXISTS gold.dim_premise (
    sk_premise SERIAL PRIMARY KEY,
    premise_code INTEGER NOT NULL UNIQUE,
    premise_description VARCHAR(255) NOT NULL,
    premise_category VARCHAR(50),
    is_public BOOLEAN
);

-- Dimensão: Perfil da Vítima
CREATE TABLE IF NOT EXISTS gold.dim_victim_profile (
    sk_victim_profile SERIAL PRIMARY KEY,
    age_group VARCHAR(20) NOT NULL,
    sex CHAR(1) NOT NULL,
    sex_description VARCHAR(20),
    descent CHAR(1),
    descent_description VARCHAR(50),
    UNIQUE(age_group, sex, descent)
);

-- ============================================
-- FATO: Crimes
-- ============================================
CREATE TABLE IF NOT EXISTS gold.fato_crimes (
    sk_crime SERIAL PRIMARY KEY,
    nk_crime_id BIGINT NOT NULL UNIQUE,
    -- Foreign Keys para dimensões
    sk_date INTEGER REFERENCES gold.dim_date(sk_date),
    sk_time INTEGER REFERENCES gold.dim_time(sk_time),
    sk_area INTEGER REFERENCES gold.dim_area(sk_area),
    sk_crime_type INTEGER REFERENCES gold.dim_crime_type(sk_crime_type),
    sk_weapon INTEGER REFERENCES gold.dim_weapon(sk_weapon),
    sk_premise INTEGER REFERENCES gold.dim_premise(sk_premise),
    sk_victim_profile INTEGER REFERENCES gold.dim_victim_profile(sk_victim_profile),
    -- Métricas e atributos
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    is_violent BOOLEAN,
    is_serious BOOLEAN,
    victim_age INTEGER,
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- AGREGAÇÕES (Tabelas pré-calculadas)
-- ============================================

-- Agregação: Crimes por Área e Mês
CREATE TABLE IF NOT EXISTS gold.agg_crimes_area_month (
    sk_area INTEGER REFERENCES gold.dim_area(sk_area),
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    total_crimes INTEGER NOT NULL,
    violent_crimes INTEGER DEFAULT 0,
    serious_crimes INTEGER DEFAULT 0,
    property_crimes INTEGER DEFAULT 0,
    avg_victim_age DECIMAL(5,2),
    pct_violent DECIMAL(5,2),
    PRIMARY KEY (sk_area, year, month)
);

-- Agregação: Crimes por Tipo e Ano
CREATE TABLE IF NOT EXISTS gold.agg_crimes_type_year (
    sk_crime_type INTEGER REFERENCES gold.dim_crime_type(sk_crime_type),
    year INTEGER NOT NULL,
    total_crimes INTEGER NOT NULL,
    weekday_crimes INTEGER DEFAULT 0,
    weekend_crimes INTEGER DEFAULT 0,
    morning_crimes INTEGER DEFAULT 0,
    afternoon_crimes INTEGER DEFAULT 0,
    night_crimes INTEGER DEFAULT 0,
    dawn_crimes INTEGER DEFAULT 0,
    PRIMARY KEY (sk_crime_type, year)
);

-- Agregação: Hotspots Geográficos
CREATE TABLE IF NOT EXISTS gold.agg_crime_hotspots (
    grid_lat DECIMAL(6,3) NOT NULL,
    grid_lon DECIMAL(6,3) NOT NULL,
    year INTEGER NOT NULL,
    total_crimes INTEGER NOT NULL,
    violent_crimes INTEGER DEFAULT 0,
    serious_crimes INTEGER DEFAULT 0,
    hotspot_level VARCHAR(20),
    PRIMARY KEY (grid_lat, grid_lon, year)
);

-- Agregação: Crimes Graves por Área e Ano
CREATE TABLE IF NOT EXISTS gold.agg_serious_crimes (
    sk_area INTEGER REFERENCES gold.dim_area(sk_area),
    year INTEGER NOT NULL,
    homicides INTEGER DEFAULT 0,
    rapes INTEGER DEFAULT 0,
    kidnappings INTEGER DEFAULT 0,
    total_serious INTEGER DEFAULT 0,
    PRIMARY KEY (sk_area, year)
);

-- ============================================
-- ÍNDICES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_fato_date ON gold.fato_crimes(sk_date);
CREATE INDEX IF NOT EXISTS idx_fato_area ON gold.fato_crimes(sk_area);
CREATE INDEX IF NOT EXISTS idx_fato_crime_type ON gold.fato_crimes(sk_crime_type);
CREATE INDEX IF NOT EXISTS idx_fato_violent ON gold.fato_crimes(is_violent);
CREATE INDEX IF NOT EXISTS idx_fato_serious ON gold.fato_crimes(is_serious);
CREATE INDEX IF NOT EXISTS idx_fato_location ON gold.fato_crimes(latitude, longitude);

-- ============================================
-- VIEWS PARA DASHBOARDS
-- ============================================

-- View: Resumo Executivo
CREATE OR REPLACE VIEW gold.vw_executive_summary AS
SELECT 
    d.year,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN f.is_violent THEN 1 ELSE 0 END) as violent_crimes,
    SUM(CASE WHEN f.is_serious THEN 1 ELSE 0 END) as serious_crimes,
    ROUND(100.0 * SUM(CASE WHEN f.is_violent THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_violent,
    COUNT(DISTINCT f.sk_area) as areas_affected,
    COUNT(DISTINCT f.sk_crime_type) as crime_types
FROM gold.fato_crimes f
JOIN gold.dim_date d ON f.sk_date = d.sk_date
GROUP BY d.year
ORDER BY d.year;

-- View: Top Áreas Perigosas
CREATE OR REPLACE VIEW gold.vw_dangerous_areas AS
SELECT 
    a.area_name,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN f.is_violent THEN 1 ELSE 0 END) as violent_crimes,
    SUM(CASE WHEN f.is_serious THEN 1 ELSE 0 END) as serious_crimes,
    ROUND(100.0 * SUM(CASE WHEN f.is_violent THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_violent
FROM gold.fato_crimes f
JOIN gold.dim_area a ON f.sk_area = a.sk_area
GROUP BY a.area_name
ORDER BY total_crimes DESC;

-- View: Crimes por Período do Dia
CREATE OR REPLACE VIEW gold.vw_crimes_by_period AS
SELECT 
    t.period_of_day,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN f.is_violent THEN 1 ELSE 0 END) as violent_crimes,
    ROUND(AVG(f.victim_age), 1) as avg_victim_age
FROM gold.fato_crimes f
JOIN gold.dim_time t ON f.sk_time = t.sk_time
WHERE f.victim_age > 0 AND f.victim_age < 100
GROUP BY t.period_of_day;
