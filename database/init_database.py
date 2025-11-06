"""
Database initialization script
Creates database schema and initializes tables
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config import DatabaseConfig
import os

def init_database(use_cloud=False):
    """
    Initialize database schema
    - Ensures the database exists
    - Applies all .sql files in the database directory (sorted by name)
    Args:
        use_cloud: If True, use cloud database; if False, use local
    """
    try:
        db_dir = Path(__file__).parent
        sql_files = sorted([p for p in db_dir.glob('*.sql')])
        if not sql_files:
            print("No .sql files found in database directory. Nothing to apply.")
        
        # Create engine (without database name for initial connection)
        conn_str = DatabaseConfig.get_connection_string(use_cloud)
        db_config = DatabaseConfig.CLOUD_DB if use_cloud else DatabaseConfig.LOCAL_DB
        db_name = db_config['database']
        base_conn_str = conn_str.rsplit('/', 1)[0]
        engine = create_engine(base_conn_str)
        
        with engine.connect() as conn:
            # Ensure database exists and select it
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.execute(text(f"USE `{db_name}`"))
            
            # Apply each SQL file
            for sql_path in sql_files:
                try:
                    print(f"Applying {sql_path.name}...")
                    sql_text = sql_path.read_text(encoding='utf-8')
                    statements = [s.strip() for s in sql_text.split(';') if s.strip()]
                    for stmt in statements:
                        try:
                            conn.execute(text(stmt))
                        except Exception as e:
                            # Show warning but continue
                            print(f"  Warning executing statement from {sql_path.name}: {e}")
                except Exception as file_err:
                    print(f"  Error reading {sql_path.name}: {file_err}")
            
            conn.commit()
        
        print(f"Database '{db_name}' initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize ETL database')
    parser.add_argument('--cloud', action='store_true', help='Use cloud database')
    args = parser.parse_args()
    
    init_database(use_cloud=args.cloud)

