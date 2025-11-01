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
    Args:
        use_cloud: If True, use cloud database; if False, use local
    """
    try:
        # Try to use generated schema first, fallback to base schema
        schema_file = Path(__file__).parent / 'schema_resultados.sql'
        if not schema_file.exists():
            schema_file = Path(__file__).parent / 'schema.sql'
        
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Create engine (without database name for initial connection)
        conn_str = DatabaseConfig.get_connection_string(use_cloud)
        
        # Extract database name to create it first
        db_config = DatabaseConfig.CLOUD_DB if use_cloud else DatabaseConfig.LOCAL_DB
        db_name = db_config['database']
        
        # Create connection without database
        base_conn_str = conn_str.rsplit('/', 1)[0]
        engine = create_engine(base_conn_str)
        
        # Execute schema
        with engine.connect() as conn:
            # Split SQL by semicolon and execute each statement
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        # Ignore errors for "IF NOT EXISTS" statements that might fail
                        if "already exists" not in str(e).lower():
                            print(f"Warning: {str(e)}")
            
            conn.commit()
        
        print(f"✅ Database '{db_name}' initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize ETL database')
    parser.add_argument('--cloud', action='store_true', help='Use cloud database')
    args = parser.parse_args()
    
    init_database(use_cloud=args.cloud)

