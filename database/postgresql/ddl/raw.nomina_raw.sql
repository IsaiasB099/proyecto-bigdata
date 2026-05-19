-- Crear esquemas (ejecutar en DBeaver)
CREATE SCHEMA IF NOT EXISTS
 raw;

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
