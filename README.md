El proyecto es un pipeline de datos completo sobre la nómina de funcionarios públicos del Ministerio de Defensa Nacional de Paraguay (enero–marzo 2026). Atraviesa todo el stack del curso: desde los CSV crudos hasta un dashboard visual.

Paso 0 — Preparar el dataset
¿Qué hace? Es la base de todo. Antes de correr cualquier herramienta, necesitás tener los datos en tu máquina.
El dataset son 3 archivos CSV mensuales con 41 columnas cada uno. Las columnas más importantes son codigoPersona (ID único del funcionario), conceptoGasto (tipo de pago: sueldo, bono, subsidio) y montoDevengado (lo que realmente se pagó en guaraníes).
Los comandos que ejecutás en WSL2 crean la estructura de carpetas del proyecto y luego copian los CSV a data/raw/nomina/. Finalmente wc -l cuenta cuántas filas tiene cada archivo y head -1 muestra las columnas para entender qué hay.
Punto clave: Los 3 archivos no se unen todavía — Pentaho los procesará uno por uno y los unifica en la base de datos usando el campo mes para distinguirlos.

Paso 1 — ETL con Pentaho PDI
¿Qué hace? Leer los 3 CSV, limpiarlos y cargarlos en PostgreSQL.
Abrís Spoon (la interfaz gráfica de Pentaho) y creás una Transformation visual con estos bloques encadenados:

Get File Names + CSV File Input → lee los 3 CSV de forma automática
Select Values → elige solo las columnas que importan (no las 41, sino las relevantes)
Filter Rows → descarta filas con codigoPersona nulo o montos negativos (datos corruptos)
String operations → limpia espacios en blanco en nombres, cargos, etc.
Table Output → escribe todo en la tabla raw.nomina_raw de PostgreSQL

Guardás la transformation como 01_carga_nomina_raw.ktr.
Punto clave: El CSV usa comillas dobles especiales para campos con comas adentro — hay que configurar bien el "Enclosure character" en Spoon o los datos quedan mal leídos.

Paso 2 — Modelado y Staging en PostgreSQL
¿Qué hace? Crear las tablas en la base de datos y pasar los datos de "brutos" a "limpios y tipados".
Se crean dos esquemas en PostgreSQL (ejecutando DDL en DBeaver):

raw.nomina_raw → espejo exacto del CSV, todo guardado como TEXT (sin conversión de tipos)
staging.nomina → versión limpia: los montos como BIGINT, las fechas como DATE, los nombres en formato Title Case, etc.

El INSERT que pasa de RAW a STAGING aplica funciones de limpieza sobre cada columna: TRIM() para espacios, INITCAP() para capitalizar nombres, ::BIGINT para convertir montos. También tiene una columna calculada automáticamente: diferencia_monto = presupuestado - devengado, útil para detectar presupuesto no ejecutado.
Punto clave: Los montos están en guaraníes enteros (sin decimales), por eso se usa BIGINT y no NUMERIC. Un sueldo típico ronda los 3 a 15 millones de guaraníes.

Paso 3 — Validación de calidad con Python
¿Qué hace? Un script Python que lee staging.nomina y verifica que los datos sean confiables antes de analizar.
El script 02_validar_calidad_nomina.py se conecta a PostgreSQL con psycopg2, carga todo en un DataFrame de pandas y hace 7 validaciones:

Cuenta registros totales y por mes
Detecta nulos por columna
Busca duplicados exactos (mismo funcionario, mismo mes, mismo concepto de gasto, misma línea)
Analiza funcionarios que aparecen en 1, 2 o los 3 meses (para detectar altas y bajas)
Detecta casos donde el devengado supera al presupuestado (anomalía financiera)
Muestra distribución por sexo por mes
Lista los 10 conceptos de gasto con mayor monto total

Punto clave: Un mismo codigoPersona puede tener varias filas en el mismo mes — una por cada concepto de gasto (sueldo, bonificación, subsidio de salud, etc.). Eso es normal, no son duplicados.

Paso 4 — Data Marts analíticos en DuckDB
¿Qué hace? Crear 3 tablas analíticas (marts) en DuckDB, conectado directamente a PostgreSQL.
DuckDB se conecta al staging de PostgreSQL usando la extensión postgres y crea 3 marts:

mart_masa_salarial → masa salarial por entidad, unidad y mes (total devengado, presupuestado, saldo sin ejecutar, promedio por registro)
mart_perfil_personal → perfil demográfico: cantidad de funcionarios por sexo, discapacidad, tipo de personal y antigüedad promedio
mart_conceptos_gasto → evolución mensual de cada concepto de gasto (sueldos, bonos, subsidios) con totales y promedios

Estos marts son las tablas que luego va a leer Metabase para los gráficos.

Paso 5 — Orquestar todo con Airflow
¿Qué hace? Un DAG de Airflow que ejecuta todo el pipeline anterior en orden y de forma automática.
El DAG pipeline_nomina_funcionarios define 4 tareas encadenadas con el operador >>:
ETL Pentaho → Staging PostgreSQL → Validación Python → Marts DuckDB
Como el dataset es estático (solo 3 meses fijos), el schedule es @once — se ejecuta una sola vez al hacer trigger manual. Si en el futuro se agregan más meses, basta cambiar a @monthly.
Para probarlo: levantás Airflow con airflow standalone, abrís localhost:8080, verificás que el DAG aparece sin errores y hacés trigger manual.

Paso 6 — Subir el repositorio a GitHub
¿Qué hace? Versionar el código del proyecto (sin los datos) en GitHub.
Los pasos son: crear el repo en GitHub, inicializar Git en /opt/repo/proyecto-bigdata, crear un .gitignore que excluye data/raw/, *.csv y *.duckdb (porque los datos son pesados y tienen nombres de personas), crear el README.md con descripción del proyecto y hacer el primer push.
Punto clave: Hacé un commit al terminar cada paso (git commit -m "step 2: staging PostgreSQL listo"). Así el historial refleja el avance real del proyecto.

Paso 7 — Dashboard en Metabase
¿Qué hace? Visualizar los marts de DuckDB en gráficos interactivos.
Instalás Metabase (un .jar de Java) en WSL2, lo levantás y lo conectás al archivo .duckdb. Luego creás 8 visualizaciones:

Sobre masa salarial: línea de evolución mensual, top 10 unidades, total acumulado, saldo sin ejecutar
Sobre perfil del personal: gráfico donut M/F por entidad, antigüedad promedio por unidad
Sobre conceptos de gasto: ranking horizontal de los 10 conceptos con más monto, línea de evolución de sueldos vs bonificaciones

Al terminar, guardás un screenshot del dashboard en reports/.

Flujo completo resumido
CSVs Drive → Pentaho ETL → raw.nomina_raw (PostgreSQL)
                               ↓
                      staging.nomina (PostgreSQL, tipado)
                               ↓
                    Script Python (validación de calidad)
                               ↓
                    DuckDB Marts (análisis OLAP)
                               ↓
                    Metabase (dashboard visual)
                               ↓
                    Airflow DAG (orquesta todo)
                    GitHub (versiona el código)
