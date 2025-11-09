# ETL Project - Presentation Outline

## Slide 1: Title Slide
**Title**: ETL Project - CSV to MySQL Processing System
**Subtitle**: Complete Usage Guide and Training
**Presenter**: [Your Name]
**Date**: [Date]

---

## Slide 2: Agenda
1. Project Overview
2. Architecture & Components
3. Setup & Installation
4. Main Workflows
5. Common Commands
6. Verification & Monitoring
7. Troubleshooting
8. Q&A

---

## Slide 3: Project Overview
**What is this project?**
- ETL (Extract, Transform, Load) system
- Processes CSV files
- Loads data into MySQL databases
- Supports local and cloud databases

**Key Capabilities**:
- Single file processing
- Monthly batch processing
- Historical bulk loading
- Automatic deduplication
- Full audit trail

---

## Slide 4: What Problems Does It Solve?
**Before**:
- Manual CSV processing
- No deduplication
- No audit trail
- Time-consuming bulk operations

**After**:
- Automated processing
- Automatic duplicate detection
- Complete audit trail
- Efficient bulk operations
- Cloud-ready

---

## Slide 5: Project Structure
```
etl_project/
├── config.py                    # Configuration
├── database/                    # Database scripts
├── etl_monthly_processor.py    # Single file processor
├── etl_merge_processor.py      # Monthly merge processor
├── bulk_load_all_script.py     # Bulk loader
├── utils/                       # Utilities
└── tools/                       # Helper scripts
```

---

## Slide 6: Core Components
1. **Configuration** (`config.py`)
   - Database connections
   - Environment variables
   - Processing settings

2. **Database Initialization** (`database/init_database.py`)
   - Schema creation
   - Table setup
   - Index creation

3. **ETL Processors**
   - Single file processor
   - Monthly merge processor
   - Bulk historical loader

---

## Slide 7: Data Flow
```
CSV Files
    ↓
Read & Parse
    ↓
Transform & Merge
    ↓
Validate
    ↓
Load to MySQL
    ↓
Audit Log
```

---

## Slide 8: Prerequisites
- Python 3.7+
- MySQL database (local or cloud)
- Access to CSV data files
- Database credentials

---

## Slide 9: Installation
**Step 1**: Install dependencies
```bash
pip install -r requirements.txt
```

**Dependencies**:
- pandas (data processing)
- SQLAlchemy (database ORM)
- pymysql (MySQL driver)
- python-dotenv (environment variables)

---

## Slide 10: Configuration
**Create `.env` file**:
```env
# Local Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=speechanalytics

# Cloud Database
CLOUD_DB_HOST=your-cloud-host
CLOUD_DB_PORT=3306
CLOUD_DB_USER=your-cloud-user
CLOUD_DB_PASSWORD=your-cloud-password
CLOUD_DB_NAME=speechanalytics
```

**⚠️ Never commit `.env` to version control!**

---

## Slide 11: Initialize Database
**Command**:
```bash
python database/init_database.py --cloud
```

**What it does**:
- Creates database schema
- Sets up all tables
- Creates indexes
- Sets up audit tables

---

## Slide 12: Test Connection
**Command**:
```bash
python test_mysql_connection.py --cloud
```

**Expected output**: "Connection successful!"

**If it fails**: Check `.env` credentials

---

## Slide 13: Use Case 1 - Single File
**Scenario**: Process one CSV file

**Command**:
```bash
python etl_monthly_processor.py --file "path/to/file.csv" --cloud
```

**What happens**:
1. Reads CSV file
2. Detects data month
3. Transforms data
4. Loads to database
5. Records file hash

---

## Slide 14: Use Case 2 - Monthly Processing
**Scenario**: Process all files for a month (with merging)

**Command**:
```bash
python etl_merge_processor.py --month 2025-08 --path "fending_data" --cloud
```

**What happens**:
1. Finds all CSV files for the month
2. Merges them (notebook logic)
3. Loads merged result
4. Creates audit records

---

## Slide 15: Use Case 3 - Bulk Historical Load
**Scenario**: Load all historical data

**Step 1 - Preview**:
```bash
python bulk_load_all_script.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud --dry-run
```

**Step 2 - Execute**:
```bash
python bulk_load_all_script.py --path "fending_data" --start-month 2024-08 --end-month 2024-12 --cloud
```

---

## Slide 16: Command Options
**Common Options**:
- `--cloud`: Use cloud database
- `--dry-run`: Preview without executing
- `--skip-duplicates`: Skip processed files (default: True)
- `--chunksize N`: Rows per batch (default: 5000)
- `--path PATH`: CSV folder path
- `--month YYYY-MM`: Specific month to process

