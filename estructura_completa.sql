                                                                                   Tabla «public.siniestros»
                Columna                |           Tipo           | Ordenamiento | Nulable  |              Por omisión               | Almacenamiento | Compresión | Estadísticas | Descripción 
---------------------------------------+--------------------------+--------------+----------+----------------------------------------+----------------+------------+--------------+-------------
 id                                    | integer                  |              | not null | nextval('siniestros_id_seq'::regclass) | plain          |            |              | 
 compania_seguros                      | character varying(255)   |              | not null |                                        | extended       |            |              | 
 ruc_compania                          | character varying(20)    |              |          |                                        | extended       |            |              | 
 tipo_reclamo                          | character varying(50)    |              |          |                                        | extended       |            |              | 
 poliza                                | character varying(50)    |              |          |                                        | extended       |            |              | 
 reclamo_num                           | character varying(100)   |              | not null |                                        | extended       |            |              | 
 fecha_siniestro                       | timestamp with time zone |              | not null |                                        | plain          |            |              | 
 direccion_siniestro                   | character varying(500)   |              | not null |                                        | extended       |            |              | 
 ubicacion_geo_lat                     | double precision         |              |          |                                        | plain          |            |              | 
 ubicacion_geo_lng                     | double precision         |              |          |                                        | plain          |            |              | 
 danos_terceros                        | boolean                  |              |          |                                        | plain          |            |              | 
 ejecutivo_cargo                       | character varying(255)   |              |          |                                        | extended       |            |              | 
 fecha_designacion                     | timestamp with time zone |              |          |                                        | plain          |            |              | 
 tipo_siniestro                        | character varying(100)   |              |          |                                        | extended       |            |              | 
 fecha_reportado                       | timestamp with time zone |              |          |                                        | plain          |            |              | 
 cobertura                             | character varying(100)   |              |          |                                        | extended       |            |              | 
 pdf_firmado_url                       | character varying(500)   |              |          |                                        | extended       |            |              | 
 fecha_declaracion                     | timestamp with time zone |              |          |                                        | plain          |            |              | 
 persona_declara_tipo                  | character varying(20)    |              |          |                                        | extended       |            |              | 
 persona_declara_cedula                | character varying(20)    |              |          |                                        | extended       |            |              | 
 persona_declara_nombre                | character varying(255)   |              |          |                                        | extended       |            |              | 
 persona_declara_relacion              | character varying(255)   |              |          |                                        | extended       |            |              | 
 misiva_investigacion                  | text                     |              |          |                                        | extended       |            |              | 
 evidencias_complementarias            | text                     |              |          |                                        | extended       |            |              | 
 evidencias_complementarias_imagen_url | character varying(500)   |              |          |                                        | extended       |            |              | 
 otras_diligencias                     | text                     |              |          |                                        | extended       |            |              | 
 otras_diligencias_imagen_url          | character varying(500)   |              |          |                                        | extended       |            |              | 
 visita_taller_descripcion             | text                     |              |          |                                        | extended       |            |              | 
 visita_taller_imagen_url              | character varying(500)   |              |          |                                        | extended       |            |              | 
 observaciones                         | text                     |              |          |                                        | extended       |            |              | 
 recomendacion_pago_cobertura          | text                     |              |          |                                        | extended       |            |              | 
 conclusiones                          | text                     |              |          |                                        | extended       |            |              | 
 anexo                                 | text                     |              |          |                                        | extended       |            |              | 
 created_at                            | timestamp with time zone |              |          | now()                                  | plain          |            |              | 
 updated_at                            | timestamp with time zone |              |          | now()                                  | plain          |            |              | 
Índices:
    "siniestros_pkey" PRIMARY KEY, btree (id)
    "ix_siniestros_id" btree (id)
    "siniestros_reclamo_num_key" UNIQUE CONSTRAINT, btree (reclamo_num)
