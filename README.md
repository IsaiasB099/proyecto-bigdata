Preparar el dataset
El dataset es la nómina de funcionarios públicos del Paraguay (Ministerio de Defensa Nacional), con 41 columnas que describen la estructura organizacional, datos personales del funcionario, concepto de gasto y montos presupuestados/devengados. Son 3 archivos mensuales: enero, febrero y marzo 2026.

Archivos del dataset (Google Drive)
nomina_enero_2026.csv
nomina_febrero_2026.csv
nomina_marzo_2026.csv

Columnas principales del dataset
anio, mes — período de la nómina
codigoPersona — ID único del funcionario
nombres, apellidos — nombre completo
sexo, discapacidad — datos demográficos
descripcionEntidad — institución (MDN)
descripcionUnidadResponsable — unidad interna
cargo, codigoCategoria — rango/categoría
fechaIngreso, tipoPersonal — antigüedad
conceptoGasto — tipo (sueldo, bono, subsidio)
fuenteFinanciamiento — origen del fondos
montoPresupuestado — monto planificado (Gs.)
montoDevengado — monto efectivamente pagado (Gs.)

# Crear estructura de carpetas del proyecto en WSL2
mkdir -p /opt/repo/proyecto-bigdata/data/raw/nomina
mkdir -p /opt/repo/proyecto-bigdata/data/duckdb
mkdir -p /opt/repo/proyecto-bigdata/etl/pentaho/transformations
mkdir -p /opt/repo/proyecto-bigdata/scripts/python
mkdir -p /opt/repo/proyecto-bigdata/orchestration/airflow/dags
mkdir -p /opt/repo/proyecto-bigdata/database/postgresql/ddl
mkdir -p /opt/repo/proyecto-bigdata/reports

# Copiar los 3 CSVs descargados de Drive:
cp ~/Downloads/nomina_enero_2026.csv   /opt/repo/proyecto-bigdata/data/raw/nomina/
cp ~/Downloads/nomina_febrero_2026.csv /opt/repo/proyecto-bigdata/data/raw/nomina/
cp ~/Downloads/nomina_marzo_2026.csv   /opt/repo/proyecto-bigdata/data/raw/nomina/

