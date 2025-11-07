# Proyecto ETL - Guía de Uso

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Crear archivo `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=speechanalytics

CLOUD_DB_HOST=tu-host-en-la-nube
CLOUD_DB_PORT=3306
CLOUD_DB_USER=tu-usuario-cloud
CLOUD_DB_PASSWORD=tu-contraseña-cloud
CLOUD_DB_NAME=speechanalytics
```

## Inicio Rápido - Subir Todos los Archivos CSV

### Método 1: Estructura de Carpeta Plana

```bash
# 1. Generar archivos SQL
python tools/generate_sql_from_csvs.py --path "fending_data" --sample 2000

# 2. Crear tablas
python database/init_database.py --cloud

# 3. Cargar todos los archivos CSV
python create_tables_from_csvs.py --path "fending_data" --cloud --chunksize 5000
```

### Método 2: Carpetas Anidadas

```bash
# Vista previa de archivos
python bulk_load_all_script.py --path "fending_data" --dry-run --cloud

# Cargar todos los archivos
python bulk_load_all_script.py --path "fending_data" --cloud

# Cargar rango de fechas
python bulk_load_all_script.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud
```

### Método 3: Procesamiento Mensual

```bash
# Cargar todos los CSVs
python monthly_loader.py --path "fending_data" --cloud

# Cargar mes específico
python monthly_loader.py --path "fending_data" --month 2025-08 --cloud
```

## Comandos

### Generar Archivos SQL

```bash
python tools/generate_sql_from_csvs.py --path "fending_data" --sample 2000 --out "database"
```

Opciones:
- `--path PATH` - Carpeta CSV (por defecto: `fending_data`)
- `--sample N` - Filas a muestrear (por defecto: `2000`)
- `--out PATH` - Carpeta de salida (por defecto: `database`)

### Inicializar Base de Datos

```bash
python database/init_database.py --cloud
```

Opciones:
- `--cloud` - Usar base de datos en la nube

### Cargar Archivos CSV

```bash
python create_tables_from_csvs.py --path "fending_data" --cloud --chunksize 5000 --sample 1000
```

Opciones:
- `--path PATH` - Carpeta CSV (por defecto: `fending_data`)
- `--cloud` - Usar base de datos en la nube
- `--chunksize N` - Filas por fragmento (por defecto: `5000`)
- `--sample N` - Filas a muestrear (por defecto: `1000`)

### Cargador Mensual

```bash
python monthly_loader.py --path "fending_data" --month 2025-08 --cloud --chunksize 5000 --sample 1000
```

Opciones:
- `--path PATH` - Ruta base (por defecto: `fending_data`)
- `--month YYYY-MM` - Mes a procesar
- `--cloud` - Usar base de datos en la nube
- `--chunksize N` - Tamaño de fragmento (por defecto: `5000`)
- `--sample N` - Filas a muestrear (por defecto: `1000`)

### Carga Masiva Completa

```bash
python bulk_load_all_script.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud --skip-duplicates --dry-run
```

Opciones:
- `--path PATH` - Ruta base (requerido)
- `--start-month YYYY-MM` - Mes inicial
- `--end-month YYYY-MM` - Mes final
- `--cloud` - Usar base de datos en la nube
- `--skip-duplicates` - Omitir archivos procesados (por defecto: True)
- `--dry-run` - Solo vista previa

### Procesador ETL Mensual

```bash
python etl_monthly_processor.py --file "data/file.csv" --cloud --skip-duplicates
python etl_monthly_processor.py --month 2025-08 --path "fending_data" --cloud
```

Opciones:
- `--file PATH` - Procesar archivo único
- `--month YYYY-MM` - Procesar mes
- `--path PATH` - Ruta base
- `--cloud` - Usar base de datos en la nube
- `--skip-duplicates` - Omitir archivos procesados (por defecto: True)

### Procesador ETL de Fusión

```bash
python etl_merge_processor.py --month 2025-08 --path "fending_data" --cloud
```

Opciones:
- `--month YYYY-MM` - Procesar mes (requerido)
- `--path PATH` - Ruta base
- `--cloud` - Usar base de datos en la nube

### Cargador Histórico Masivo

```bash
python bulk_historical_loader.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud --skip-duplicates --dry-run
```

Opciones:
- `--path PATH` - Ruta base (requerido)
- `--start-month YYYY-MM` - Mes inicial
- `--end-month YYYY-MM` - Mes final
- `--cloud` - Usar base de datos en la nube
- `--skip-duplicates` - Omitir archivos procesados (por defecto: True)
- `--dry-run` - Solo vista previa

### Probar Conexión

```bash
python test_mysql_connection.py --cloud
```

Opciones:
- `--cloud` - Probar base de datos en la nube

### Verificar Datos en la Nube

```bash
python check_cloud_data.py
```

## Verificar Datos

```sql
SHOW TABLES;
SELECT COUNT(*) FROM flags_resumen_total_con_morosidad;
SELECT COUNT(*) FROM flags_resumen_total_con_pagos_atc;
SELECT COUNT(*) FROM flags_resumen_total_con_pagos_galicia;
SELECT COUNT(*) FROM resultados_analisis_completo_metadata_final_nps;
SELECT * FROM upload_reports ORDER BY report_id DESC LIMIT 10;
```

