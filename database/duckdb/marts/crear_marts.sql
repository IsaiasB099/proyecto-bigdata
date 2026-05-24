--duckdb /opt/repo/proyecto-bigdata/data/duckdb/bigdata_lab.duckdb

-- Instalar extensión Postgres y conectar
INSTALL
 postgres;
LOAD
 postgres;

ATTACH
 'host=localhost port=5432 dbname=proyecto_bigdata user=bigdata_user password=bigdata123'
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
