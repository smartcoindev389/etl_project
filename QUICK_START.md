# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- MySQL (local or cloud)
- CSV files ready

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your database credentials:
   ```env
   # For local MySQL
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=etl_project
   
   # For cloud MySQL (when ready)
   CLOUD_DB_HOST=your_cloud_host
   CLOUD_DB_USER=your_cloud_user
   CLOUD_DB_PASSWORD=your_cloud_password
   CLOUD_DB_NAME=etl_project
   ```

## Step 3: Initialize Database

```bash
# Local database
python database/init_database.py

# OR cloud database
python database/init_database.py --cloud
```

## Step 4: Test Connection

```bash
# Local
python test_mysql_connection.py

# Cloud
python test_mysql_connection.py --cloud
```

## Step 5: Process Your First CSV File

```bash
# Process single file
python etl_monthly_processor.py --file path/to/your/file.csv

# Process all files for a month
python etl_monthly_processor.py --month 2024-12 --path ./data
```

## Step 6: Load Historical Data (Bulk)

```bash
# Dry run first (see what will be processed)
python bulk_historical_loader.py --path ./data --dry-run

# Actually load data
python bulk_historical_loader.py --path ./data
```

## Common Commands

```bash
# Monthly processing
python etl_monthly_processor.py --month 2024-12 --path ./data --cloud

# Single file
python etl_monthly_processor.py --file data/2024-12/file.csv --cloud

# Bulk load with date range
python bulk_historical_loader.py \
  --path ./data \
  --start-month 2024-08 \
  --end-month 2024-12 \
  --cloud
```

## Troubleshooting

### "Connection failed"
- Check `.env` file credentials
- Verify MySQL is running
- For cloud: check firewall/network settings

### "Table doesn't exist"
- Run database initialization:
  ```bash
  python database/init_database.py
  ```

### "Column mismatch"
- Update `database/schema.sql` with your CSV columns
- Reinitialize database

## Next Steps

1. ✅ Update database schema for your CSV structure
2. ✅ Test with sample CSV files
3. ✅ Set up cloud MySQL (see `CLOUD_SETUP_GUIDE.md`)
4. ✅ Load historical data
5. ✅ Set up automation

For detailed information, see `README.md`

