# Requirements Analysis

## Current Status

### ✅ Completed
1. Database structure created (`etl_project` database)
2. Basic tables: `fact_records`, `audit_loads`
3. Test connection script exists

### ⚠️ Pending Information Needed
1. **Actual CSV file structure** - Need column names and data types
2. **CSV file samples** - To test ETL process
3. **Excel file structure** - Reference file mentioned ("Pasos para inbound - workana.xlsx")
4. **Original notebook structure** - To understand current transformations

## Requirements Breakdown

### 1. Database Design ✅
- **Status**: Schema created with historization support
- **Tables**:
  - `fact_records`: Main data table with metadata
  - `audit_loads`: Complete ETL audit trail
  - `processed_files`: Duplicate prevention
  - `monthly_summary`: Aggregated statistics

### 2. ETL Process ✅
- **Status**: Main ETL processor created
- **Features**:
  - Monthly processing
  - File deduplication
  - Error handling
  - Audit logging
  - Automatic month extraction

### 3. Bulk Loading ✅
- **Status**: Bulk loader created
- **Features**:
  - Historical data loading
  - Date range filtering
  - Dry run mode
  - Progress tracking

### 4. Cloud Database ⚠️
- **Status**: Configuration ready, needs setup
- **Action Required**: Client needs to choose and configure cloud provider
- **Options Provided**: Railway, PlanetScale, Aiven, AWS RDS

### 5. Automation Ready ✅
- **Status**: All scripts are CLI-based, ready for automation
- **Future**: Can integrate with cloud schedulers

## Next Steps

### Immediate Actions Required

1. **Get CSV Structure**
   - Analyze actual CSV files
   - Update `database/schema.sql` with correct columns
   - Update `etl_monthly_processor.py` column mapping

2. **Test with Sample Data**
   - Use client's CSV files
   - Verify ETL process works
   - Fix any column/data type issues

3. **Cloud Database Setup**
   - Client chooses provider
   - Configure connection
   - Test and initialize

4. **Bulk Historical Load**
   - Load all historical CSV files
   - Verify data integrity
   - Generate summary reports

### Schema Update Process

When CSV structure is known:

1. **Update `database/schema.sql`**:
   ```sql
   CREATE TABLE fact_records (
     record_id BIGINT AUTO_INCREMENT PRIMARY KEY,
     -- Add actual CSV columns here
     column1 VARCHAR(255),
     column2 DECIMAL(15,2),
     -- ... etc
     
     -- Keep metadata columns
     source_file VARCHAR(500),
     data_month DATE,
     load_ts TIMESTAMP,
     -- ...
   );
   ```

2. **Update `etl_monthly_processor.py`**:
   - Modify `transform_data()` if custom logic needed
   - Adjust `load_data_to_db()` if column mapping required

3. **Reinitialize Database**:
   ```bash
   python database/init_database.py --cloud
   ```

## CSV File Patterns Expected

Based on client description:
- `resultados_analisis_completo*.csv` - Main results files
- `metadata*.csv` - Metadata files
- `speech_analytics*.csv` - Speech analytics files
- Files organized by month (December 24, August 25, etc.)

## Data Flow

```
CSV Files (Monthly)
    ↓
Extract (Read CSV)
    ↓
Transform (Clean, merge, cross-reference)
    ↓
Load (Insert to MySQL)
    ↓
Audit (Log in audit_loads)
    ↓
Track (Record in processed_files)
```

## Historization Strategy

1. **All records preserved** - No data deletion
2. **Month tracking** - Each record has `data_month`
3. **Load tracking** - Each record linked to `load_id`
4. **File tracking** - Prevent duplicate processing
5. **Audit trail** - Complete history in `audit_loads`

## Automation Design

Future cloud automation:
- **Monthly trigger**: Cloud scheduler (e.g., Google Cloud Scheduler)
- **Process**: Run `etl_monthly_processor.py --month YYYY-MM --cloud`
- **Notification**: Email/Slack on completion/failure
- **Monitoring**: Check `audit_loads.status`

## Questions to Resolve

1. What are the exact column names in CSV files?
2. What data types should be used?
3. What transformations are needed (currently done in notebook)?
4. How are multiple CSV files joined/cross-referenced?
5. What is the preferred cloud provider?
6. What is the volume of data (files/month, rows/file)?

## Estimated Timeline

- **Phase 1** (Current): Setup and structure ✅
- **Phase 2**: Schema update based on CSV structure (1-2 hours)
- **Phase 3**: Testing with sample data (1-2 hours)
- **Phase 4**: Cloud setup and migration (1-2 hours)
- **Phase 5**: Bulk historical load (2-4 hours depending on volume)
- **Phase 6**: Final testing and documentation (1 hour)

**Total Estimated Time**: 6-11 hours