---

## Slide 17: Quick Reference - Database Operations
```bash
# Initialize
python database/init_database.py --cloud

# Test connection
python test_mysql_connection.py --cloud

# Check data
python check_cloud_data.py
```

---

## Slide 18: Quick Reference - Processing
```bash
# Single file
python etl_monthly_processor.py --file "file.csv" --cloud

# Monthly
python etl_merge_processor.py --month 2025-08 --path "fending_data" --cloud

# Bulk
python bulk_load_all_script.py --path "fending_data" --cloud
```

---

## Slide 19: Verification - SQL Queries
**Check tables**:
```sql
SHOW TABLES;
```

**Check counts**:
```sql
SELECT COUNT(*) FROM flags_resumen_total_con_morosidad;
```

**Check recent uploads**:
```sql
SELECT * FROM upload_reports ORDER BY report_id DESC LIMIT 10;
```

---

## Slide 20: Monitoring
**What the system tracks**:
- ✅ Processed files (SHA256 hashes)
- ✅ Load timestamps
- ✅ Record counts
- ✅ Errors and failures
- ✅ Processing duration

**Where to check**:
- `audit_loads` table
- `processed_files` table
- `upload_reports` table

---

## Slide 21: Troubleshooting - Connection Errors
**Symptom**: "Connection refused" or "Access denied"

**Solutions**:
1. Verify `.env` credentials
2. Check database is running
3. Verify network/firewall settings
4. Test with `test_mysql_connection.py`

---

## Slide 22: Troubleshooting - File Errors
**Symptom**: "File not found"

**Solutions**:
1. Check file path is correct
2. Use absolute paths
3. Verify file permissions

**Symptom**: Memory issues

**Solutions**:
1. Reduce `--chunksize` (e.g., `--chunksize 1000`)
2. Process files individually
3. Increase system memory

---

## Slide 23: Troubleshooting - Data Errors
**Symptom**: "Duplicate entry" errors

**Solution**: System skips duplicates automatically. Check `processed_files` table.

**Symptom**: "Incorrect column type"

**Solution**:
1. Regenerate SQL: `python tools/generate_sql_from_csvs.py`
2. Reinitialize: `python database/init_database.py --cloud`

---

## Slide 24: Best Practices
1. ✅ **Always test first**: Use `--dry-run`
2. ✅ **Start small**: Process one month first
3. ✅ **Monitor progress**: Check audit logs
4. ✅ **Keep backups**: Backup before bulk operations
5. ✅ **Use version control**: But never commit `.env`

---

## Slide 25: Performance Tips
**Chunk Size Guidelines**:
- Small files: 1,000-5,000
- Large files: 5,000-10,000
- Very large files: 10,000+

**Processing Tips**:
- Process during off-peak hours
- Use appropriate chunk sizes
- Monitor memory usage

---

## Slide 26: Common Questions
**Q: Can I reprocess a file?**  
A: Yes, but remove its hash from `processed_files` table first.

**Q: What if process fails halfway?**  
A: Safe to rerun - system skips already processed files.

**Q: How to schedule monthly runs?**  
A: Use cron/Task Scheduler with `etl_merge_processor.py`.

---

## Slide 27: Next Steps
1. **Set up environment**
   - Install dependencies
   - Create `.env` file
   - Test connection

2. **Run a test**
   - Process one file or month
   - Verify data loaded

3. **Load historical data**
   - Use dry-run first
   - Then execute full load

---

## Slide 28: Resources
**Documentation**:
- `README.md` - Main documentation
- `README_ES.md` - Spanish documentation
- `FLOWCHART.md` - Process diagrams
- `MEETING_SCRIPTS.md` - Full meeting scripts

**Support**:
- Check documentation first
- Review troubleshooting section
- Check audit logs in database

---

## Slide 29: Key Takeaways
1. ✅ Automated CSV to MySQL processing
2. ✅ Supports local and cloud databases
3. ✅ Automatic deduplication
4. ✅ Full audit trail
5. ✅ Safe to rerun (idempotent)

---

## Slide 30: Q&A
**Questions?**

**Contact**: [Your contact information]

**Thank you for your attention!**

---

## Presentation Tips

### Timing Guide
- **30-minute meeting**: Slides 1-15, 26-30
- **60-minute meeting**: Slides 1-28, 30
- **90-minute meeting**: All slides + live demo

### Visual Aids
- Show actual commands in terminal
- Display database queries and results
- Share screen for live demo
- Use flowcharts from `FLOWCHART.md`

### Engagement
- Pause after each major section
- Ask for questions frequently
- Use real examples from your data
- Show actual outputs/results

---

*Last Updated: [Current Date]*

