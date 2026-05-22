
## PostgreSQL — Modelado y Staging 
Se crean dos esquemas en PostgreSQL(ejecutando DDL en DBeaver): raw.nomina_raw → espejo exacto del CSV, todo guardado como TEXT (sin conversión de tipos)staging.nomina → versión limpia: los montos como BIGINT, las fechas como DATE, los nombres en formato Title Case, etc.

El INSERT que pasa de RAW a STAGING aplica funciones de limpieza sobre cada columna: TRIM() para espacios, INITCAP() para capitalizar nombres, ::BIGINT para convertir montos. También tiene una columna calculada automáticamente: diferencia_monto = presupuestado - devengado, útil para detectar presupuesto no ejecutado.

## DuckDB — Data Marts 
DuckDB se conecta al staging de PostgreSQL usando la extensión postgres y crea 3 marts: mart_masa_salarial → masa salarial por entidad, unidad y mes (total devengado, presupuestado, saldo sin ejecutar, promedio por registro) mart_perfil_personal → perfil demográfico: cantidad de funcionarios por sexo, discapacidad, tipo de personal y antigüedad promedio mart_conceptos_gasto → evolución mensual de cada concepto de gasto (sueldos, bonos, subsidios) con totales y promedios

## Cómo aplicar los scripts 
Primero se aplica, raw.nomina_raw para crear la tabla raw con todos los datos en formato TEXT, luego se aplica staging.nomina para tipar y limpiar los datos. Por ultimo  un script para pasar de RAW a STAGING ya con datos limpiados y tipados