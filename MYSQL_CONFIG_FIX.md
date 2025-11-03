# MySQL Configuration Fix for Large Files

## Problem
When loading large CSV files, you're getting:
- `MySQL server has gone away`
- `Lost connection to MySQL server during query`

This happens because MySQL has limits that are too low for large files.

## Solution: Update MySQL Configuration

### Option 1: Update my.ini/my.cnf (Recommended)

Edit your MySQL configuration file:

**Windows**: `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`  
**Linux/Mac**: `/etc/mysql/my.cnf` or `/etc/my.cnf`

Add or update these settings:

```ini
[mysqld]
max_allowed_packet = 256M
wait_timeout = 600
interactive_timeout = 600
net_read_timeout = 600
net_write_timeout = 600
```

### Option 2: Set via SQL (Temporary - Lost on Restart)

Connect to MySQL and run:

```sql
SET GLOBAL max_allowed_packet = 268435456;  -- 256MB
SET GLOBAL wait_timeout = 600;
SET GLOBAL interactive_timeout = 600;
SET GLOBAL net_read_timeout = 600;
SET GLOBAL net_write_timeout = 600;
```

### Option 3: Use Smaller Batch Size

Edit your `.env` file:

```env
BATCH_SIZE=1000
```

This processes smaller chunks but takes longer.

## After Making Changes

1. **Restart MySQL Server** (if you edited my.ini/my.cnf)
   - Windows: Services → MySQL → Restart
   - Linux: `sudo systemctl restart mysql`
   - Mac: `brew services restart mysql`

2. **Test with small file first**:
   ```bash
   python etl_monthly_processor.py --file test_sample.csv
   ```

3. **Then try the full file again**

## Quick Check Current Settings

```sql
SHOW VARIABLES LIKE 'max_allowed_packet';
SHOW VARIABLES LIKE 'wait_timeout';
```

## Alternative: Process in Smaller Batches

The ETL script now processes in chunks of 5000 rows. If still failing, try:

1. Split the CSV file manually into smaller files
2. Process each file separately
3. Or reduce BATCH_SIZE in .env to 1000

## Test First

Try with the test sample I created:
```bash
python etl_monthly_processor.py --file test_sample.csv
```

If that works, then the issue is definitely MySQL configuration for large files.

