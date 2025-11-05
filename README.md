# ETL Project - MySQL Cloud Historization

Complete ETL system for processing monthly CSV files and storing them in MySQL database with full historization support.

## Features

- ✅ **Nested folder support** - Automatically discovers and processes CSV files from multiple folders per month
- ✅ Monthly CSV processing with historization
- ✅ Automatic column filtering (handles different CSV structures)
- ✅ **Bulk historical data loading** - Loads ALL CSV files from nested folder structures automatically
- ✅ Duplicate file detection and prevention (SHA256 hashing)
- ✅ Complete audit trail for all loads
- ✅ Support for local and cloud MySQL
- ✅ Automatic month extraction from file paths (YYYY-MM, YYYYMM, month names)
- ✅ Scripted, repeatable processes (no manual work required)
- ✅ Chunked processing for large files
- ✅ Error handling and retry logic

## Project Structure

```
etl_project/
├── config.py                          # Configuration management
├── etl_monthly_processor.py          # Basic ETL processor (filters columns automatically)
├── etl_merge_processor.py            # Merge processor (replicates notebook logic)
├── bulk_historical_loader.py         # Bulk loader for historical data
├── bulk_load_all_script.py          # Complete bulk load script (recommended)
├── test_mysql_connection.py          # Connection testing utility
├── requirements.txt                   # Python dependencies
├── .env.example                      # Environment variables template
│
├── database/
│   ├── schema.sql                    # Base schema template
│   ├── schema_resultados.sql         # Complete schema (111 data columns + metadata)
│   └── init_database.py              # Database initialization
│
├── utils/
│   ├── db_utils.py                   # Database utilities
│   └── schema_generator.py           # Schema generator from CSV
│
└── fending data/                     # Client CSV files (ignored in git)
    ├── Month1/                       # Example: Monthly folders
    │   ├── Folder1/                  # Multiple folders per month
    │   │   ├── resultados_analisis_completo.csv
    │   │   └── grabaciones_multimedia.csv
    │   └── Folder2/
    │       └── todas_conversaciones.csv
    └── Month2/
        └── ...
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your database credentials:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Or manually create .env file
```

Edit `.env` with your MySQL credentials:

```env
# Local MySQL (for XAMPP)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=etl_project

# Cloud MySQL (when ready)
CLOUD_DB_HOST=
CLOUD_DB_PORT=3306
CLOUD_DB_USER=
CLOUD_DB_PASSWORD=
CLOUD_DB_NAME=etl_project

# ETL Configuration
CSV_BASE_PATH=./data
BATCH_SIZE=10000
```

### 3. Initialize Database

```bash
# Local database
python database/init_database.py

# Cloud database
python database/init_database.py --cloud
```

### 4. Test Connection

```bash
# Local
python test_mysql_connection.py

# Cloud
python test_mysql_connection.py --cloud
```

## XAMPP MySQL Configuration

If you're using XAMPP and get "MySQL server has gone away" errors with large files:

### Fix MySQL Configuration

1. Edit `C:\xampp\mysql\bin\my.ini` (as Administrator)

2. Find `[mysqld]` section and add:

```ini
[mysqld]
max_allowed_packet = 256M
wait_timeout = 600
interactive_timeout = 600
net_read_timeout = 600
net_write_timeout = 600
```

3. Restart MySQL in XAMPP Control Panel:
   - Click **Stop** on MySQL
   - Wait a few seconds
   - Click **Start** on MySQL

### Alternative: Quick SQL Fix (Temporary)

If you can't edit the file right now:

1. Open **phpMyAdmin**: http://localhost/phpmyadmin
2. Go to **SQL** tab
3. Run:

```sql
SET GLOBAL max_allowed_packet = 268435456;
SET GLOBAL wait_timeout = 600;
SET GLOBAL interactive_timeout = 600;
SET GLOBAL net_read_timeout = 600;
SET GLOBAL net_write_timeout = 600;
```

**Note**: These settings reset when MySQL restarts, so edit `my.ini` for permanent fix.

## Usage

### Process Single CSV File

```bash
# Process any CSV file (automatically filters columns to match database)
python etl_monthly_processor.py --file "fending data\resultados_analisis_completo.csv"

# Process final merged file
python etl_monthly_processor.py --file "fending data\resultados_analisis_completo_metadata_final_nps2.csv"
```

