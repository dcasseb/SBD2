FROM jupyter/pyspark-notebook:latest

USER root

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

# Instalar dependências Python
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar código fonte
COPY src/ /home/jovyan/src/
COPY spark_config/ /home/jovyan/spark_config/
