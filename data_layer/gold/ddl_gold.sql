-- ============================================
-- DDL - Camada Gold
-- Crime Data Analytics
-- ============================================

-- Schema para a camada Gold (Data Mart)
CREATE SCHEMA IF NOT EXISTS gold;

-- ============================================
-- FATO: Crimes
-- ============================================
CREATE TABLE IF NOT EXISTS gold.fato_crimes (
    sk_crime SERIAL PRIMARY KEY,
    nk_crime_id BIGINT NOT NULL,
    sk_area INTEGER REFERENCES gold.dim_area(sk_area),
    sk_crime_type INTEGER REFERENCES gold.dim_crime_type(sk_crime_type),
    sk_weapon INTEGER REFERENCES gold.dim_weapon(sk_weapon),
    sk_premise INTEGER REFERENCES gold.dim_premise(sk_premise),
    sk_date INTEGER REFERENCES gold.dim_date(sk_date),
    sk_time INTEGER REFERENCES gold.dim_time(sk_time),
    sk_victim INTEGER REFERENCES gold.dim_victim(sk_victim),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    is_violent BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DIMENSÃO: Área
-- ============================================
CREATE TABLE IF NOT EXISTS gold.dim_area (
    sk_area SERIAL PRIMARY KEY,
    area_code INTEGER NOT NULL,
    area_name VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    UNIQUE(area_code)
);

-- ============================================
-- DIMENSÃO: Tipo de Crime
-- ============================================
CREATE TABLE IF NOT EXISTS gold.dim_crime_type (
    sk_crime_type SERIAL PRIMARY KEY,
    crime_code INTEGER NOT NULL,
    crime_description VARCHAR(255) NOT NULL,
    crime_category VARCHAR(50),
    is_violent BOOLEAN DEFAULT FALSE,
    severity_level INTEGER,
    UNIQUE(crime_code)
);

-- ============================================
-- DIMENSÃO: Arma
-- ============================================
CREATE TABLE IF NOT EXISTS gold.dim_weapon (
    sk_weapon SERIAL PRIMARY KEY,
    weapon_code INTEGER,
    weapon_description VARCHAR(100),
    weapon_category VARCHAR(50),
    lethality_level INTEGER,
    UNIQUE(weapon_code)
);

-- ============================================
-- DIMENSÃO: Local (Premise)
-- ============================================
CREATE TABLE IF NOT EXISTS gold.dim_premise (
    sk_premise SERIAL PRIMARY KEY,
    premise_code INTEGER NOT NULL,
    premise_description VARCHAR(255) NOT NULL,
    premise_category VARCHAR(50),
    is_public BOOLEAN,
    UNIQUE(premise_code)
);

-- ============================================
-- DIMENSÃO: Data
-- ============================================
CREATE TABLE IF NOT EXISTS gold.dim_date (
    sk_date SERIAL PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    week_of_year INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN DEFAULT FALSE,
    UNIQUE(full_date)
);

-- ============================================
-- DIMENSÃO: Tempo
-- ============================================
CREATE TABLE IF NOT EXISTS gold.dim_time (
    sk_time SERIAL PRIMARY KEY,
    full_time TIME NOT NULL,
    hour INTEGER,
    minute INTEGER,
    period_of_day VARCHAR(20),
    is_rush_hour BOOLEAN,
    UNIQUE(full_time)
);

-- ============================================
-- DIMENSÃO: Vítima
-- ============================================
CREATE TABLE IF NOT EXISTS gold.dim_victim (
    sk_victim SERIAL PRIMARY KEY,
    age_group VARCHAR(20),
    sex CHAR(1),
    descent CHAR(1),
    descent_description VARCHAR(50),
    UNIQUE(age_group, sex, descent)
);

-- ============================================
-- AGREGAÇÕES PARA DASHBOARDS
-- ============================================

-- Agregação: Crimes por Área e Período
CREATE TABLE IF NOT EXISTS gold.agg_crimes_area_period (
    sk_area INTEGER,
    year INTEGER,
    month INTEGER,
    period_of_day VARCHAR(20),
    total_crimes INTEGER,
    violent_crimes INTEGER,
    property_crimes INTEGER,
    avg_victim_age DECIMAL(5,2),
    PRIMARY KEY (sk_area, year, month, period_of_day)
);

-- Agregação: Crimes por Tipo e Ano
CREATE TABLE IF NOT EXISTS gold.agg_crimes_type_year (
    sk_crime_type INTEGER,
    year INTEGER,
    total_crimes INTEGER,
    weekday_crimes INTEGER,
    weekend_crimes INTEGER,
    PRIMARY KEY (sk_crime_type, year)
);

-- Agregação: Hotspots Geográficos
CREATE TABLE IF NOT EXISTS gold.agg_crime_hotspots (
    grid_lat DECIMAL(8,4),
    grid_lon DECIMAL(8,4),
    year INTEGER,
    total_crimes INTEGER,
    violent_crimes INTEGER,
    hotspot_level VARCHAR(20),
    PRIMARY KEY (grid_lat, grid_lon, year)
);

-- ============================================
-- ÍNDICES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_fato_crimes_date ON gold.fato_crimes(sk_date);
CREATE INDEX IF NOT EXISTS idx_fato_crimes_area ON gold.fato_crimes(sk_area);
CREATE INDEX IF NOT EXISTS idx_fato_crimes_type ON gold.fato_crimes(sk_crime_type);
CREATE INDEX IF NOT EXISTS idx_fato_crimes_violent ON gold.fato_crimes(is_violent);