### Process All Files for a Month

```bash
python etl_monthly_processor.py --month 2025-08 --path "fending data"
```

### Merge and Process (Recommended)

Automatically finds and merges source files (replicates notebook logic):

```bash
# Process August 2025
python etl_merge_processor.py --month 2025-08 --path "fending data"
```

This will:
1. Find `resultados_analisis_completo*.csv` for the month
2. Find `grabaciones_multimedia_*.csv` for the month
3. Find `todas_conversaciones_*.csv` for the month
4. Merge them together
5. Load to database

### Bulk Historical Loading

**Loads ALL CSV files from nested folder structures automatically**

The system automatically:
- Discovers all CSV files recursively (including nested folders)
- Groups files by month (even if in different folders)
- Processes all files from all folders
- Handles multiple folders per month
- Handles multiple files per folder

```bash
# Preview what will be loaded (dry run)
python bulk_load_all_script.py --path "fending data" --dry-run

# Load all historical data (from all folders)
python bulk_load_all_script.py --path "fending data"

# Load specific date range
python bulk_load_all_script.py \
  --path "fending data" \
  --start-month 2024-08 \
  --end-month 2024-12

# Load with cloud database
python bulk_load_all_script.py --path "fending data" --cloud
```

**Alternative (original bulk loader):**
```bash
python bulk_historical_loader.py --path "fending data" --dry-run
python bulk_historical_loader.py --path "fending data"
```

## Database Schema

### Main Tables

- **fact_records**: Main data table (111 data columns + 7 metadata columns)
  - Data columns: All motivo_*_flg, flag_agrupacion_*, metadata from merged files
  - Metadata: source_file, data_month, load_ts, load_id
  - Total: 118 columns

- **audit_loads**: Complete ETL audit trail
  - Tracks all file processing attempts
  - Status, row counts, timing, errors

- **processed_files**: File tracking and duplicate prevention
  - SHA256 file hashing
  - Prevents re-processing same files

- **monthly_summary**: Aggregated monthly statistics

### Schema Details

The database schema (`database/schema_resultados.sql`) matches the final merged CSV structure:
- 111 data columns from `resultados_analisis_completo_metadata_final_nps2.csv`
- 7 metadata columns for historization
- Automatic column filtering for files with different structures

## CSV File Structure

### Supported Files

1. **resultados_analisis_completo.csv** (162 columns)
   - Contains: nombre_archivo, fecha_procesamiento, motivo_* columns (with frase/fraser/simil/subfrases)
   - System automatically filters to flag columns only

2. **grabaciones_multimedia_*.csv** (18 columns)
   - Multimedia recordings metadata
   - Columns: conversation_id, archivo_multimedia, dates, queue info, etc.

3. **todas_conversaciones_*.csv** (19 columns)
   - All conversations metadata
   - Columns: conversation_id, participant info, session details, etc.

4. **resultados_analisis_completo_metadata_final_nps2.csv** (111 columns)
   - FINAL merged table (ready to load directly)
   - Contains: flags only + merged metadata + NPS data

## Features Details

### Automatic Column Filtering

The ETL processor automatically:
- Reads database schema columns
- Filters CSV columns to match database
- Only loads columns that exist in database
- Handles files with different structures gracefully

### Nested Folder Support

The bulk loader handles complex folder structures:
- **Multiple folders per month**: Automatically finds all CSV files in all subfolders
- **Nested structures**: Recursively searches all subdirectories
- **Multiple files per folder**: Processes all CSV files in each folder
- **Organized by month**: Groups files by month regardless of folder structure

Example structure supported:
```
data/
├── 2024-08/
│   ├── Folder1/
│   │   ├── resultados_analisis_completo.csv
│   │   └── grabaciones_multimedia.csv
│   └── Folder2/
│       └── todas_conversaciones.csv
├── 2024-09/
│   └── ...
└── 2024-10/
    ├── Subfolder1/
    │   └── file1.csv
    └── Subfolder2/
        └── file2.csv
```

All files are automatically discovered and processed!

### Historization

- **All records preserved**: Never deletes data
- **Month tracking**: Each record has `data_month` (YYYY-MM-01)
- **Source tracking**: `source_file` and `source_type` columns
- **Load tracking**: Linked to `load_id` in audit table
- **Timestamp tracking**: `load_ts` records when loaded
- **Duplicate prevention**: Files tracked by SHA256 hash

