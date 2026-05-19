-- Pasar de RAW a STAGING con limpieza y tipado
INSERT INTO
 staging.nomina (
    anio, mes, codigo_nivel, descripcion_nivel,
    codigo_entidad, descripcion_entidad,
    codigo_programa, descripcion_programa,
    codigo_unidad, descripcion_unidad,
    codigo_objeto_gasto, concepto_gasto, fuente_financiamiento, linea,
    codigo_persona, nombres, apellidos, sexo, discapacidad,
    codigo_categoria, cargo, fecha_ingreso, tipo_personal,
    monto_presupuestado, monto_devengado
)
SELECT

    anio::SMALLINT,
    mes::SMALLINT,
    codigonivel::SMALLINT,
    INITCAP(TRIM(descripcionnivel)),
    codigoentidad::SMALLINT,
    TRIM(descripcionentidad),
    codigoprograma::SMALLINT,
    TRIM(descripcionprograma),
    codigounidadresponsable::SMALLINT,
    TRIM(descripcionunidadresponsable),
    codigoobjetogasto::SMALLINT,
    TRIM(conceptogasto),
    TRIM(fuentefinanciamiento),
    linea::SMALLINT,
    codigopersona::BIGINT,
    INITCAP(TRIM(nombres)),
    INITCAP(TRIM(apellidos)),
    UPPER(TRIM(sexo)),
    UPPER(TRIM(discapacidad)),
    TRIM(codigocategoria),
    TRIM(cargo),
    NULLIF(TRIM(fechaingreso), '')::DATE,
    TRIM(tipopersonal),
    montoPresupuestado::BIGINT,
    montoDevengado::BIGINT
FROM
 raw.nomina_raw
WHERE
 codigoPersona IS NOT NULL
  
AND
 codigoPersona != ''
  
AND
 montoDevengado::BIGINT >= 0;