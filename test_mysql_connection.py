"""
Test MySQL Connection Script
Tests connection to local or cloud MySQL database
"""
from sqlalchemy import create_engine, text
import sys
from pathlib import Path

# Add config to path
sys.path.append(str(Path(__file__).parent))

from config import DatabaseConfig
import pandas as pd

def test_connection(use_cloud=False):
    """Test database connection"""
    try:
        conn_str = DatabaseConfig.get_connection_string(use_cloud)
        db_type = "Cloud" if use_cloud else "Local"
        
        print(f"Testing {db_type} MySQL connection...")
        print(f"   Connection string: {conn_str.split('@')[0]}@...")
        
        engine = create_engine(conn_str)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"   Connected successfully!")
            print(f"   MySQL Version: {version}")
            
            # Check if database exists
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"   Database: {db_name}")
            
            # Check if tables exist
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """))
            table_count = result.fetchone()[0]
            print(f"   Tables found: {table_count}")
            
            # Test insert (if fact_records exists)
            if table_count > 0:
                try:
                    # Check what columns exist in fact_records
                    result = conn.execute(text("""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = DATABASE() 
                        AND TABLE_NAME = 'fact_records'
                        AND COLUMN_NAME NOT IN ('record_id', 'data_year', 'data_month_num')
                        ORDER BY ORDINAL_POSITION
                    """))
                    columns = [row[0] for row in result]
                    
                    if not columns:
                        print(f"WARNING: fact_records table exists but has no columns (might be empty schema)")
                        return True
                    
                    # Create minimal test data with only required columns
                    # Find required columns (NOT NULL columns)
                    result = conn.execute(text("""
                        SELECT COLUMN_NAME, IS_NULLABLE, DATA_TYPE
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = DATABASE() 
                        AND TABLE_NAME = 'fact_records'
                        AND COLUMN_NAME NOT IN ('record_id', 'data_year', 'data_month_num')
                        AND IS_NULLABLE = 'NO'
                        ORDER BY ORDINAL_POSITION
                    """))
                    required_cols = {row[0]: row[2] for row in result}
                    
                    # Build test data with only required columns
                    test_data = {}
                    datetime_cols_to_convert = []
                    
                    for col, data_type in required_cols.items():
                        if col == 'source_file':
                            test_data[col] = ['test_connection.csv']
                        elif col == 'data_month':
                            test_data[col] = ['2025-01-01']
                        elif 'DATETIME' in data_type:
                            # Only convert actual datetime columns (fecha_inicio, fecha_fin, fecha_procesamiento)
                            if 'fecha' in col.lower() or 'timestamp' in col.lower():
                                test_data[col] = ['2025-01-01 00:00:00']
                                datetime_cols_to_convert.append(col)
                            else:
                                test_data[col] = ['2025-01-01 00:00:00']
                                datetime_cols_to_convert.append(col)
                        elif 'DECIMAL' in data_type or 'INT' in data_type or 'TINYINT' in data_type:
                            test_data[col] = [0]
                        elif 'VARCHAR' in data_type:
                            test_data[col] = ['TEST']
                        else:
                            test_data[col] = ['TEST']
                    
                    if not test_data:
                        print(f"WARNING: No required columns found for test insert")
                        return True
                    
                    df = pd.DataFrame(test_data)
                    
                    # Convert date columns
                    if 'data_month' in df.columns:
                        df['data_month'] = pd.to_datetime(df['data_month']).dt.date
                    
                    # Convert only actual datetime columns
                    for col in datetime_cols_to_convert:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col])
                    
                    df.to_sql("fact_records", engine, if_exists="append", index=False)
                    print(f"SUCCESS: Test insert successful!")
                    
                    # Clean up test record
                    conn.execute(text("""
                        DELETE FROM fact_records 
                        WHERE source_file = 'test_connection.csv'
                    """))
                    conn.commit()
                    print(f"SUCCESS: Test record cleaned up")
                    
                except Exception as e:
                    print(f"WARNING: Test insert failed: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Connection failed: {str(e)}")
        print(f"\nTroubleshooting:")
        print(f"   1. Check .env file configuration")
        print(f"   2. Verify database credentials")
        print(f"   3. Ensure database exists")
        print(f"   4. Check network/firewall settings (for cloud)")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test MySQL Connection')
    parser.add_argument('--cloud', action='store_true', help='Test cloud database')
    args = parser.parse_args()
    
    success = test_connection(use_cloud=args.cloud)
    sys.exit(0 if success else 1)