Referenciada por:
    TABLE "antecedentes" CONSTRAINT "antecedentes_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "asegurados" CONSTRAINT "asegurados_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "beneficiarios" CONSTRAINT "beneficiarios_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "conductores" CONSTRAINT "conductores_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "dinamicas_accidente" CONSTRAINT "dinamicas_accidente_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "inspecciones" CONSTRAINT "inspecciones_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "objetos_asegurados" CONSTRAINT "objetos_asegurados_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "relatos_asegurado" CONSTRAINT "relatos_asegurado_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "relatos_conductor" CONSTRAINT "relatos_conductor_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "testigos" CONSTRAINT "testigos_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
    TABLE "visitas_taller" CONSTRAINT "visitas_taller_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                                         Tabla «public.asegurados»
       Columna       |          Tipo          | Ordenamiento | Nulable  |              Por omisión               | Almacenamiento | Compresión | Estadísticas | Descripción 
---------------------+------------------------+--------------+----------+----------------------------------------+----------------+------------+--------------+-------------
 id                  | integer                |              | not null | nextval('asegurados_id_seq'::regclass) | plain          |            |              | 
 siniestro_id        | integer                |              |          |                                        | plain          |            |              | 
 tipo                | character varying(50)  |              |          |                                        | extended       |            |              | 
 cedula              | character varying(20)  |              |          |                                        | extended       |            |              | 
 nombre              | character varying(255) |              |          |                                        | extended       |            |              | 
 celular             | character varying(20)  |              |          |                                        | extended       |            |              | 
 direccion           | character varying(500) |              |          |                                        | extended       |            |              | 
 parentesco          | character varying(100) |              |          |                                        | extended       |            |              | 
 correo              | character varying(255) |              |          |                                        | extended       |            |              | 
 ruc                 | character varying(20)  |              |          |                                        | extended       |            |              | 
 empresa             | character varying(255) |              |          |                                        | extended       |            |              | 
 representante_legal | character varying(255) |              |          |                                        | extended       |            |              | 
 telefono            | character varying(20)  |              |          |                                        | extended       |            |              | 
Índices:
    "asegurados_pkey" PRIMARY KEY, btree (id)
    "asegurados_siniestro_id_key" UNIQUE CONSTRAINT, btree (siniestro_id)
    "ix_asegurados_id" btree (id)
Restricciones de llave foránea:
    "asegurados_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                                      Tabla «public.beneficiarios»
   Columna    |          Tipo          | Ordenamiento | Nulable  |                Por omisión                | Almacenamiento | Compresión | Estadísticas | Descripción 
--------------+------------------------+--------------+----------+-------------------------------------------+----------------+------------+--------------+-------------
 id           | integer                |              | not null | nextval('beneficiarios_id_seq'::regclass) | plain          |            |              | 
 siniestro_id | integer                |              |          |                                           | plain          |            |              | 
 razon_social | character varying(255) |              |          |                                           | extended       |            |              | 
 cedula_ruc   | character varying(20)  |              |          |                                           | extended       |            |              | 
 domicilio    | character varying(500) |              |          |                                           | extended       |            |              | 
Índices:
    "beneficiarios_pkey" PRIMARY KEY, btree (id)
    "beneficiarios_siniestro_id_key" UNIQUE CONSTRAINT, btree (siniestro_id)
    "ix_beneficiarios_id" btree (id)
Restricciones de llave foránea:
    "beneficiarios_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                                      Tabla «public.conductores»
   Columna    |          Tipo          | Ordenamiento | Nulable  |               Por omisión               | Almacenamiento | Compresión | Estadísticas | Descripción 
--------------+------------------------+--------------+----------+-----------------------------------------+----------------+------------+--------------+-------------
 id           | integer                |              | not null | nextval('conductores_id_seq'::regclass) | plain          |            |              | 
 siniestro_id | integer                |              |          |                                         | plain          |            |              | 
 nombre       | character varying(255) |              | not null |                                         | extended       |            |              | 
 cedula       | character varying(20)  |              | not null |                                         | extended       |            |              | 
 celular      | character varying(20)  |              |          |                                         | extended       |            |              | 
 direccion    | character varying(500) |              |          |                                         | extended       |            |              | 
 parentesco   | character varying(100) |              |          |                                         | extended       |            |              | 
