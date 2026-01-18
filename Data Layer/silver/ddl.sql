-- ============================================
-- DDL - Camada Silver
-- Crime Data from 2020 to Present
-- ============================================

-- Schema para a camada Silver
CREATE SCHEMA IF NOT EXISTS silver;

-- Tabela principal de crimes (dados limpos e normalizados)
CREATE TABLE IF NOT EXISTS silver.crimes (
    crime_id BIGINT PRIMARY KEY,
    date_reported DATE NOT NULL,
    date_occurred DATE NOT NULL,
    time_occurred TIME,
    hour_occurred INTEGER,
    area_code INTEGER NOT NULL,
    area_name VARCHAR(50),
    district_number INTEGER,
    crime_code INTEGER NOT NULL,
    crime_description VARCHAR(255),
    victim_age INTEGER,
    victim_sex CHAR(1),
    victim_descent CHAR(1),
    premise_code INTEGER,
    premise_description VARCHAR(255),
    weapon_code INTEGER,
    weapon_description VARCHAR(100),
    status_code VARCHAR(10),
    status_description VARCHAR(50),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    location VARCHAR(255),
    cross_street VARCHAR(100),
    -- Features derivadas
    year_occurred INTEGER,
    month_occurred INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN,
    period_of_day VARCHAR(20),
    is_violent BOOLEAN,
    age_group VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de dimensão: Áreas
CREATE TABLE IF NOT EXISTS silver.dim_areas (
    area_code INTEGER PRIMARY KEY,
    area_name VARCHAR(50) NOT NULL,
    total_crimes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de dimensão: Tipos de Crime
CREATE TABLE IF NOT EXISTS silver.dim_crime_types (
    crime_code INTEGER PRIMARY KEY,
    crime_description VARCHAR(255) NOT NULL,
    is_violent BOOLEAN DEFAULT FALSE,
    crime_category VARCHAR(50),
    total_occurrences INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de dimensão: Armas
CREATE TABLE IF NOT EXISTS silver.dim_weapons (
    weapon_code INTEGER PRIMARY KEY,
    weapon_description VARCHAR(100) NOT NULL,
    weapon_category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de dimensão: Locais (Premises)
CREATE TABLE IF NOT EXISTS silver.dim_premises (
    premise_code INTEGER PRIMARY KEY,
    premise_description VARCHAR(255) NOT NULL,
    premise_category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_crimes_date ON silver.crimes(date_occurred);
CREATE INDEX IF NOT EXISTS idx_crimes_area ON silver.crimes(area_code);
CREATE INDEX IF NOT EXISTS idx_crimes_type ON silver.crimes(crime_code);
CREATE INDEX IF NOT EXISTS idx_crimes_location ON silver.crimes(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_crimes_violent ON silver.crimes(is_violent);

-- View para análise temporal
CREATE OR REPLACE VIEW silver.vw_crimes_temporal AS
SELECT 
    year_occurred,
    month_occurred,
    day_of_week,
    period_of_day,
    is_weekend,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN is_violent THEN 1 ELSE 0 END) as violent_crimes,
    AVG(victim_age) as avg_victim_age
FROM silver.crimes
GROUP BY year_occurred, month_occurred, day_of_week, period_of_day, is_weekend;

-- View para análise por área
CREATE OR REPLACE VIEW silver.vw_crimes_by_area AS
SELECT 
    area_code,
    area_name,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN is_violent THEN 1 ELSE 0 END) as violent_crimes,
    COUNT(DISTINCT crime_code) as unique_crime_types,
    AVG(victim_age) as avg_victim_age
FROM silver.crimes
GROUP BY area_code, area_name;