# Verificar cantidad de registros por mes:
wc -l /opt/repo/proyecto-bigdata/data/raw/nomina/*.csv

# Ver las columnas del dataset:
head -1 /opt/repo/proyecto-bigdata/data/raw/nomina/nomina_enero_2026.csv

Los 3 archivos tienen la misma estructura de columnas (mismo mes de inicio 2026). No los unificás todavía — Pentaho los procesa uno por uno y los carga todos a la misma tabla RAW con el campo mes como discriminador.
Descargar los 3 archivos de nómina desde Google Drive
Copiar a data/raw/nomina/ y verificar con wc -l
Revisar el encabezado con head -1 y entender las 41 columnas
Identificar los campos clave: codigoPersona, conceptoGasto, montoDevengado

1 ETL con Pentaho PDI
Pentaho Data Integration — Spoon
Crear una Transformation que procese los 3 archivos CSV de nómina secuencialmente, seleccione las columnas relevantes, filtre registros inconsistentes (montos negativos, códigos de persona nulos) y cargue todo en PostgreSQL esquema RAW con una sola tabla mensual consolidada.

# Abrir Spoon desde WSL2:
cd /opt/pentaho/data-integration
./spoon.sh

# En Spoon crear nueva Transformation (.ktr) con estos pasos:
# 1. CSV File Input (repetido 3 veces, uno por mes, o usar "Get File Names")
#    Separador: coma | Encabezado: sí | Encoding: UTF-8
#    Apuntar a: data/raw/nomina/nomina_enero_2026.csv
#               data/raw/nomina/nomina_febrero_2026.csv
#               data/raw/nomina/nomina_marzo_2026.csv

# 2. Select Values → seleccionar columnas necesarias:
#    Identificación: anio, mes, codigoPersona, nombres, apellidos, sexo, discapacidad
#    Org:  codigoNivel, descripcionNivel, codigoEntidad, descripcionEntidad
#          codigoPrograma, descripcionPrograma, codigoUnidadResponsable, descripcionUnidadResponsable
#    Gasto: codigoObjetoGasto, conceptoGasto, fuenteFinanciamiento, linea
#    Cargo: codigoCategoria, cargo, horasCatedra, fechaIngreso, tipoPersonal, lugar
#    Montos: montoPresupuestado, montoDevengado

# 3. Filter Rows → eliminar filas inválidas:
#    codigoPersona IS NULL → descartar
#    montoDevengado < 0    → descartar
#    montoPresupuestado < 0 → descartar

# 4. String operations → trim() en nombres, apellidos, cargo, descripcionEntidad

# 5. Table Output → PostgreSQL
#    Schema: raw | Table: nomina_raw

# Guardar como:
# etl/pentaho/transformations/01_carga_nomina_raw.ktr

En Spoon usá el step "Get File Names" apuntando al directorio data/raw/nomina/ con filtro *.csv, seguido de "CSV File Input" en modo "Accept file names from previous step". Así procesás los 3 archivos con una sola Transformation sin duplicar steps.
El CSV usa comillas dobles anidadas (""campo"") para escapar valores con comas. Configurá bien el "Enclosure character" en CSV File Input: usar comilla doble ". Si no, los campos de descripción van a quedar mal parseados.
Crear la Transformation 01_carga_nomina_raw.ktr en Spoon
Configurar "Get File Names" + CSV File Input para los 3 CSVs
Agregar Select Values con las columnas clave
Agregar Filter Rows para montos negativos y personas sin código
Configurar Table Output hacia PostgreSQL esquema raw y ejecutar

2 Modelado y Staging en PostgreSQL
PostgreSQL 15 + DBeaver
Crear las tablas con DDL correcto, tipar columnas (montos como BIGINT en guaraníes, fechas como DATE), normalizar texto y mover datos de RAW a STAGING con limpieza adicional.

-- Crear esquemas (ejecutar en DBeaver)
CREATE SCHEMA IF NOT EXISTS
 raw;
CREATE SCHEMA IF NOT EXISTS
 staging;

-- Tabla RAW (espejo del CSV, todo texto)
CREATE TABLE
 raw.nomina_raw (
    id                          SERIAL PRIMARY KEY,
    anio                        TEXT,
    mes                         TEXT,
    codigoNivel                 TEXT,
    descripcionNivel            TEXT,
    codigoEntidad               TEXT,
    descripcionEntidad          TEXT,
    codigoPrograma              TEXT,
    descripcionPrograma         TEXT,
    codigoSubprograma           TEXT,
    descripcionSubprograma      TEXT,
    codigoProyecto              TEXT,
    descripcionProyecto         TEXT,
    codigoUnidadResponsable     TEXT,
    descripcionUnidadResponsable TEXT,
    codigoObjetoGasto           TEXT,
    conceptoGasto               TEXT,
    fuenteFinanciamiento        TEXT,
    linea                       TEXT,
    codigoPersona               TEXT,
    nombres                     TEXT,
    apellidos                   TEXT,
    sexo                        TEXT,
    discapacidad                TEXT,
    codigoCategoria             TEXT,
    cargo                       TEXT,
    horasCatedra                TEXT,
    fechaIngreso                TEXT,
    tipoPersonal                TEXT,
    lugar                       TEXT,
    montoPresupuestado          TEXT,
    montoDevengado              TEXT,
    mesCorte                    TEXT,
    anioCorte                   TEXT,
    fechaCorte                  TEXT,
    cargado_en                  TIMESTAMP 
DEFAULT
 NOW()
);

-- Tabla STAGING (datos tipados y limpios)
CREATE TABLE
 staging.nomina (
    id                          SERIAL PRIMARY KEY,
    anio                        SMALLINT,
    mes                         SMALLINT,
    codigo_nivel                SMALLINT,
    descripcion_nivel           VARCHAR(60),
    codigo_entidad              SMALLINT,
    descripcion_entidad         VARCHAR(120),
    codigo_programa             SMALLINT,
    descripcion_programa        VARCHAR(120),
    codigo_unidad               SMALLINT,
    descripcion_unidad          VARCHAR(200),
    codigo_objeto_gasto         SMALLINT,
    concepto_gasto              VARCHAR(200),
    fuente_financiamiento       VARCHAR(60),
    linea                       SMALLINT,
    codigo_persona              BIGINT,
    nombres                     VARCHAR(100),
    apellidos                   VARCHAR(100),
    sexo                        CHAR(1),           -- M / F
    discapacidad                CHAR(1),           -- S / N
    codigo_categoria            VARCHAR(10),
    cargo                       VARCHAR(200),
    fecha_ingreso               DATE,
    tipo_personal               VARCHAR(10),
    monto_presupuestado         BIGINT,            -- en guaraníes
    monto_devengado             BIGINT,            -- en guaraníes
    diferencia_monto            BIGINT             -- presupuestado - devengado
        GENERATED ALWAYS AS (monto_presupuestado - monto_devengado) STORED,
    procesado_en                TIMESTAMP 
DEFAULT
 NOW()
);

-- Pasar de RAW a STAGING con limpieza y tipado
INSERT INTO
 staging.nomina (
    anio, mes, codigo_nivel, descripcion_nivel,
    codigo_entidad, descripcion_entidad,
    codigo_programa, descripcion_programa,
    codigo_unidad, descripcion_unidad,
    codigo_objeto_gasto, concepto_gasto, fuente_financiamiento, linea,
    codigo_persona, nombres, apellidos, sexo, discapacidad,
    codigo_categoria, cargo, fecha_ingreso, tipo_personal,
    monto_presupuestado, monto_devengado
)
SELECT

    anio::SMALLINT,
    mes::SMALLINT,
    codigonivel::SMALLINT,
    INITCAP(TRIM(descripcionnivel)),
    codigoentidad::SMALLINT,
    TRIM(descripcionentidad),
    codigoprograma::SMALLINT,
    TRIM(descripcionprograma),
    codigounidadresponsable::SMALLINT,
    TRIM(descripcionunidadresponsable),
    codigoobjetogasto::SMALLINT,
    TRIM(conceptogasto),
    TRIM(fuentefinanciamiento),
    linea::SMALLINT,
    codigopersona::BIGINT,
    INITCAP(TRIM(nombres)),
    INITCAP(TRIM(apellidos)),
    UPPER(TRIM(sexo)),
    UPPER(TRIM(discapacidad)),
    TRIM(codigocategoria),
    TRIM(cargo),
    NULLIF(TRIM(fechaingreso), '')::DATE,
    TRIM(tipopersonal),
    montoPresupuestado::BIGINT,
    montoDevengado::BIGINT
FROM
 raw.nomina_raw
WHERE
 codigoPersona IS NOT NULL
  
AND
 codigoPersona != ''
  
AND
 montoDevengado::BIGINT >= 0;

Los montos están en guaraníes (sin decimales, valores de millones). No los conviertas a NUMERIC — usá BIGINT para evitar problemas de precisión. Un sueldo típico ronda los 3–15 millones de guaraníes.
La columna diferencia_monto es calculada automáticamente (columna generada). Te va a servir luego para detectar funcionarios con presupuesto no ejecutado.
Crear esquemas raw y staging en DBeaver
Crear la tabla raw.nomina_raw con el DDL
Crear la tabla staging.nomina con tipos correctos y columna generada
Ejecutar el INSERT RAW → STAGING y verificar conteos por mes

3 Validación de calidad con Python
Python 3.12 + pandas + psycopg2
Conectarse a PostgreSQL, leer el staging y validar: nulos por columna, funcionarios duplicados en el mismo mes, consistencia de montos (devengado vs presupuestado), variación entre meses (¿aparece alguien en enero que no está en marzo?), y distribución por sexo, entidad y concepto de gasto.

# scripts/python/02_validar_calidad_nomina.py
import
 pandas 
as
 pd
import
 psycopg2
from
 dotenv 
import
 load_dotenv
import
 os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DBNAME"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

df = pd.read_sql("SELECT * FROM staging.nomina", conn)
conn.close()

print(f"Total registros cargados: {len(df):,}")
print(f"Registros por mes:\n{df.groupby('mes')['id'].count()}")
print()

# 1. Nulos por columna
print("=== NULOS POR COLUMNA ===")
nulls = df.isnull().sum()
print(nulls[nulls > 0])

# 2. Duplicados: mismo funcionario + mismo mes + mismo concepto de gasto
dups = df.duplicated(
    subset=['codigo_persona','mes','codigo_objeto_gasto','linea']
).sum()
print(f"\nDuplicados exactos: {dups:,}")

# 3. Funcionarios que aparecen en los 3 meses vs solo algunos
por_persona = df.groupby('codigo_persona')['mes'].nunique()
print(f"\nFuncionarios en 1 mes: {(por_persona==1).sum():,}")
print(f"Funcionarios en 2 meses: {(por_persona==2).sum():,}")
print(f"Funcionarios en 3 meses: {(por_persona==3).sum():,}")

# 4. Montos: casos donde devengado > presupuestado
excedidos = df[df['monto_devengado'] > df['monto_presupuestado']]
print(f"\nRegistros con devengado > presupuestado: {len(excedidos):,}")

# 5. Distribución por sexo
print("\n=== DISTRIBUCIÓN POR SEXO ===")
print(df.groupby(['mes','sexo'])['codigo_persona'].nunique().unstack())

# 6. Top 10 conceptos de gasto por monto devengado total
print("\n=== TOP CONCEPTOS DE GASTO ===")
top = df.groupby('concepto_gasto')['monto_devengado'].sum().sort_values(ascending=False).head(10)
print(top)

# 7. Variación de masa salarial entre meses
print("\n=== MASA SALARIAL POR MES (en millones de Gs.) ===")
masa = df.groupby('mes')['monto_devengado'].sum() / 1_000_000
print(masa.round(0))

Es normal encontrar un mismo codigoPersona con múltiples registros en el mismo mes — cada fila es un concepto de gasto diferente (sueldo, bonificación, subsidio de salud, etc.). No son duplicados; son ítems de la planilla de ese funcionario.
Crear el script 02_validar_calidad_nomina.py
Ejecutar y anotar la cantidad de registros por mes
Verificar si hay funcionarios que entraron o salieron entre enero y marzo
Documentar los conceptos de gasto más frecuentes


4 Data Mart analítico en DuckDB
DuckDB + SQL OLAP
Crear 3 marts analíticos conectando DuckDB a PostgreSQL staging: uno con masa salarial por entidad y mes, otro con perfil demográfico del personal, y un tercero con evolución mensual de conceptos de gasto.

duckdb /opt/repo/proyecto-bigdata/data/duckdb/bigdata_lab.duckdb

-- Instalar extensión Postgres y conectar
INSTALL
 postgres;
LOAD
 postgres;

ATTACH
 'host=localhost port=5432 dbname=bigdata_lab user=postgres password=postgres'
    
AS
 pg (TYPE POSTGRES);

-- MART 1: masa salarial por entidad y mes
CREATE OR REPLACE TABLE
 mart_masa_salarial 
AS

SELECT

    anio,
    mes,
    descripcion_entidad,
    descripcion_unidad,
    COUNT(DISTINCT codigo_persona)          
AS
 total_funcionarios,
    SUM(monto_devengado)                    
AS
 total_devengado,
    SUM(monto_presupuestado)                
AS
 total_presupuestado,
    SUM(monto_presupuestado - monto_devengado) 
AS
 saldo_sin_ejecutar,
    ROUND(AVG(monto_devengado), 0)         
AS
 promedio_por_registro
FROM
 pg.staging.nomina
GROUP BY
 anio, mes, descripcion_entidad, descripcion_unidad;

-- MART 2: perfil demográfico del personal
CREATE OR REPLACE TABLE
 mart_perfil_personal 
AS

SELECT

    mes,
    descripcion_entidad,
    sexo,
    discapacidad,
    tipo_personal,
    COUNT(DISTINCT codigo_persona)         
AS
 cantidad_funcionarios,
    ROUND(AVG(
        DATE_DIFF('year', fecha_ingreso, CURRENT_DATE)
    ), 1)                                  
AS
 antiguedad_promedio_anios,
    SUM(monto_devengado)                   
AS
 total_devengado
FROM
 pg.staging.nomina
WHERE
 fecha_ingreso IS NOT NULL
GROUP BY
 mes, descripcion_entidad, sexo, discapacidad, tipo_personal;

-- MART 3: evolución mensual por concepto de gasto
CREATE OR REPLACE TABLE
 mart_conceptos_gasto 
AS

SELECT

    mes,
    concepto_gasto,
    fuente_financiamiento,
    COUNT(*)                               
AS
 cantidad_registros,
    COUNT(DISTINCT codigo_persona)         
AS
 funcionarios_afectados,
    SUM(monto_devengado)                   
AS
 total_devengado,
    ROUND(AVG(monto_devengado), 0)         
AS
 promedio_devengado
FROM
 pg.staging.nomina
GROUP BY
 mes, concepto_gasto, fuente_financiamiento
ORDER BY
 mes, total_devengado 
DESC
;

-- Query de ejemplo: evolución de la masa salarial mes a mes
SELECT
 mes,
       SUM(total_devengado) / 1000000 
AS
 masa_salarial_millones_gs
FROM
 mart_masa_salarial
GROUP BY
 mes
ORDER BY
 mes;

El MART 2 (mart_perfil_personal) te va a permitir analizar la brecha de género y la distribución de personas con discapacidad en el plantel — datos sensibles pero públicos en la nómina oficial.
Crear el archivo DuckDB en data/duckdb/bigdata_lab.duckdb
Conectar DuckDB a PostgreSQL con la extensión postgres
Crear los 3 marts: mart_masa_salarial, mart_perfil_personal, mart_conceptos_gasto
Ejecutar la query de evolución mensual y anotar los resultados

5 Orquestar todo con Airflow
Apache Airflow 3.1.8
Crear un DAG que ejecute el pipeline completo: Pentaho ETL (3 CSVs) → SQL staging → Python calidad → DuckDB marts. El dataset cubre enero–marzo 2026 (estático), así que el schedule es @once o manual.

cd /opt/repo/proyecto-bigdata
source venv/bin/activate
export AIRFLOW_HOME=/opt/repo/proyecto-bigdata/orchestration/airflow

# Iniciar servicio limpio
airflow standalone
# orchestration/airflow/dags/dag_nomina_pipeline.py
from
 airflow.sdk 
import
 dag, task
from
 datetime 
import
 datetime
import
 subprocess

@dag(
    dag_id='pipeline_nomina_funcionarios',
    start_date=datetime(2026, 1, 1),
    schedule='@once',          # dataset estático ene-mar 2026
    catchup=False,
    tags=['nomina', 'funcionarios', 'bigdata']
)
def
 pipeline_nomina():

    @task()
    
def
 ejecutar_pentaho_etl():
        """Lee los 3 CSVs de nómina y carga raw.nomina_raw en PostgreSQL"""
        subprocess.run([
            "/opt/pentaho/data-integration/pan.sh",
            "-file=/opt/repo/proyecto-bigdata/etl/pentaho/transformations/01_carga_nomina_raw.ktr"
        ], check=True)
        print("ETL Pentaho completado — 3 meses cargados")

    @task()
    
def
 staging_postgresql():
        """Ejecuta el INSERT RAW → STAGING con tipado y limpieza"""
        subprocess.run([
            "psql", "-h", "localhost", "-U", "postgres",
            "-d", "bigdata_lab",
            "-f", "/opt/repo/proyecto-bigdata/database/postgresql/ddl/nomina_staging.sql"
        ], check=True)

    @task()
    
def
 validar_calidad():
        """Valida nulos, duplicados y variación mensual de la nómina"""
        subprocess.run([
            "python",
            "/opt/repo/proyecto-bigdata/scripts/python/02_validar_calidad_nomina.py"
        ], check=True)

    @task()
    
def
 actualizar_duckdb_marts():
        """Crea/actualiza los 3 marts analíticos en DuckDB"""
        subprocess.run([
            "duckdb",
            "/opt/repo/proyecto-bigdata/data/duckdb/bigdata_lab.duckdb",
            "-f",
            "/opt/repo/proyecto-bigdata/database/duckdb/marts/crear_marts_nomina.sql"
        ], check=True)

    # Orden del pipeline
    etl   = ejecutar_pentaho_etl()
    stg   = staging_postgresql()
    cal   = validar_calidad()
    marts = actualizar_duckdb_marts()

    etl >> stg >> cal >> marts

pipeline_nomina()

Como el dataset cubre ene–mar 2026, usá schedule='@once'. Si en el futuro se agregan más meses de nómina, cambiás a schedule='@monthly' y el pipeline procesa el CSV del mes nuevo automáticamente.
Crear el archivo DAG en orchestration/airflow/dags/
Levantar Airflow con airflow standalone y abrir el UI en localhost:8080
Verificar que el DAG aparece sin errores de sintaxis
Hacer trigger manual y monitorear cada tarea en verde

6 Subir el repositorio a GitHub
Git · GitHub · WSL2
Crear el repositorio proyecto-bigdata en GitHub, inicializar Git en el directorio local y hacer el primer push. El dataset no se sube (está en Drive), así que se ignora con .gitignore.

# 1. Crear el repositorio en GitHub (sin README, sin .gitignore)
#    → github.com → New repository → nombre: proyecto-bigdata → Create

# 2. Inicializar Git en el proyecto local
cd /opt/repo/proyecto-bigdata
git init
git branch -M main

# 3. Crear .gitignore para no subir el dataset pesado
cat > .gitignore << 'EOF'
data/raw/
data/duckdb/
*.csv
*.duckdb
__pycache__/
.env
*.log
EOF

# 4. Crear README.md
cat > README.md << 'EOF'
# Proyecto Big Data — Nómina de Funcionarios Públicos PY

Pipeline de datos end-to-end sobre nómina del Ministerio de Defensa Nacional.
Período: enero–marzo 2026.

## Stack
- **ETL**: Pentaho PDI
- **Staging**: PostgreSQL 15
- **Calidad**: Python 3.12
- **OLAP**: DuckDB
- **Orquestación**: Apache Airflow 3.1.8
- **Dashboard**: Metabase

## Dataset
Nómina pública disponible en Google Drive (3 archivos mensuales).
EOF

# 5. Primer commit y push

git add .
git commit -m "feat: estructura inicial del pipeline nómina funcionarios"
git remote add origin https://github.com/<tu-usuario>/proyecto-bigdata.git
git push -u origin main

No subas el dataset — contiene nombres y documentos de funcionarios. El .gitignore ya excluye data/raw/ y *.csv. Podés mencionar que los datos son de acceso público oficial en el README.
Hacé commits al cerrar cada step: git commit -m "step 2: staging PostgreSQL listo". Así el historial de Git refleja el avance real del proyecto y sirve como documentación del proceso.
Crear el repositorio proyecto-bigdata en GitHub
Inicializar Git y crear el .gitignore con exclusión del dataset
Crear el README.md con descripción del proyecto
Hacer el primer git push y verificar en github.com
Hacer commits al finalizar cada step del pipeline

7 Dashboard en Metabase
Metabase → DuckDB
Conectar Metabase al archivo DuckDB y crear visualizaciones sobre los 3 marts: evolución de la masa salarial mensual, distribución de funcionarios por entidad, brecha de género y ranking de conceptos de gasto.

# Instalar Metabase (jar) en WSL2:
mkdir -p /opt/metabase
cd /opt/metabase
curl -L https://downloads.metabase.com/latest/metabase.jar \
     -o metabase.jar
java -jar metabase.jar

# Abrir en navegador: http://localhost:3000
# Conectar a DuckDB:
# Settings → Databases → Add database
# Driver: DuckDB | Path: /opt/repo/proyecto-bigdata/data/duckdb/bigdata_lab.duckdb

# Visualizaciones a crear sobre mart_masa_salarial:
# 1. Línea: Evolución de masa salarial total (enero → marzo)
# 2. Barra: Top 10 unidades por monto devengado (mes de marzo)
# 3. Número: Total devengado acumulado enero-marzo
# 4. Tabla: Saldo sin ejecutar por unidad (presupuestado - devengado)

# Sobre mart_perfil_personal:
# 5. Donut: Distribución M/F por entidad
# 6. Barra apilada: Antigüedad promedio por unidad responsable

# Sobre mart_conceptos_gasto:
# 7. Barra horizontal: Top 10 conceptos de gasto por monto total
# 8. Línea: Evolución mensual de SUELDOS vs BONIFICACIONES

Para el gráfico de línea de masa salarial, usá mart_masa_salarial agrupado por mes sumando total_devengado. Metabase lo reconoce como serie temporal si el eje X es numérico o fecha.
Instalar y levantar Metabase
Conectar Metabase al archivo DuckDB
Crear el gráfico de evolución de masa salarial mensual
Crear las visualizaciones de perfil demográfico y conceptos de gasto
Guardar screenshot del dashboard en reports/
