# ETL Project - Usage Guide

## Installation

```bash
pip install -r requirements.txt
```

## Setup

Create `.env` file:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=speechanalytics

CLOUD_DB_HOST=your-cloud-host
CLOUD_DB_PORT=3306
CLOUD_DB_USER=your-cloud-user
CLOUD_DB_PASSWORD=your-cloud-password
CLOUD_DB_NAME=speechanalytics
```

## Quick Start - Upload All CSV Files

### Method 1: Flat Folder Structure

```bash
# 1. Generate SQL files
python tools/generate_sql_from_csvs.py --path "fending_data" --sample 2000

# 2. Create tables
python database/init_database.py --cloud

# 3. Load all CSV files
python create_tables_from_csvs.py --path "fending_data" --cloud --chunksize 5000
```

### Method 2: Nested Folders

```bash
# Preview files
python bulk_load_all_script.py --path "fending_data" --dry-run --cloud

# Load all files
python bulk_load_all_script.py --path "fending_data" --cloud

# Load date range
python bulk_load_all_script.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud
```

### Method 3: Monthly Processing

```bash
# Load all CSVs
python monthly_loader.py --path "fending_data" --cloud

# Load specific month
python monthly_loader.py --path "fending_data" --month 2025-08 --cloud
```

## Commands

### Generate SQL Files

```bash
python tools/generate_sql_from_csvs.py --path "fending_data" --sample 2000 --out "database"
```

Options:
- `--path PATH` - CSV folder (default: `fending_data`)
- `--sample N` - Rows to sample (default: `2000`)
- `--out PATH` - Output folder (default: `database`)

### Initialize Database

```bash
python database/init_database.py --cloud
```

Options:
- `--cloud` - Use cloud database

### Load CSV Files

```bash
python create_tables_from_csvs.py --path "fending_data" --cloud --chunksize 5000 --sample 1000
```

Options:
- `--path PATH` - CSV folder (default: `fending_data`)
- `--cloud` - Use cloud database
- `--chunksize N` - Rows per chunk (default: `5000`)
- `--sample N` - Rows to sample (default: `1000`)

### Monthly Loader

```bash
python monthly_loader.py --path "fending_data" --month 2025-08 --cloud --chunksize 5000 --sample 1000
```

Options:
- `--path PATH` - Base path (default: `fending_data`)
- `--month YYYY-MM` - Month to process
- `--cloud` - Use cloud database
- `--chunksize N` - Insert chunk size (default: `5000`)
- `--sample N` - Rows to sample (default: `1000`)

### Bulk Load All

```bash
python bulk_load_all_script.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud --skip-duplicates --dry-run
```

Options:
- `--path PATH` - Base path (required)
- `--start-month YYYY-MM` - Start month
- `--end-month YYYY-MM` - End month
- `--cloud` - Use cloud database
- `--skip-duplicates` - Skip processed files (default: True)
- `--dry-run` - Preview only

### ETL Monthly Processor

```bash
python etl_monthly_processor.py --file "data/file.csv" --cloud --skip-duplicates
python etl_monthly_processor.py --month 2025-08 --path "fending_data" --cloud
```

Options:
- `--file PATH` - Process single file
- `--month YYYY-MM` - Process month
- `--path PATH` - Base path
- `--cloud` - Use cloud database
- `--skip-duplicates` - Skip processed files (default: True)

### ETL Merge Processor

```bash
python etl_merge_processor.py --month 2025-08 --path "fending_data" --cloud
```

Options:
- `--month YYYY-MM` - Process month (required)
- `--path PATH` - Base path
- `--cloud` - Use cloud database

### Bulk Historical Loader

```bash
python bulk_historical_loader.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud --skip-duplicates --dry-run
```

Options:
- `--path PATH` - Base path (required)
- `--start-month YYYY-MM` - Start month
- `--end-month YYYY-MM` - End month
- `--cloud` - Use cloud database
- `--skip-duplicates` - Skip processed files (default: True)
- `--dry-run` - Preview only

### Test Connection

```bash
python test_mysql_connection.py --cloud
```

Options:
- `--cloud` - Test cloud database

### Check Cloud Data

```bash
python check_cloud_data.py
```

## Verify Data

```sql
SHOW TABLES;
SELECT COUNT(*) FROM flags_resumen_total_con_morosidad;
SELECT COUNT(*) FROM flags_resumen_total_con_pagos_atc;
SELECT COUNT(*) FROM flags_resumen_total_con_pagos_galicia;
SELECT COUNT(*) FROM resultados_analisis_completo_metadata_final_nps;
SELECT * FROM upload_reports ORDER BY report_id DESC LIMIT 10;
```
