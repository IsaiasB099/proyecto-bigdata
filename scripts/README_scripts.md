## 02_validar_calidad_nomina.py — Un script Python que lee staging.nomina y verifica que los datos sean confiables antes de analizar.
## El script 02_validar_calidad_nomina.py se conecta a PostgreSQL con psycopg2, carga todo en un DataFrame de pandas y hace 7 validaciones:

## Cuenta registros totales y por mes
## Detecta nulos por columna

## Busca duplicados exactos (mismo funcionario, mismo mes, mismo concepto de gasto, misma línea)

## Analiza funcionarios que aparecen en 1, 2 o los 3 meses (para detectar altas y bajas)

## Detecta casos donde el devengado supera al presupuestado (anomalía financiera)

## Muestra distribución por sexo por mes

## Lista los 10 conceptos de gasto con mayor monto total



## ver_duckdb.py — script de exploración/diagnóstico: qué tablas lista, para qué sirve

## Cómo ejecutar — python scripts/python/nombre.py, dependencias, variables de entorno (.env)

## Nota — el archivo bigdata_lab.duckdb dentro de scripts/ parece un artefacto — considerar moverlo a data/duckdb/