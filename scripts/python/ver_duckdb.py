import duckdb
# Conectar al archivo existente
con = duckdb.connect('/opt/repo/proyecto-bigdata/data/duckdb/bigdata_lab.duckdb')

# Lista de todas las tablas disponibles
tablas = ['mart_conceptos_gasto', 'mart_masa_salarial', 'mart_perfil_personal']

for tabla in tablas:
    # Obtiene el conteo total de filas de cada tabla
    conteo = con.sql(f"SELECT COUNT(*) FROM {tabla}").fetchall()[0][0]
    print(f"Tabla '{tabla}': {conteo} registros.")
