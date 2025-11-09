# ETL Project - Quick Reference for Meetings

## 5-Minute Overview

**What it does**: Processes CSV files and loads them into MySQL databases (local or cloud)

**Key features**:
- Single file processing
- Monthly batch processing
- Historical bulk loading
- Automatic deduplication
- Full audit trail

**Main commands**:
```bash
# Test connection
python test_mysql_connection.py --cloud

# Process one month
python etl_merge_processor.py --month 2025-08 --path "fending_data" --cloud

# Bulk load (preview first)
python bulk_load_all_script.py --path "fending_data" --dry-run --cloud
python bulk_load_all_script.py --path "fending_data" --cloud
```

---

## 10-Minute Setup Demo

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Create `.env` with database credentials
3. **Initialize**: `python database/init_database.py --cloud`
4. **Test**: `python test_mysql_connection.py --cloud`
5. **Process**: `python etl_merge_processor.py --month 2025-08 --path "fending_data" --cloud`

---

## Common Use Cases

### Use Case 1: Process Single File
```bash
python etl_monthly_processor.py --file "path/to/file.csv" --cloud
```

### Use Case 2: Process Month
```bash
python etl_merge_processor.py --month 2025-08 --path "fending_data" --cloud
```

### Use Case 3: Bulk Historical Load
```bash
# Preview
python bulk_load_all_script.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud --dry-run

# Execute
python bulk_load_all_script.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud
```

---

## Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| Connection error | Check `.env` credentials, test with `test_mysql_connection.py` |
| File not found | Verify path, use absolute path |
| Memory error | Reduce `--chunksize` (e.g., `--chunksize 1000`) |
| Duplicate error | System skips duplicates automatically (check `processed_files` table) |

---

## Verification Commands

```sql
-- Check tables
SHOW TABLES;

-- Check counts
SELECT COUNT(*) FROM flags_resumen_total_con_morosidad;

-- Check recent uploads
SELECT * FROM upload_reports ORDER BY report_id DESC LIMIT 10;
```

---

## Key Points to Emphasize

1. **Always use `--dry-run` first** for bulk operations
2. **System automatically skips duplicates** (SHA256 hashing)
3. **Full audit trail** in `audit_loads` table
4. **Works with both local and cloud** databases
5. **Idempotent**: Safe to rerun commands

---

## Questions to Expect

**Q: Can I reprocess a file?**  
A: Yes, but remove its hash from `processed_files` table first.

**Q: What if process fails halfway?**  
A: Safe to rerun - system skips already processed files.

**Q: How to schedule monthly runs?**  
A: Use cron/Task Scheduler to run `etl_merge_processor.py` monthly.

---

*For full details, see MEETING_SCRIPTS.md*

