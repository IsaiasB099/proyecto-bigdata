## Proyecto Big Data 
Pipeline de Nómina — El proyecto es un pipeline de datos completo sobre la nómina de funcionarios públicos del Ministerio de Defensa Nacional de Paraguay (enero–marzo 2026). Atraviesa todo el stack del curso: desde los CSV crudos hasta un dashboard visual. (nóminas de funcionarios, meses 01-03/2026)

## Descripción 
qué problema resuelve, qué datos procesa, para qué sirven los reportes

## Stack tecnológico 
tabla con: Pentaho PDI, PostgreSQL, Python, DuckDB, Airflow, y las versiones

## Arquitectura del pipeline — 
 CSVs Drive → Pentaho ETL → raw.nomina_raw(PostgreSQL)
                             ↓
              staging.nomina (PostgreSQL, tipado)
                             ↓
            Script Python (validación de calidad)
                             ↓
                 DuckDB Marts (análisis OLAP)
                             ↓
                  Rstudio (dashboard visual)
                             ↓
                  Airflow DAG (orquesta todo)
                             ↓
                  GitHub (versiona el código)

## Estructura del repositorio
 📦data
 ┣ 📂duckdb
 ┃ ┣ 📜bigdata_lab.duckdb
 ┃ ┗ 📜proyecto_bigdata.duckdb
 ┣ 📂raw
 ┃ ┗ 📂nomina
 ┃ ┃ ┣ 📜nomina_2026-01.csv
 ┃ ┃ ┣ 📜nomina_2026-02.csv
 ┃ ┃ ┗ 📜nomina_2026-03.csv
 ┣ 📜Progreso del proyecto.md
 ┗ 📜data_README

 📦database
 ┣ 📂duckdb
 ┃ ┗ 📂marts
 ┃ ┃ ┗ 📜crear_marts_nomina.sql
 ┣ 📂postgresql
 ┃ ┗ 📂ddl
 ┃ ┃ ┣ 📜limpieza_y_tipado.sql
 ┃ ┃ ┣ 📜nomina_staging.sql
 ┃ ┃ ┗ 📜raw.nomina_raw.sql
 ┗ 📜README_database.md

 📦etl
 ┗ 📂pentaho
 ┃ ┗ 📂transformations
 ┃ ┃ ┗ 📜01_carga_nomina_raw.ktr

 📦reports
 ┣ 📜01_masa_salarial.png
 ┣ 📜02_distribucion_genero.png
 ┗ 📜03_conceptos_gasto.png

 📦scripts
 ┗ 📂python
 ┃ ┣ 📜02_validar_calidad_nomina.py
 ┃ ┣ 📜bigdata_lab.duckdb
 ┃ ┗ 📜ver_duckdb.py

## Requisitos previos
Python 3.10+, Pentaho PDI, PostgreSQL, Airflow; cómo configurar el .env, Rstudio, DuckDB, 

## Cómo ejecutar 
pasos ordenados: Paso 1 — ETL con Pentaho PDI Paso 2 — Modelado y Staging en PostgreSQL Paso 3 — Validación de calidad con Python Paso 4 — Data Marts analíticos en DuckDB Paso 5 — Orquestar todo con Airflow Paso 6 — Subir el repositorio a GitHub Paso 7 — Dashboard en Rstudio

## Resultados / Reportes 
(masa salarial, género, conceptos de gasto)