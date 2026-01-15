"""
Script para carregar dados do CSV para PostgreSQL
Crime Data from 2020 to Present - LAPD
"""

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from pathlib import Path
import sys
from datetime import datetime

# Configurações de conexão
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'crime_data',
    'user': 'sbd2',
    'password': 'sbd2_password'
}

# Caminho do CSV
CSV_PATH = Path(__file__).parent.parent / 'Crime_Data_from_2020_to_Present.csv'


def get_connection():
    """Cria conexão com o PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)


def load_raw_data(csv_path: Path, batch_size: int = 10000):
    """Carrega dados brutos do CSV para a camada raw"""
    
    print(f"📂 Lendo CSV: {csv_path}")
    
    # Ler CSV
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"   Registros lidos: {len(df):,}")
    
    # Mapear colunas do CSV para colunas do banco
    column_mapping = {
        'DR_NO': 'dr_no',
        'Date Rptd': 'date_rptd',
        'DATE OCC': 'date_occ',
        'TIME OCC': 'time_occ',
        'AREA': 'area',
        'AREA NAME': 'area_name',
        'Rpt Dist No': 'rpt_dist_no',
        'Part 1-2': 'part_1_2',
        'Crm Cd': 'crm_cd',
        'Crm Cd Desc': 'crm_cd_desc',
        'Mocodes': 'mocodes',
        'Vict Age': 'vict_age',
        'Vict Sex': 'vict_sex',
        'Vict Descent': 'vict_descent',
        'Premis Cd': 'premis_cd',
        'Premis Desc': 'premis_desc',
        'Weapon Used Cd': 'weapon_used_cd',
        'Weapon Desc': 'weapon_desc',
        'Status': 'status',
        'Status Desc': 'status_desc',
        'Crm Cd 1': 'crm_cd_1',
        'Crm Cd 2': 'crm_cd_2',
        'Crm Cd 3': 'crm_cd_3',
        'Crm Cd 4': 'crm_cd_4',
        'LOCATION': 'location',
        'Cross Street': 'cross_street',
        'LAT': 'lat',
        'LON': 'lon'
    }
    
    # Renomear colunas
    df = df.rename(columns=column_mapping)
    
    # Selecionar apenas colunas mapeadas
    cols = [v for v in column_mapping.values() if v in df.columns]
    df = df[cols]
    
    # Adicionar metadados
    df['source_file'] = csv_path.name
    
    # Conectar ao banco
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Limpar tabela existente
        print("🗑️  Limpando tabela raw.crime_data...")
        cursor.execute("TRUNCATE TABLE raw.crime_data")
        
        # Preparar inserção
        columns = df.columns.tolist()
        insert_query = sql.SQL("INSERT INTO raw.crime_data ({}) VALUES %s").format(
            sql.SQL(', ').join(map(sql.Identifier, columns))
        )
        
        # Inserir em batches
        print(f"📥 Inserindo dados em batches de {batch_size:,}...")
        
        total_inserted = 0
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            values = [tuple(row) for row in batch.values]
            execute_values(cursor, insert_query.as_string(conn), values)
            total_inserted += len(batch)
            print(f"   Progresso: {total_inserted:,}/{len(df):,} ({100*total_inserted/len(df):.1f}%)")
        
        conn.commit()
        print(f"✅ {total_inserted:,} registros inseridos na camada raw")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def transform_to_silver():
    """Transforma dados da camada raw para silver"""
    
    print("\n🔄 Transformando dados para camada Silver...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Popular dimensões primeiro
        print("   Populando dimensões...")
        
        # dim_areas
        cursor.execute("""
            INSERT INTO silver.dim_areas (area_code, area_name)
            SELECT DISTINCT area, area_name 
            FROM raw.crime_data 
            WHERE area IS NOT NULL
            ON CONFLICT (area_code) DO UPDATE SET area_name = EXCLUDED.area_name
        """)
        
        # dim_crime_types
        cursor.execute("""
            INSERT INTO silver.dim_crime_types (crime_code, crime_description, crime_part, is_violent, crime_category)
            SELECT DISTINCT 
                crm_cd,
                crm_cd_desc,
                part_1_2,
                CASE WHEN crm_cd_desc ~* 'ASSAULT|ROBBERY|HOMICIDE|RAPE|MURDER|KIDNAPPING|BATTERY|WEAPON|SHOOTING|MANSLAUGHTER' 
                     THEN TRUE ELSE FALSE END,
                CASE 
                    WHEN crm_cd_desc ~* 'HOMICIDE|MURDER|MANSLAUGHTER' THEN 'Homicídio'
                    WHEN crm_cd_desc ~* 'RAPE|SEXUAL' THEN 'Crime Sexual'
                    WHEN crm_cd_desc ~* 'KIDNAP' THEN 'Sequestro'
                    WHEN crm_cd_desc ~* 'ASSAULT|BATTERY' THEN 'Agressão'
                    WHEN crm_cd_desc ~* 'ROBBERY' THEN 'Roubo'
                    WHEN crm_cd_desc ~* 'BURGLARY' THEN 'Arrombamento'
                    WHEN crm_cd_desc ~* 'THEFT|STOLEN' THEN 'Furto'
                    WHEN crm_cd_desc ~* 'VANDALISM' THEN 'Vandalismo'
                    ELSE 'Outros'
                END
            FROM raw.crime_data 
            WHERE crm_cd IS NOT NULL
            ON CONFLICT (crime_code) DO UPDATE SET 
                crime_description = EXCLUDED.crime_description,
                is_violent = EXCLUDED.is_violent,
                crime_category = EXCLUDED.crime_category
        """)
        
        # dim_weapons
        cursor.execute("""
            INSERT INTO silver.dim_weapons (weapon_code, weapon_description)
            SELECT DISTINCT weapon_used_cd, weapon_desc 
            FROM raw.crime_data 
            WHERE weapon_used_cd IS NOT NULL
            ON CONFLICT (weapon_code) DO UPDATE SET weapon_description = EXCLUDED.weapon_description
        """)
        
        # dim_premises
        cursor.execute("""
            INSERT INTO silver.dim_premises (premise_code, premise_description, premise_category, is_public)
            SELECT DISTINCT 
                premis_cd, 
                premis_desc,
                CASE 
                    WHEN premis_desc ~* 'STREET|SIDEWALK|ALLEY|PARKING|PARK' THEN 'Via Pública'
                    WHEN premis_desc ~* 'DWELLING|HOUSE|APARTMENT|RESIDENCE' THEN 'Residência'
                    WHEN premis_desc ~* 'STORE|SHOP|RESTAURANT|BAR|BANK|HOTEL' THEN 'Estabelecimento Comercial'
                    WHEN premis_desc ~* 'SCHOOL|COLLEGE|UNIVERSITY' THEN 'Instituição de Ensino'
                    WHEN premis_desc ~* 'VEHICLE|CAR|TRUCK' THEN 'Veículo'
                    ELSE 'Outros'
                END,
                premis_desc ~* 'STREET|SIDEWALK|ALLEY|PARKING|PARK'
            FROM raw.crime_data 
            WHERE premis_cd IS NOT NULL
            ON CONFLICT (premise_code) DO UPDATE SET 
                premise_description = EXCLUDED.premise_description,
                premise_category = EXCLUDED.premise_category
        """)
        
        print("   ✅ Dimensões populadas")
        
        # Transformar e inserir na tabela principal
        print("   Transformando tabela principal...")
        
        cursor.execute("""
            INSERT INTO silver.crimes (
                crime_id, date_reported, date_occurred, time_occurred, hour_occurred,
                area_code, area_name, district_number, latitude, longitude, location, cross_street,
                crime_code, crime_description, crime_part,
                victim_age, victim_sex, victim_descent,
                premise_code, premise_description,
                weapon_code, weapon_description,
                status_code, status_description,
                year_occurred, month_occurred, day_of_week, day_name, is_weekend, period_of_day,
                is_violent, crime_category, age_group, descent_description
            )
            SELECT 
                dr_no,
                TO_DATE(date_rptd, 'MM/DD/YYYY HH24:MI:SS AM'),
                TO_DATE(date_occ, 'MM/DD/YYYY HH24:MI:SS AM'),
                TO_TIMESTAMP(LPAD(time_occ::TEXT, 4, '0'), 'HH24MI')::TIME,
                (time_occ::INT / 100),
                area,
                area_name,
                rpt_dist_no,
                lat,
                lon,
                location,
                cross_street,
                crm_cd,
                crm_cd_desc,
                part_1_2,
                vict_age,
                LEFT(vict_sex, 1),
                LEFT(vict_descent, 1),
                premis_cd,
                premis_desc,
                weapon_used_cd,
                weapon_desc,
                status,
                status_desc,
                EXTRACT(YEAR FROM TO_DATE(date_occ, 'MM/DD/YYYY HH24:MI:SS AM')),
                EXTRACT(MONTH FROM TO_DATE(date_occ, 'MM/DD/YYYY HH24:MI:SS AM')),
                EXTRACT(DOW FROM TO_DATE(date_occ, 'MM/DD/YYYY HH24:MI:SS AM')),
                TO_CHAR(TO_DATE(date_occ, 'MM/DD/YYYY HH24:MI:SS AM'), 'Day'),
                EXTRACT(DOW FROM TO_DATE(date_occ, 'MM/DD/YYYY HH24:MI:SS AM')) IN (0, 6),
                CASE 
                    WHEN (time_occ::INT / 100) >= 6 AND (time_occ::INT / 100) < 12 THEN 'Manhã'
                    WHEN (time_occ::INT / 100) >= 12 AND (time_occ::INT / 100) < 18 THEN 'Tarde'
                    WHEN (time_occ::INT / 100) >= 18 THEN 'Noite'
                    ELSE 'Madrugada'
                END,
                crm_cd_desc ~* 'ASSAULT|ROBBERY|HOMICIDE|RAPE|MURDER|KIDNAPPING|BATTERY|WEAPON|SHOOTING|MANSLAUGHTER',
                CASE 
                    WHEN crm_cd_desc ~* 'HOMICIDE|MURDER|MANSLAUGHTER' THEN 'Homicídio'
                    WHEN crm_cd_desc ~* 'RAPE|SEXUAL' THEN 'Crime Sexual'
                    WHEN crm_cd_desc ~* 'KIDNAP' THEN 'Sequestro'
                    WHEN crm_cd_desc ~* 'ASSAULT|BATTERY' THEN 'Agressão'
                    WHEN crm_cd_desc ~* 'ROBBERY' THEN 'Roubo'
                    WHEN crm_cd_desc ~* 'BURGLARY' THEN 'Arrombamento'
                    WHEN crm_cd_desc ~* 'THEFT|STOLEN' THEN 'Furto'
                    WHEN crm_cd_desc ~* 'VANDALISM' THEN 'Vandalismo'
                    ELSE 'Outros'
                END,
                CASE 
                    WHEN vict_age BETWEEN 0 AND 12 THEN '0-12'
                    WHEN vict_age BETWEEN 13 AND 17 THEN '13-17'
                    WHEN vict_age BETWEEN 18 AND 25 THEN '18-25'
                    WHEN vict_age BETWEEN 26 AND 35 THEN '26-35'
                    WHEN vict_age BETWEEN 36 AND 50 THEN '36-50'
                    WHEN vict_age BETWEEN 51 AND 65 THEN '51-65'
                    WHEN vict_age > 65 THEN '65+'
                    ELSE 'Desconhecido'
                END,
                d.descent_description
            FROM raw.crime_data r
            LEFT JOIN silver.dim_descent d ON LEFT(r.vict_descent, 1) = d.descent_code
            ON CONFLICT (crime_id) DO NOTHING
        """)
        
        conn.commit()
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM silver.crimes")
        count = cursor.fetchone()[0]
        print(f"   ✅ {count:,} registros na camada Silver")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Função principal"""
    print("="*60)
    print("🚀 CARGA DE DADOS - Crime Data LA")
    print("="*60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Carregar dados brutos
    if CSV_PATH.exists():
        load_raw_data(CSV_PATH)
    else:
        print(f"❌ CSV não encontrado: {CSV_PATH}")
        sys.exit(1)
    
    # 2. Transformar para Silver
    transform_to_silver()
    
    print()
    print("="*60)
    print(f"✅ Carga finalizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


if __name__ == "__main__":
    main()
