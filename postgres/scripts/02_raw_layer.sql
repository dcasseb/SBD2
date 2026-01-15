-- ============================================
-- DDL - Camada RAW (Bronze)
-- Tabela espelho do CSV original
-- ============================================

-- Tabela para importação direta do CSV
CREATE TABLE IF NOT EXISTS raw.crime_data (
    dr_no BIGINT,                           -- Division of Records Number
    date_rptd VARCHAR(50),                  -- Date Reported
    date_occ VARCHAR(50),                   -- Date of Occurrence
    time_occ VARCHAR(10),                   -- Time of Occurrence (HHMM)
    area INTEGER,                           -- Area Code
    area_name VARCHAR(100),                 -- Area Name
    rpt_dist_no INTEGER,                    -- Reporting District Number
    part_1_2 INTEGER,                       -- Crime Part (1 or 2)
    crm_cd INTEGER,                         -- Crime Code
    crm_cd_desc VARCHAR(255),               -- Crime Code Description
    mocodes VARCHAR(500),                   -- Modus Operandi Codes
    vict_age INTEGER,                       -- Victim Age
    vict_sex VARCHAR(5),                    -- Victim Sex
    vict_descent VARCHAR(5),                -- Victim Descent
    premis_cd INTEGER,                      -- Premise Code
    premis_desc VARCHAR(255),               -- Premise Description
    weapon_used_cd INTEGER,                 -- Weapon Used Code
    weapon_desc VARCHAR(255),               -- Weapon Description
    status VARCHAR(10),                     -- Status Code
    status_desc VARCHAR(100),               -- Status Description
    crm_cd_1 INTEGER,                       -- Crime Code 1
    crm_cd_2 INTEGER,                       -- Crime Code 2
    crm_cd_3 INTEGER,                       -- Crime Code 3
    crm_cd_4 INTEGER,                       -- Crime Code 4
    location VARCHAR(255),                  -- Street Address
    cross_street VARCHAR(255),              -- Cross Street
    lat DECIMAL(12, 8),                     -- Latitude
    lon DECIMAL(12, 8),                     -- Longitude
    -- Metadados de carga
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_file VARCHAR(255)
);

-- Índices para a camada raw
CREATE INDEX IF NOT EXISTS idx_raw_dr_no ON raw.crime_data(dr_no);
CREATE INDEX IF NOT EXISTS idx_raw_crm_cd ON raw.crime_data(crm_cd);
CREATE INDEX IF NOT EXISTS idx_raw_area ON raw.crime_data(area);

COMMENT ON TABLE raw.crime_data IS 'Dados brutos importados do CSV Crime_Data_from_2020_to_Present';
