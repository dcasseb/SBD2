"""
Configuração do Apache Spark
SBD2 - Crime Data Pipeline
"""

import os
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf


def get_spark_config() -> SparkConf:
    """Retorna configuração do Spark"""
    conf = SparkConf()
    
    # Configurações básicas
    conf.setAppName("SBD2 - Crime Data Pipeline")
    conf.setMaster(os.getenv('SPARK_MASTER_URL', 'local[*]'))
    
    # Memória
    conf.set("spark.driver.memory", os.getenv('SPARK_DRIVER_MEMORY', '2g'))
    conf.set("spark.executor.memory", os.getenv('SPARK_EXECUTOR_MEMORY', '2g'))
    conf.set("spark.executor.cores", "2")
    
    # Configurações de performance
    conf.set("spark.sql.shuffle.partitions", "200")
    conf.set("spark.default.parallelism", "100")
    conf.set("spark.sql.adaptive.enabled", "true")
    conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
    
    # Configurações de serialização
    conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    conf.set("spark.kryoserializer.buffer.max", "512m")
    
    # Configurações de I/O
    conf.set("spark.sql.parquet.compression.codec", "snappy")
    conf.set("spark.sql.csv.parser.columnPruning.enabled", "true")
    
    # PostgreSQL JDBC
    conf.set("spark.jars.packages", "org.postgresql:postgresql:42.6.0")
    
    # Delta Lake (opcional)
    # conf.set("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0")
    # conf.set("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    
    return conf


def create_spark_session(app_name: str = None) -> SparkSession:
    """Cria sessão Spark com configurações otimizadas"""
    conf = get_spark_config()
    
    if app_name:
        conf.setAppName(app_name)
    
    spark = SparkSession.builder \
        .config(conf=conf) \
        .getOrCreate()
    
    # Configurar log level
    spark.sparkContext.setLogLevel("WARN")
    
    return spark


def get_postgres_url() -> str:
    """Retorna URL de conexão PostgreSQL para Spark"""
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    database = os.getenv('SBD2_POSTGRES_DB', 'crime_data')
    
    return f"jdbc:postgresql://{host}:{port}/{database}"


def get_postgres_properties() -> dict:
    """Retorna propriedades de conexão PostgreSQL"""
    return {
        "user": os.getenv('SBD2_POSTGRES_USER', 'sbd2'),
        "password": os.getenv('SBD2_POSTGRES_PASSWORD', 'sbd2_password'),
        "driver": "org.postgresql.Driver"
    }


# Caminhos padrão
DATA_PATHS = {
    'raw': '/data/raw',
    'silver': '/data/silver',
    'gold': '/data/gold',
    'crime_data': '/data/raw/crime_data/Crime_Data_from_2020_to_Present.csv'
}


# Schema do dataset de crimes
CRIME_SCHEMA = """
    DR_NO BIGINT,
    `Date Rptd` STRING,
    `DATE OCC` STRING,
    `TIME OCC` STRING,
    AREA INT,
    `AREA NAME` STRING,
    `Rpt Dist No` INT,
    `Part 1-2` INT,
    `Crm Cd` INT,
    `Crm Cd Desc` STRING,
    Mocodes STRING,
    `Vict Age` INT,
    `Vict Sex` STRING,
    `Vict Descent` STRING,
    `Premis Cd` INT,
    `Premis Desc` STRING,
    `Weapon Used Cd` INT,
    `Weapon Desc` STRING,
    Status STRING,
    `Status Desc` STRING,
    `Crm Cd 1` INT,
    `Crm Cd 2` INT,
    `Crm Cd 3` INT,
    `Crm Cd 4` INT,
    LOCATION STRING,
    `Cross Street` STRING,
    LAT DOUBLE,
    LON DOUBLE
"""
