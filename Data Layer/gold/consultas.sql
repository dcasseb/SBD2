-- ============================================
-- Consultas - Camada Gold
-- Crime Data Analytics (PostgreSQL)
-- ============================================

-- ============================================
-- 1. Total de crimes por área
-- ============================================
SELECT 
    da.area_name,
    da.region,
    COUNT(*) as total_crimes
FROM gold.fato_crimes fc
JOIN gold.dim_area da ON fc.sk_area = da.sk_area
GROUP BY da.area_name, da.region
ORDER BY total_crimes DESC;

-- ============================================
-- 2. Crimes por tipo e categoria
-- ============================================
SELECT 
    dct.crime_category,
    dct.crime_description,
    dct.is_violent,
    COUNT(*) as total_ocorrencias
FROM gold.fato_crimes fc
JOIN gold.dim_crime_type dct ON fc.sk_crime_type = dct.sk_crime_type
GROUP BY dct.crime_category, dct.crime_description, dct.is_violent
ORDER BY total_ocorrencias DESC;

-- ============================================
-- 3. Análise temporal - Crimes por ano e mês
-- ============================================
SELECT 
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN fc.is_violent THEN 1 ELSE 0 END) as violent_crimes
FROM gold.fato_crimes fc
JOIN gold.dim_date dd ON fc.sk_date = dd.sk_date
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;

-- ============================================
-- 4. Crimes por período do dia
-- ============================================
SELECT 
    dt.period_of_day,
    dt.hour,
    COUNT(*) as total_crimes
FROM gold.fato_crimes fc
JOIN gold.dim_time dt ON fc.sk_time = dt.sk_time
GROUP BY dt.period_of_day, dt.hour
ORDER BY dt.hour;

-- ============================================
-- 5. Top 10 armas mais utilizadas
-- ============================================
SELECT 
    dw.weapon_description,
    dw.weapon_category,
    dw.lethality_level,
    COUNT(*) as total_uso
FROM gold.fato_crimes fc
JOIN gold.dim_weapon dw ON fc.sk_weapon = dw.sk_weapon
WHERE dw.weapon_code IS NOT NULL
GROUP BY dw.weapon_description, dw.weapon_category, dw.lethality_level
ORDER BY total_uso DESC
LIMIT 10;

-- ============================================
-- 6. Análise de vítimas por faixa etária
-- ============================================
SELECT 
    dv.age_group,
    dv.sex,
    COUNT(*) as total_vitimas
FROM gold.fato_crimes fc
JOIN gold.dim_victim dv ON fc.sk_victim = dv.sk_victim
GROUP BY dv.age_group, dv.sex
ORDER BY total_vitimas DESC;

-- ============================================
-- 7. Crimes em finais de semana vs dias úteis
-- ============================================
SELECT 
    dd.is_weekend,
    COUNT(*) as total_crimes,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual
FROM gold.fato_crimes fc
JOIN gold.dim_date dd ON fc.sk_date = dd.sk_date
GROUP BY dd.is_weekend;

-- ============================================
-- 8. Locais mais perigosos (Premises)
-- ============================================
SELECT 
    dp.premise_description,
    dp.premise_category,
    dp.is_public,
    COUNT(*) as total_crimes
FROM gold.fato_crimes fc
JOIN gold.dim_premise dp ON fc.sk_premise = dp.sk_premise
GROUP BY dp.premise_description, dp.premise_category, dp.is_public
ORDER BY total_crimes DESC
LIMIT 20;

-- ============================================
-- 9. Mapa de calor - Crimes por localização
-- ============================================
SELECT 
    ROUND(fc.latitude::numeric, 2) as lat_group,
    ROUND(fc.longitude::numeric, 2) as lon_group,
    COUNT(*) as total_crimes
FROM gold.fato_crimes fc
WHERE fc.latitude IS NOT NULL AND fc.longitude IS NOT NULL
GROUP BY ROUND(fc.latitude::numeric, 2), ROUND(fc.longitude::numeric, 2)
ORDER BY total_crimes DESC;

-- ============================================
-- 10. Tendência anual de crimes violentos
-- ============================================
SELECT 
    dd.year,
    COUNT(*) as total_crimes,
    SUM(CASE WHEN fc.is_violent THEN 1 ELSE 0 END) as violent_crimes,
    ROUND(SUM(CASE WHEN fc.is_violent THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pct_violent
FROM gold.fato_crimes fc
JOIN gold.dim_date dd ON fc.sk_date = dd.sk_date
GROUP BY dd.year
ORDER BY dd.year;
