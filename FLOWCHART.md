# ETL Process Flowcharts (EN/ES)

## English: End-to-End ETL Flow

```mermaid
flowchart TD
  A[Start] --> B[Read .env configuration]
  B --> C{Target DB}
  C -->|Local| D[Create SQLAlchemy engine (local)]
  C -->|Cloud| E[Create SQLAlchemy engine (cloud)]
  D --> F[Initialize schema if needed]
  E --> F[Initialize schema if needed]
  F --> G{Mode}
  G -->|Single file| H[etl_monthly_processor.py --file]
  G -->|Monthly merge| I[etl_merge_processor.py --month]
  G -->|Bulk historical| J[bulk_load_all_script.py --path]

  H --> H1[Identify source type]
  H1 --> H2[Extract data month from path]
  H2 --> H3[Read CSV (pandas)]
  H3 --> H4[Transform: basic cleanup, add source_type]
  H4 --> H5[Filter columns to match DB schema]
  H5 --> H6[Chunked load with retries]
  H6 --> H7[Write audit_loads + processed_files]
  H7 --> K[Finish]

  I --> I1[Discover month files (resultados, grabaciones, conversaciones, nps)]
  I1 --> I2[Load dataframes]
  I2 --> I3[Merge per notebook logic]
  I3 --> I4[Filter columns to DB schema]
  I4 --> I5[Chunked load with retries]
  I5 --> I6[Write audit + processed_files]
  I6 --> K

  J --> J1[Discover all CSV recursively by month and folder]
  J1 --> J2[Group files by month]
  J2 --> J3[Iterate folders/files per month]
  J3 --> J4[Process each file via ETLMonthlyProcessor]
  J4 --> J5[Track successes/skips/failures]
  J5 --> J6[Generate report]
  J6 --> K
```

### Components and Responsibilities (EN)
- config.py: Loads DB/ETL settings from `.env` (local/cloud, batch size, base path).
- database/init_database.py: Creates `etl_project` schema and tables when needed.
- etl_monthly_processor.py: Single-file ETL (detects month, filters columns, loads in chunks, writes audit and file hash).
- etl_merge_processor.py: Finds monthly inputs, merges like the notebook, then loads.
- bulk_load_all_script.py: Full historical loader; discovers nested folders, groups by month, processes everything.
- Tables: `fact_records` (data), `audit_loads` (audits), `processed_files` (hashes), `monthly_summary` (stats).

---

## Español: Flujo ETL de Extremo a Extremo

```mermaid
flowchart TD
  A[Inicio] --> B[Leer configuración .env]
  B --> C{BD destino}
  C -->|Local| D[Crear engine SQLAlchemy (local)]
  C -->|Nube| E[Crear engine SQLAlchemy (nube)]
  D --> F[Inicializar esquema si es necesario]
  E --> F[Inicializar esquema si es necesario]
  F --> G{Modo}
  G -->|Archivo único| H[etl_monthly_processor.py --file]
  G -->|Merge mensual| I[etl_merge_processor.py --month]
  G -->|Histórico masivo| J[bulk_load_all_script.py --path]

  H --> H1[Identificar tipo de fuente]
  H1 --> H2[Extraer mes de datos desde la ruta]
  H2 --> H3[Leer CSV (pandas)]
  H3 --> H4[Transformar: limpieza básica, agregar source_type]
  H4 --> H5[Filtrar columnas para coincidir con el esquema]
  H5 --> H6[Carga por lotes con reintentos]
  H6 --> H7[Escribir audit_loads + processed_files]
  H7 --> K[Fin]

  I --> I1[Descubrir archivos del mes (resultados, grabaciones, conversaciones, nps)]
  I1 --> I2[Cargar dataframes]
  I2 --> I3[Merge según lógica del notebook]
  I3 --> I4[Filtrar columnas al esquema]
  I4 --> I5[Carga por lotes con reintentos]
  I5 --> I6[Escribir auditoría + archivos procesados]
  I6 --> K

  J --> J1[Descubrir todos los CSV recursivamente por mes y carpeta]
  J1 --> J2[Agrupar archivos por mes]
  J2 --> J3[Iterar carpetas/archivos por mes]
  J3 --> J4[Procesar cada archivo con ETLMonthlyProcessor]
  J4 --> J5[Rastrear éxitos/omisiones/errores]
  J5 --> J6[Generar reporte]
  J6 --> K
```

### Componentes y Responsabilidades (ES)
- config.py: Carga parámetros de BD/ETL desde `.env` (local/nube, tamaño de lote, ruta base).
- database/init_database.py: Crea el esquema `etl_project` y tablas cuando sea necesario.
- etl_monthly_processor.py: ETL para archivo único (detecta mes, filtra columnas, carga por lotes, escribe auditoría y hash del archivo).
- etl_merge_processor.py: Encuentra insumos mensuales, hace merge como el notebook y luego carga.
- bulk_load_all_script.py: Cargador histórico completo; descubre carpetas anidadas, agrupa por mes y procesa todo.
- Tablas: `fact_records` (datos), `audit_loads` (auditoría), `processed_files` (hashes), `monthly_summary` (estadísticas).

---

## Notes / Notas
- Large files: tune MySQL (`max_allowed_packet`, timeouts) or reduce `BATCH_SIZE` in `.env`.
- Idempotency: `processed_files` prevents reloading the same file (SHA256).
- Historization: every row gets `data_month`, `source_file`, `load_ts`, and `load_id` for full traceability.
