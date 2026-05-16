from airflow.sdk import dag, task
from datetime import datetime
import subprocess
import os

@dag(
    dag_id='pipeline_nomina_funcionarios',
    start_date=datetime(2026, 1, 1),
    schedule='@once',          
    catchup=False,
    tags=['nomina', 'funcionarios', 'bigdata']
)
def pipeline_nomina():

    @task()
    def ejecutar_pentaho_etl():
        """Lee los 3 CSVs de nómina y carga raw.nomina_raw en PostgreSQL"""
        subprocess.run([
            "/opt/pentaho/client-tools/data-integration/pan.sh",
            "-file=/opt/repo/proyecto-bigdata/etl/pentaho/transformations/01_carga_nomina_raw.ktr"
        ], check=True)
        print("ETL Pentaho completado — 3 meses cargados")

    @task()
    def staging_postgresql():
        """Ejecuta el INSERT RAW → STAGING con tipado y limpieza sin pedir clave"""
        env = os.environ.copy()
        env["PGPASSWORD"] = "bigdata123"
        
        subprocess.run([
            "psql", "-h", "localhost", "-U", "postgres",
            "-d", "proyecto_bigdata",
            "-f", "/opt/repo/proyecto-bigdata/database/postgresql/ddl/nomina_staging.sql",
            "--no-align", "--quiet"
        ], env=env, check=True)

    @task()
    def validar_calidad():
        """Valida nulos, duplicados y variación mensual de la nómina con el Python del venv"""
        subprocess.run([
            "/opt/repo/proyecto-bigdata/venv/bin/python",
            "/opt/repo/proyecto-bigdata/scripts/python/02_validar_calidad_nomina.py"
        ], check=True)

    @task()
    def actualizar_duckdb_marts():
        """Crea/actualiza los 3 marts analíticos en DuckDB leyendo el archivo correctamente"""
        # Aseguramos que la carpeta destino de DuckDB exista
        os.makedirs("/opt/repo/proyecto-bigdata/data/duckdb", exist_ok=True)
        
        # Sintaxis oficial de DuckDB para ejecutar un archivo .sql externo
        subprocess.run([
            "duckdb",
            "/opt/repo/proyecto-bigdata/data/duckdb/proyecto_bigdata.duckdb",
            "-c", ".read /opt/repo/proyecto-bigdata/database/duckdb/marts/crear_marts_nomina.sql"
        ], check=True)

    # Orden del pipeline
    etl   = ejecutar_pentaho_etl()
    stg   = staging_postgresql()
    cal   = validar_calidad()
    marts = actualizar_duckdb_marts()

    etl >> stg >> cal >> marts

pipeline_nomina()
