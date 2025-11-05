"""
Check Cloud Database Data
Diagnostic script to verify data in cloud database
"""
from sqlalchemy import create_engine, text
from config import DatabaseConfig
from utils.db_utils import get_database_stats

def check_cloud_database():
    """Check cloud database for data"""
    print("="*60)
    print("CLOUD DATABASE DIAGNOSTICS")
    print("="*60)
    
    try:
        engine = create_engine(DatabaseConfig.get_connection_string(use_cloud=True))
        
        with engine.connect() as conn:
            # Check if tables exist
            print("\n1. Checking tables...")
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"   Tables found: {', '.join(tables)}")
            
            # Check fact_records
            if 'fact_records' in tables:
                print("\n2. Checking fact_records table...")
                result = conn.execute(text("SELECT COUNT(*) FROM fact_records"))
                total_records = result.fetchone()[0]
                print(f"   Total records: {total_records:,}")
                
                if total_records > 0:
                    # Records by month
                    result = conn.execute(text("""
                        SELECT data_month, COUNT(*) as count 
                        FROM fact_records 
                        GROUP BY data_month 
                        ORDER BY data_month DESC
                        LIMIT 10
                    """))
                    print("\n   Records by month:")
                    for row in result:
                        print(f"     {row[0]}: {row[1]:,} records")
                    
                    # Sample records
                    result = conn.execute(text("""
                        SELECT source_file, data_month, load_ts 
                        FROM fact_records 
                        ORDER BY load_ts DESC 
                        LIMIT 5
                    """))
                    print("\n   Recent records:")
                    for row in result:
                        print(f"     {row[0]} | {row[1]} | {row[2]}")
                else:
                    print("   WARNING: No records found in fact_records!")
            
            # Check audit_loads
            if 'audit_loads' in tables:
                print("\n3. Checking audit_loads table...")
                result = conn.execute(text("SELECT COUNT(*) FROM audit_loads"))
                total_loads = result.fetchone()[0]
                print(f"   Total loads: {total_loads:,}")
                
                if total_loads > 0:
                    result = conn.execute(text("""
                        SELECT 
                            load_id,
                            source_file,
                            status,
                            rows_read,
                            rows_inserted,
                            start_ts,
                            error_message
                        FROM audit_loads 
                        ORDER BY start_ts DESC 
                        LIMIT 10
                    """))
                    print("\n   Recent loads:")
                    for row in result:
                        status_icon = "[OK]" if row[2] == "COMPLETED" else "[FAIL]" if row[2] == "FAILED" else "[RUN]"
                        print(f"     {status_icon} Load {row[0]}: {row[1]}")
                        print(f"        Status: {row[2]} | Read: {row[3] or 0:,} | Inserted: {row[4] or 0:,} | Time: {row[5]}")
                        if row[6]:
                            print(f"        Error: {row[6][:100]}")
                else:
                    print("   WARNING: No loads found in audit_loads!")
            
            # Check processed_files
            if 'processed_files' in tables:
                print("\n4. Checking processed_files table...")
                result = conn.execute(text("SELECT COUNT(*) FROM processed_files"))
                total_files = result.fetchone()[0]
                print(f"   Total processed files: {total_files:,}")
                
                if total_files > 0:
                    result = conn.execute(text("""
                        SELECT file_name, source_type, data_month, last_processed_ts
                        FROM processed_files 
                        ORDER BY last_processed_ts DESC 
                        LIMIT 10
                    """))
                    print("\n   Recent processed files:")
                    for row in result:
                        print(f"     {row[0]} | {row[1]} | {row[2]} | {row[3]}")
                else:
                    print("   WARNING: No files marked as processed!")
        
        # Get stats using utility function
        print("\n5. Database Statistics:")
        print("-" * 60)
        stats = get_database_stats(use_cloud=True)
        print(f"   Total records: {stats['total_records']:,}")
        loads_total = stats['loads'].get('total', 0) or 0
        loads_completed = stats['loads'].get('completed', 0) or 0
        loads_failed = stats['loads'].get('failed', 0) or 0
        print(f"   Total loads: {loads_total:,} (Completed: {loads_completed:,}, Failed: {loads_failed:,})")
        print(f"   Processed files: {stats['processed_files']:,}")
        
        if stats['records_by_month']:
            print("\n   Records by month:")
            for month_data in stats['records_by_month']:
                print(f"     {month_data['month']}: {month_data['count']:,} records")
        
        print("\n" + "="*60)
        
        if stats['total_records'] == 0:
            print("WARNING: No data found in cloud database!")
            print("\nPossible reasons:")
            print("  1. Files were not loaded with --cloud flag")
            print("  2. Files failed to load (check audit_loads for errors)")
            print("  3. Files were already processed and skipped")
            print("\nTo load data:")
            print("  python bulk_load_all_script.py --path 'fending_data' --cloud")
            return False
        else:
            print("SUCCESS: Data found in cloud database!")
            return True
            
    except Exception as e:
        print(f"\nERROR: Error checking database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_cloud_database()

