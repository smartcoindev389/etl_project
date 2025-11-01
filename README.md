# ETL Project - MySQL Cloud Historization

ETL system for processing monthly CSV files and storing them in MySQL cloud database with full historization.

## Features

- ✅ Monthly CSV processing with historization
- ✅ Bulk historical data loading
- ✅ Duplicate file detection and prevention
- ✅ Complete audit trail for all loads
- ✅ Support for local and cloud MySQL
- ✅ Automatic month extraction from file paths
- ✅ Scripted, repeatable processes

## Project Structure

```
etl_project/
├── config.py                  # Configuration management
├── etl_monthly_processor.py   # Main ETL processor for monthly files
├── bulk_historical_loader.py # Bulk loader for historical data
├── database/
│   ├── schema.sql            # Database schema definition
│   └── init_database.py      # Database initialization script
├── utils/
│   └── db_utils.py           # Database utility functions
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your database credentials:

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:
- For **local**: Update `DB_HOST`, `DB_USER`, `DB_PASSWORD`
- For **cloud**: Update `CLOUD_DB_*` variables

### 3. Initialize Database

Initialize the database schema:

```bash
# Local database
python database/init_database.py

# Cloud database
python database/init_database.py --cloud
```

## Cloud MySQL Options (Free Tier)

### Recommended Free/Cheap Options:

1. **Railway** (Free tier available)
   - https://railway.app
   - Free tier: $5 credit/month

2. **PlanetScale** (Free tier)
   - https://planetscale.com
   - Free tier: 1 database, 1GB storage

3. **Aiven** (Free trial)
   - https://aiven.io
   - Free trial with MySQL

4. **AWS RDS** (Free tier for 12 months)
   - https://aws.amazon.com/rds/
   - Free tier: t2.micro instance

### Setting Up Cloud MySQL

1. Create account with chosen provider
2. Create MySQL database instance
3. Get connection details (host, port, user, password)
4. Update `.env` file with `CLOUD_DB_*` variables
5. Test connection:
   ```bash
   python test_mysql_connection.py
   ```

## Usage

### Monthly Processing

Process a single CSV file:

```bash
python etl_monthly_processor.py --file path/to/file.csv --cloud
```

Process all files for a specific month:

```bash
python etl_monthly_processor.py --month 2024-12 --path ./data --cloud
```

### Bulk Historical Loading

Load all historical data:

```bash
python bulk_historical_loader.py --path ./data --cloud
```

Dry run (see what would be processed):

```bash
python bulk_historical_loader.py --path ./data --cloud --dry-run
```

Load specific date range:

```bash
python bulk_historical_loader.py \
  --path ./data \
  --start-month 2024-08 \
  --end-month 2024-12 \
  --cloud
```

### Database Utilities

Check database statistics:

```python
from utils.db_utils import get_database_stats
stats = get_database_stats(use_cloud=True)
print(stats)
```

Verify data integrity:

```python
from utils.db_utils import verify_data_integrity
checks = verify_data_integrity(use_cloud=True)
print(checks)
```

## CSV File Organization

The system automatically detects data months from file paths. Supported patterns:

- `2024-12/file.csv` → December 2024
- `2024_12/file.csv` → December 2024
- `Diciembre 24/file.csv` → December 2024
- `Agosto 25/file.csv` → August 2025

## Database Schema

### Main Tables

- **fact_records**: Main data table with historization
- **audit_loads**: Complete audit trail of all ETL loads
- **processed_files**: Track processed files to prevent duplicates
- **monthly_summary**: Aggregated monthly statistics

### Historization

All records include:
- `data_month`: Month of data (YYYY-MM-01)
- `source_file`: Original CSV filename
- `load_ts`: Timestamp when loaded
- `load_id`: Reference to audit_loads table

## Updating Schema for Your CSV Structure

1. **Analyze your CSV files** to identify all columns
2. **Update `database/schema.sql`**:
   - Modify `fact_records` table to match your CSV columns
   - Adjust data types as needed
3. **Update `etl_monthly_processor.py`**:
   - Modify `transform_data()` method if custom transformations needed
   - Update `load_data_to_db()` column mapping if needed
4. **Reinitialize database**:
   ```bash
   python database/init_database.py --cloud
   ```

## Future Automation

The system is designed for cloud automation:

- **Google Cloud Scheduler**: Schedule monthly runs
- **AWS Lambda**: Serverless monthly processing
- **Airflow**: Orchestrate complex workflows
- **GitHub Actions**: CI/CD for ETL processes

Example automation command:
```bash
python etl_monthly_processor.py --month $(date +%Y-%m) --path /cloud/storage/data --cloud
```

## Troubleshooting

### Connection Issues

Test connection:
```bash
python test_mysql_connection.py
```

Update `.env` file with correct credentials.

### Schema Mismatch

If you see column errors, update `database/schema.sql` and reinitialize:
```bash
python database/init_database.py --cloud
```

### Duplicate Files

The system automatically skips already processed files. To reprocess:
```bash
# Edit bulk_historical_loader.py or etl_monthly_processor.py
# Set skip_duplicates=False
```

## Next Steps

1. ✅ Get CSV file structure from client
2. ✅ Update database schema to match CSV columns
3. ✅ Update transform logic if needed
4. ✅ Test with sample CSV files
5. ✅ Load historical data
6. ✅ Set up cloud MySQL instance
7. ✅ Schedule monthly automation

## Support

For questions or issues, check:
- Database logs in `audit_loads` table
- Error messages in `audit_loads.error_message`
- Processed files log in `processed_files` table