### Error Handling

- Connection retry logic for timeouts
- Chunked processing for large files
- Error logging in `audit_loads` table
- Resume capability (skips already processed files)

## Common Commands

```bash
# Test connection
python test_mysql_connection.py

# Initialize database
python database/init_database.py

# Process single file
python etl_monthly_processor.py --file "path/to/file.csv"

# Process month
python etl_monthly_processor.py --month 2025-08 --path "fending data"

# Merge and process (recommended for monthly processing)
python etl_merge_processor.py --month 2025-08 --path "fending data"

# Bulk load ALL files from nested folders (recommended for historical load)
python bulk_load_all_script.py --path "fending data" --dry-run
python bulk_load_all_script.py --path "fending data"
```

## Troubleshooting

### "Table doesn't exist"
```bash
# Reinitialize database
python database/init_database.py
```

### "MySQL server has gone away"
- **XAMPP**: Update `C:\xampp\mysql\bin\my.ini` (see XAMPP MySQL Configuration above)
- **Other MySQL**: Update `max_allowed_packet` in MySQL config
- **Quick fix**: Reduce `BATCH_SIZE` in `.env` to 1000

### "Connection failed"
- Check `.env` file credentials
- Verify MySQL is running (XAMPP Control Panel)
- Test connection: `python test_mysql_connection.py`

### "Column mismatch"
- System automatically filters columns
- If issue persists, check database schema matches CSV structure

### Large Files Failing
1. Update MySQL `max_allowed_packet` (see XAMPP MySQL Configuration)
2. Reduce `BATCH_SIZE` in `.env`
3. Process in smaller batches manually

## Testing

### Test with Sample Data

```bash
# Test with small sample (100 rows)
python etl_monthly_processor.py --file test_sample.csv
```

### Verify Data Loaded

Check database:
```sql
-- Count records
SELECT COUNT(*) FROM fact_records;

-- Check by month
SELECT data_month, COUNT(*) 
FROM fact_records 
GROUP BY data_month;

-- Check audit logs
SELECT * FROM audit_loads ORDER BY start_ts DESC LIMIT 10;
```

## Database Utilities

```python
from utils.db_utils import get_database_stats, verify_data_integrity

# Get statistics
stats = get_database_stats(use_cloud=False)
print(f"Total records: {stats['total_records']}")
print(f"Records by month: {stats['records_by_month']}")

# Verify integrity
checks = verify_data_integrity(use_cloud=False)
print(f"All checks passed: {checks['all_passed']}")
```

## Cloud Deployment

### Setup Cloud MySQL

1. Choose provider (Railway, PlanetScale, AWS RDS, Aiven)
2. Create MySQL database instance
3. Get connection credentials
4. Update `.env` with `CLOUD_DB_*` variables
5. Test: `python test_mysql_connection.py --cloud`
6. Initialize: `python database/init_database.py --cloud`

### Automation Ready

All scripts are CLI-based and ready for:
- Google Cloud Scheduler
- AWS Lambda / EventBridge
- GitHub Actions
- Cron jobs

Example:
```bash
# Monthly automation
python etl_merge_processor.py --month $(date +%Y-%m) --path /cloud/storage/data --cloud
```

## Project Status

✅ **Complete and Ready for Production**

- All core functionality implemented
- Tested with local MySQL (XAMPP)
- Ready for cloud deployment
- Comprehensive error handling
- Complete documentation

## Next Steps

1. ✅ Set up local MySQL (XAMPP) - **DONE**
2. ✅ Test with sample files - **DONE**
3. ⚠️ Update MySQL config for large files (if needed)
4. ⚠️ Set up cloud MySQL (when ready)
5. ⚠️ Load all historical data
6. ⚠️ Set up monthly automation

## Support

For issues:
1. Check `audit_loads` table for error details
2. Review connection logs
3. Verify MySQL configuration
4. Test with smaller files first

## Process Flow

For visual flowcharts and detailed explanations (English and Spanish), see:
- FLOWCHART.md

---

**Version**: 1.0.0  
**Last Updated**: October 31, 2025  
**Status**: Production Ready

