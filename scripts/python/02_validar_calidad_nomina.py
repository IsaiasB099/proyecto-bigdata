import os
import glob
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Configuración de rutas locales
DATA_DIR = "/opt/repo/proyecto-bigdata/data/raw/nomina"
ENV_PATH = "/opt/repo/proyecto-bigdata/.env"

print("=== CARGANDO ARCHIVOS CSV LOCALES ===")

# Buscar solo archivos reales .csv (ignorando los :Zone.Identifier)
csv_files = glob.glob(os.path.join(DATA_DIR, "nomina_2026-*.csv"))
csv_files = [f for f in csv_files if not f.endswith(":Zone.Identifier")]

if not csv_files:
    print(f"Error: No se encontraron archivos CSV en la ruta: {DATA_DIR}")
    exit(1)

# Leer y concatenar todos los archivos CSV en un solo DataFrame
lista_df = []
for file in sorted(csv_files):
    print(f"Leyendo: {os.path.basename(file)}")
    try:
        # Se añade encoding='utf-8' o 'latin1' según corresponda a tus datos
        temp_df = pd.read_csv(file, encoding='latin1', low_memory=False)
        lista_df.append(temp_df)
    except Exception as e:
        print(f"Error al leer {os.path.basename(file)}: {e}")

if not lista_df:
    print("Error: No se pudo procesar ningún archivo CSV.")
    exit(1)

# DataFrame consolidado con los 3 meses
df = pd.concat(lista_df, ignore_index=True)

total_registros = len(df)
print(f"\nTotal registros cargados en memoria: {total_registros:,}")

print("\n=== COLUMNAS DETECTADAS EN EL CSV ===")
print(list(df.columns))
exit(0)  # Detiene el script temporalmente para que puedas ver la lista


if total_registros == 0:
    print("⚠️ ADVERTENCIA: Los archivos CSV están vacíos.")
    exit(0)

# =====================================================================
# PROCESAMIENTO Y VALIDACIONES DE CALIDAD DE DATOS
# =====================================================================

# Asegurar tipos de datos numéricos para evitar fallas de cálculo
df['monto_devengado'] = pd.to_numeric(df['monto_devengado'], errors='coerce')
df['monto_presupuestado'] = pd.to_numeric(df['monto_presupuestado'], errors='coerce')

# Verificar si la columna 'mes' existe, si no, crearla desde el nombre del archivo si fuera necesario
if 'mes' not in df.columns:
    print("⚠️ La columna 'mes' no existe en los CSV. Intenta validando tus columnas.")
else:
    print(f"Registros por mes:\n{df.groupby('mes')['id'].count() if 'id' in df.columns else df.groupby('mes').size()}")
print()

# 1. Nulos por columna
print("=== NULOS POR COLUMNA ===")
nulls = df.isnull().sum()
print(nulls[nulls > 0].sort_values(ascending=False))

# 2. Duplicados: mismo funcionario + mismo mes + mismo concepto de gasto
subset_cols = ['codigo_persona', 'mes', 'codigo_objeto_gasto', 'linea']
existing_cols = [c for c in subset_cols if c in df.columns]
if len(existing_cols) == len(subset_cols):
    dups = df.duplicated(subset=subset_cols).sum()
    print(f"\nDuplicados exactos (Persona-Mes-Objeto-Línea): {dups:,}")
else:
    print("\n⚠️ No se pudo calcular duplicados. Faltan algunas columnas clave.")

# 3. Funcionarios que aparecen en los 3 meses vs solo algunos
if 'codigo_persona' in df.columns and 'mes' in df.columns:
    por_persona = df.groupby('codigo_persona')['mes'].nunique()
    print(f"\nFuncionarios en 1 mes: {(por_persona==1).sum():,}")
    print(f"Funcionarios en 2 meses: {(por_persona==2).sum():,}")
    print(f"Funcionarios en 3 meses: {(por_persona==3).sum():,}")

# 4. Montos: casos donde devengado > presupuestado
if 'monto_devengado' in df.columns and 'monto_presupuestado' in df.columns:
    excedidos = df[df['monto_devengado'] > df['monto_presupuestado']]
    print(f"\nRegistros con devengado > presupuestado: {len(excedidos):,}")

# 5. Distribución por sexo
if 'mes' in df.columns and 'sexo' in df.columns and 'codigo_persona' in df.columns:
    print("\n=== DISTRIBUCIÓN POR SEXO ===")
    print(df.groupby(['mes', 'sexo'])['codigo_persona'].nunique().unstack())

# 6. Top 10 conceptos de gasto por monto devengado total
if 'concepto_gasto' in df.columns and 'monto_devengado' in df.columns:
    print("\n=== TOP CONCEPTOS DE GASTO ===")
    top = df.groupby('concepto_gasto')['monto_devengado'].sum().sort_values(ascending=False).head(10)
    print(top)

# 7. Variación de masa salarial entre meses
if 'mes' in df.columns and 'monto_devengado' in df.columns:
    print("\n=== MASA SALARIAL POR MES (en millones de Gs.) ===")
    masa = df.groupby('mes')['monto_devengado'].sum() / 1_000_000
    print(masa.round(0))

# =====================================================================
# OPCIONAL: GUARDAR EN LA BASE DE DATOS POSTGRESQL (INGESTA)
# =====================================================================
load_dotenv(dotenv_path=ENV_PATH)
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
dbname = os.getenv("POSTGRES_DBNAME")

if all([user, password, host, port, dbname]):
    try:
        print("\n=== GUARDANDO DATOS EN POSTGRESQL ===")
        engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
        
        # Guarda todo el dataframe consolidado en la tabla staging.nomina
        # if_exists='replace' recreará la tabla con los nuevos datos de los CSV
        df.to_sql("nomina", engine, schema="staging", if_exists="replace", index=False)
        print("¡Datos exportados con éxito a staging.nomina en la base de datos!")
    except Exception as e:
        print(f"\n⚠️ No se pudo guardar en la BD (pero las validaciones locales terminaron): {e}")
else:
    print("\n💡 Nota: No se detectaron credenciales en el .env. Los datos no se guardaron en la BD.")