Índices:
    "conductores_pkey" PRIMARY KEY, btree (id)
    "conductores_siniestro_id_key" UNIQUE CONSTRAINT, btree (siniestro_id)
    "ix_conductores_id" btree (id)
Restricciones de llave foránea:
    "conductores_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                                      Tabla «public.objetos_asegurados»
   Columna    |          Tipo          | Ordenamiento | Nulable  |                  Por omisión                   | Almacenamiento | Compresión | Estadísticas | Descripción 
--------------+------------------------+--------------+----------+------------------------------------------------+----------------+------------+--------------+-------------
 id           | integer                |              | not null | nextval('objetos_asegurados_id_seq'::regclass) | plain          |            |              | 
 siniestro_id | integer                |              |          |                                                | plain          |            |              | 
 placa        | character varying(20)  |              | not null |                                                | extended       |            |              | 
 marca        | character varying(100) |              |          |                                                | extended       |            |              | 
 modelo       | character varying(100) |              |          |                                                | extended       |            |              | 
 tipo         | character varying(50)  |              |          |                                                | extended       |            |              | 
 color        | character varying(50)  |              |          |                                                | extended       |            |              | 
 ano          | integer                |              |          |                                                | plain          |            |              | 
 serie_motor  | character varying(100) |              |          |                                                | extended       |            |              | 
 chasis       | character varying(100) |              |          |                                                | extended       |            |              | 
Índices:
    "objetos_asegurados_pkey" PRIMARY KEY, btree (id)
    "ix_objetos_asegurados_id" btree (id)
    "objetos_asegurados_siniestro_id_key" UNIQUE CONSTRAINT, btree (siniestro_id)
Restricciones de llave foránea:
    "objetos_asegurados_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                              Tabla «public.antecedentes»
   Columna    |  Tipo   | Ordenamiento | Nulable  |               Por omisión                | Almacenamiento | Compresión | Estadísticas | Descripción 
--------------+---------+--------------+----------+------------------------------------------+----------------+------------+--------------+-------------
 id           | integer |              | not null | nextval('antecedentes_id_seq'::regclass) | plain          |            |              | 
 siniestro_id | integer |              |          |                                          | plain          |            |              | 
 descripcion  | text    |              | not null |                                          | extended       |            |              | 
Índices:
    "antecedentes_pkey" PRIMARY KEY, btree (id)
    "ix_antecedentes_id" btree (id)
Restricciones de llave foránea:
    "antecedentes_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                                      Tabla «public.relatos_asegurado»
    Columna    |          Tipo          | Ordenamiento | Nulable  |                  Por omisión                  | Almacenamiento | Compresión | Estadísticas | Descripción 
---------------+------------------------+--------------+----------+-----------------------------------------------+----------------+------------+--------------+-------------
 id            | integer                |              | not null | nextval('relatos_asegurado_id_seq'::regclass) | plain          |            |              | 
 siniestro_id  | integer                |              |          |                                               | plain          |            |              | 
 numero_relato | integer                |              | not null |                                               | plain          |            |              | 
 texto         | text                   |              | not null |                                               | extended       |            |              | 
 imagen_url    | character varying(500) |              |          |                                               | extended       |            |              | 
Índices:
    "relatos_asegurado_pkey" PRIMARY KEY, btree (id)
    "ix_relatos_asegurado_id" btree (id)
Restricciones de llave foránea:
    "relatos_asegurado_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                                      Tabla «public.relatos_conductor»
    Columna    |          Tipo          | Ordenamiento | Nulable  |                  Por omisión                  | Almacenamiento | Compresión | Estadísticas | Descripción 
---------------+------------------------+--------------+----------+-----------------------------------------------+----------------+------------+--------------+-------------
 id            | integer                |              | not null | nextval('relatos_conductor_id_seq'::regclass) | plain          |            |              | 
 siniestro_id  | integer                |              |          |                                               | plain          |            |              | 
 numero_relato | integer                |              | not null |                                               | plain          |            |              | 
 texto         | text                   |              | not null |                                               | extended       |            |              | 
 imagen_url    | character varying(500) |              |          |                                               | extended       |            |              | 
