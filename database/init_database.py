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

def create_system_tables(conn):
    """
    Create system tables required for ETL processing
    These tables are created programmatically to ensure they always match the code
    """
    print("Creating system tables...")
    
    # Table: processed_files
    # Tracks which files have been processed to prevent duplicate processing
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS `processed_files` (
          `file_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
          `file_path` VARCHAR(2000) NOT NULL,
          `file_path_hash` VARCHAR(64) NOT NULL COMMENT 'SHA256 hash of file_path for uniqueness',
          `file_name` VARCHAR(500) NOT NULL,
          `file_hash` VARCHAR(64) NOT NULL COMMENT 'SHA256 hash of file content',
          `file_size_bytes` BIGINT NOT NULL,
          `source_type` VARCHAR(100) NOT NULL COMMENT 'Type of source: flags, resultados, nps, etc.',
          `data_month` DATE NOT NULL COMMENT 'Month this data represents (YYYY-MM-01)',
          `last_processed_ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          `first_processed_ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          `process_count` INT DEFAULT 1 COMMENT 'Number of times this file has been processed',
          UNIQUE KEY `uk_file_path_hash` (`file_path_hash`),
          INDEX `idx_file_hash` (`file_hash`),
          INDEX `idx_data_month` (`data_month`),
          INDEX `idx_source_type` (`source_type`),
          INDEX `idx_file_name` (`file_name`),
          INDEX `idx_file_path` (`file_path`(255))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))
    print("  [OK] processed_files table created")
    
    # Note: audit_loads and fact_records are only needed for:
    # - etl_monthly_processor.py (Method 3)
    # - etl_merge_processor.py
    # They are NOT needed for Method 2 (bulk_load_all_script.py) which uses upload_reports instead
    # Uncomment below if you need these tables for other methods:
    
    # # Table: audit_loads
    # # Tracks each ETL load operation for auditing and debugging (only for etl_monthly_processor)
    # conn.execute(text("""
    #     CREATE TABLE IF NOT EXISTS `audit_loads` (
    #       `load_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    #       `source_file` VARCHAR(500) NOT NULL,
    #       `source_type` VARCHAR(100) NOT NULL,
    #       `file_path` VARCHAR(2000) NOT NULL,
    #       `file_size_bytes` BIGINT NOT NULL,
    #       `data_month` DATE NOT NULL,
    #       `data_year` INT GENERATED ALWAYS AS (YEAR(data_month)) STORED,
    #       `data_month_num` INT GENERATED ALWAYS AS (MONTH(data_month)) STORED,
    #       `status` VARCHAR(50) NOT NULL DEFAULT 'RUNNING' COMMENT 'RUNNING, COMPLETED, FAILED',
    #       `rows_read` INT DEFAULT 0,
    #       `rows_valid` INT DEFAULT 0,
    #       `rows_inserted` INT DEFAULT 0,
    #       `rows_skipped` INT DEFAULT 0,
    #       `start_ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    #       `end_ts` TIMESTAMP NULL,
    #       `processing_duration_seconds` INT GENERATED ALWAYS AS (
    #         CASE 
    #           WHEN end_ts IS NOT NULL THEN TIMESTAMPDIFF(SECOND, start_ts, end_ts)
    #           ELSE NULL
    #         END
    #       ) STORED,
    #       `error_message` VARCHAR(500) NULL,
    #       `error_details` TEXT NULL,
    #       INDEX `idx_data_month` (`data_month`),
    #       INDEX `idx_status` (`status`),
    #       INDEX `idx_source_type` (`source_type`),
    #       INDEX `idx_start_ts` (`start_ts`)
    #     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    # """))
    # print("  [OK] audit_loads table created")
    # 
    # # Table: fact_records
    # # Base structure for fact_records table (only for etl_monthly_processor)
    # # Note: The actual data columns are added dynamically based on CSV files
    # conn.execute(text("""
    #     CREATE TABLE IF NOT EXISTS `fact_records` (
    #       `record_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    #       `source_file` VARCHAR(500) NOT NULL COMMENT 'Source CSV file name',
    #       `data_month` DATE NOT NULL COMMENT 'Month this record represents',
    #       `data_year` INT GENERATED ALWAYS AS (YEAR(data_month)) STORED,
    #       `data_month_num` INT GENERATED ALWAYS AS (MONTH(data_month)) STORED,
    #       `load_id` BIGINT NOT NULL COMMENT 'Reference to audit_loads.load_id',
    #       `load_ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'When this record was loaded',
    #       INDEX `idx_data_month` (`data_month`),
    #       INDEX `idx_load_id` (`load_id`),
    #       INDEX `idx_source_file` (`source_file`),
    #       FOREIGN KEY (`load_id`) REFERENCES `audit_loads`(`load_id`) ON DELETE RESTRICT
    #     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    # """))
    # print("  [OK] fact_records base table created")
    
    # Table: monthly_summary (optional, for statistics)
    # Provides monthly aggregation statistics
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS `monthly_summary` (
          `summary_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
          `data_month` DATE NOT NULL,
          `data_year` INT GENERATED ALWAYS AS (YEAR(data_month)) STORED,
          `data_month_num` INT GENERATED ALWAYS AS (MONTH(data_month)) STORED,
          `source_type` VARCHAR(100) NOT NULL,
          `total_records` BIGINT DEFAULT 0,
          `total_files` INT DEFAULT 0,
          `last_updated_ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY `idx_month_source` (`data_month`, `source_type`),
          INDEX `idx_data_month` (`data_month`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))
    print("  [OK] monthly_summary table created")
    
    # Table: upload_reports (for Method 1 and Method 2)
    # Tracks upload operations for each table/file
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS `upload_reports` (
          `report_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
          `table_name` VARCHAR(255) NOT NULL,
          `source_file` VARCHAR(1000) NOT NULL,
          `file_size_bytes` BIGINT,
          `rows_read` BIGINT DEFAULT 0,
          `chunksize` INT,
          `sample_rows` INT,
          `status` VARCHAR(50) DEFAULT 'COMPLETED',
          `error_message` TEXT,
          `started_ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          `completed_ts` TIMESTAMP NULL,
          `duration_seconds` DECIMAL(12,2),
          INDEX `idx_table_name` (`table_name`),
          INDEX `idx_status` (`status`),
          INDEX `idx_started_ts` (`started_ts`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))
    print("  [OK] upload_reports table created")

def init_database(use_cloud=False):
    """
    Initialize database schema
    - Ensures the database exists
    - Creates system tables programmatically
    - Applies all .sql files in the database directory (sorted by name)
    Args:
        use_cloud: If True, use cloud database; if False, use local
    """
    try:
        db_dir = Path(__file__).parent
        sql_files = sorted([p for p in db_dir.glob('*.sql')])
        
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
            
            # Create system tables programmatically
            create_system_tables(conn)
            
            # Apply each SQL file (for data table schemas)
            if sql_files:
                print("\nApplying data table SQL files...")
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
            else:
                print("\nNo data table SQL files found. Data tables will be created dynamically from CSV files.")
            
            conn.commit()
        
        print(f"\nDatabase '{db_name}' initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize ETL database')
    parser.add_argument('--cloud', action='store_true', help='Use cloud database')
    args = parser.parse_args()
    
    init_database(use_cloud=args.cloud)

