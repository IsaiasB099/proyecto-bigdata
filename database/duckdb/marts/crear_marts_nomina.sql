-- Instalar y cargar extensión de Postgres en DuckDB por si se requiere conectar directo
INSTALL postgres;
LOAD postgres;

-- Conectar a Postgres de manera local
--ATTACH 'dbname=proyecto_bigdata user=postgres password=bigdata123 host=localhost' AS pg_db (TYPE postgres);
ATTACH
 'host=localhost port=5432 dbname=bigdata_lab user=postgres password=bigdata123'
AS
 pg (TYPE POSTGRES);

-- Crear esquemas analíticos locales en DuckDB
CREATE SCHEMA IF NOT EXISTS marts;

-- Mart 1: Resumen de salarios por Mes y Año
CREATE OR REPLACE TABLE marts.resumen_mensual AS 
SELECT anio, mes, COUNT(*) as total_empleados, SUM(salario_bruto) as masa_salarial
FROM pg_db.staging.nomina_funcionarios
GROUP BY anio, mes;

-- Mostrar resultado en consola
SELECT * FROM marts.resumen_mensual;