Índices:
    "relatos_conductor_pkey" PRIMARY KEY, btree (id)
    "ix_relatos_conductor_id" btree (id)
Restricciones de llave foránea:
    "relatos_conductor_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                                        Tabla «public.inspecciones»
      Columna      |          Tipo          | Ordenamiento | Nulable  |               Por omisión                | Almacenamiento | Compresión | Estadísticas | Descripción 
-------------------+------------------------+--------------+----------+------------------------------------------+----------------+------------+--------------+-------------
 id                | integer                |              | not null | nextval('inspecciones_id_seq'::regclass) | plain          |            |              | 
 siniestro_id      | integer                |              |          |                                          | plain          |            |              | 
 numero_inspeccion | integer                |              | not null |                                          | plain          |            |              | 
 descripcion       | text                   |              | not null |                                          | extended       |            |              | 
 imagen_url        | character varying(500) |              |          |                                          | extended       |            |              | 
Índices:
    "inspecciones_pkey" PRIMARY KEY, btree (id)
    "ix_inspecciones_id" btree (id)
Restricciones de llave foránea:
    "inspecciones_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                                      Tabla «public.testigos»
    Columna    |          Tipo          | Ordenamiento | Nulable  |             Por omisión              | Almacenamiento | Compresión | Estadísticas | Descripción 
---------------+------------------------+--------------+----------+--------------------------------------+----------------+------------+--------------+-------------
 id            | integer                |              | not null | nextval('testigos_id_seq'::regclass) | plain          |            |              | 
 siniestro_id  | integer                |              |          |                                      | plain          |            |              | 
 numero_relato | integer                |              | not null |                                      | plain          |            |              | 
 texto         | text                   |              | not null |                                      | extended       |            |              | 
 imagen_url    | character varying(500) |              |          |                                      | extended       |            |              | 
Índices:
    "testigos_pkey" PRIMARY KEY, btree (id)
    "ix_testigos_id" btree (id)
Restricciones de llave foránea:
    "testigos_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                              Tabla «public.visitas_taller»
   Columna    |  Tipo   | Ordenamiento | Nulable  |                Por omisión                 | Almacenamiento | Compresión | Estadísticas | Descripción 
--------------+---------+--------------+----------+--------------------------------------------+----------------+------------+--------------+-------------
 id           | integer |              | not null | nextval('visitas_taller_id_seq'::regclass) | plain          |            |              | 
 siniestro_id | integer |              |          |                                            | plain          |            |              | 
 descripcion  | text    |              | not null |                                            | extended       |            |              | 
Índices:
    "visitas_taller_pkey" PRIMARY KEY, btree (id)
    "ix_visitas_taller_id" btree (id)
    "visitas_taller_siniestro_id_key" UNIQUE CONSTRAINT, btree (siniestro_id)
Restricciones de llave foránea:
    "visitas_taller_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

                                                              Tabla «public.dinamicas_accidente»
   Columna    |  Tipo   | Ordenamiento | Nulable  |                   Por omisión                   | Almacenamiento | Compresión | Estadísticas | Descripción 
--------------+---------+--------------+----------+-------------------------------------------------+----------------+------------+--------------+-------------
 id           | integer |              | not null | nextval('dinamicas_accidente_id_seq'::regclass) | plain          |            |              | 
 siniestro_id | integer |              |          |                                                 | plain          |            |              | 
 descripcion  | text    |              | not null |                                                 | extended       |            |              | 
Índices:
    "dinamicas_accidente_pkey" PRIMARY KEY, btree (id)
    "dinamicas_accidente_siniestro_id_key" UNIQUE CONSTRAINT, btree (siniestro_id)
    "ix_dinamicas_accidente_id" btree (id)
Restricciones de llave foránea:
    "dinamicas_accidente_siniestro_id_fkey" FOREIGN KEY (siniestro_id) REFERENCES siniestros(id)
Método de acceso: heap

