## Herramienta — Pentaho Data Integration (PDI), también conocido por su nombre original Kettle, es una poderosa herramienta de software libre (open source) utilizada para realizar procesos ETL (Extracción, Transformación y Carga).

## Transformación: 01_carga_nomina_raw.ktr —    Get File Names + CSV File Input → lee los 3 CSV de forma automática                             Select Values → elige solo las columnas que importan (no las 41, sino las relevantes)                                  Filter Rows → descarta filas con codigoPersona nulo o montos negativos (datos corruptos)    String operations → limpia espacios en blanco en nombres, cargos, etc.                         Table Output → escribe todo en la tabla raw.nomina_raw de PostgreSQL                         Se guarda la transformation como 01_carga_nomina_raw.ktr

## Cómo ejecutar manualmente — comando pan.sh o desde Spoon (GUI), variables de entorno necesarias

## Cómo ejecutar desde Airflow — referencia al DAG que lo orquesta, task ejecutar_pentaho_etl