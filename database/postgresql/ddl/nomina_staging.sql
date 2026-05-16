-- Crear el esquema staging si no existe
CREATE SCHEMA IF NOT EXISTS staging;

-- Recrear la tabla destino estructurada
DROP TABLE IF EXISTS staging.nomina_funcionarios CASCADE;
CREATE TABLE staging.nomina_funcionarios (
    id SERIAL PRIMARY KEY,
    anio INT,
    mes INT,
    documento VARCHAR(50),
    nombre VARCHAR(255),
    apellido VARCHAR(255),
    salario_bruto NUMERIC(15,2),
    fecha_proceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cargar y transformar los datos desde el esquema raw que llenó Pentaho
-- Nota: Adaptamos la query asumiendo columnas estándar de la carga masiva
INSERT INTO staging.nomina_funcionarios (anio, mes, documento, nombre, apellido, salario_bruto)
SELECT 
    CAST(anio AS INT),
    CAST(mes AS INT),
    REGEXP_REPLACE(documento, '[^0-9]', '', 'g'), -- Remueve puntos o guiones
    UPPER(TRIM(nombre)),
    UPPER(TRIM(apellido)),
    CAST(COALESCE(NULLIF(salario, ''), '0') AS NUMERIC(15,2))
FROM raw.nomina_raw;

ANALYZE staging.nomina_funcionarios;
