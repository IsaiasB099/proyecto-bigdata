## DAG: pipeline_nomina_funcionarios 
Un DAG de Airflow que ejecuta todo el pipeline en orden y de forma automática.

## Tareas y orden 
Las 3 tasks del DAG: ETL Pentaho → Staging PostgreSQL → Validación Python → Marts DuckDB

## Cómo levantar Airflow 
comandos: airflow standalone, el scheduler es: @once (solo 3 meses fijos), si se agregaran mas meses se cambia a @monthly, puerto por defecto (8080), trigger manual

## Configuración — Comando para arrancar el AIRFLOW                                          
cd /opt/repo/proyecto-bigdata
source venv/bin/activate
export AIRFLOW_HOME=/opt/repo/proyecto-bigdata/orchestration/airflow

## Iniciar servicio limpio
 airflow standalone
 