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
        
        print(f"🔌 Testing {db_type} MySQL connection...")
        print(f"   Connection string: {conn_str.split('@')[0]}@...")
        
        engine = create_engine(conn_str)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
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
                    df = pd.DataFrame({
                        "field1": ["TEST"],
                        "field2": ["CONNECTION"],
                        "source_file": ["test_connection.csv"],
                        "data_month": ["2025-01-01"]
                    })
                    
                    df.to_sql("fact_records", engine, if_exists="append", index=False)
                    print(f"✅ Test insert successful!")
                    
                    # Clean up test record
                    conn.execute(text("""
                        DELETE FROM fact_records 
                        WHERE source_file = 'test_connection.csv'
                    """))
                    conn.commit()
                    print(f"✅ Test record cleaned up")
                    
                except Exception as e:
                    print(f"⚠️  Test insert failed (table might not exist yet): {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print(f"\n💡 Troubleshooting:")
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
