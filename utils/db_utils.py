"""
Database utility functions
"""
from sqlalchemy import create_engine, text
from typing import Dict, List
from config import DatabaseConfig

def get_database_stats(use_cloud=False) -> Dict:
    """Get database statistics"""
    engine = create_engine(DatabaseConfig.get_connection_string(use_cloud))
    
    stats = {}
    
    with engine.connect() as conn:
        # Total records
        result = conn.execute(text("SELECT COUNT(*) as total FROM fact_records"))
        stats['total_records'] = result.fetchone()[0]
        
        # Records by month
        result = conn.execute(text("""
            SELECT data_month, COUNT(*) as count 
            FROM fact_records 
            GROUP BY data_month 
            ORDER BY data_month DESC
            LIMIT 12
        """))
        stats['records_by_month'] = [
            {'month': str(row[0]), 'count': row[1]} 
            for row in result
        ]
        
        # Total loads
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed
            FROM audit_loads
        """))
        row = result.fetchone()
        stats['loads'] = {
            'total': row[0],
            'completed': row[1],
            'failed': row[2]
        }
        
        # Processed files count
        result = conn.execute(text("SELECT COUNT(*) FROM processed_files"))
        stats['processed_files'] = result.fetchone()[0]
    
    return stats

def verify_data_integrity(use_cloud=False) -> Dict:
    """Verify data integrity checks"""
    engine = create_engine(DatabaseConfig.get_connection_string(use_cloud))
    
    checks = {}
    
    with engine.connect() as conn:
        # Check for orphaned records (load_id not in audit_loads)
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM fact_records f
            LEFT JOIN audit_loads a ON f.load_id = a.load_id
            WHERE f.load_id IS NOT NULL AND a.load_id IS NULL
        """))
        checks['orphaned_records'] = result.fetchone()[0]
        
        # Check for records without data_month
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM fact_records 
            WHERE data_month IS NULL
        """))
        checks['records_without_month'] = result.fetchone()[0]
        
        # Check for duplicate file paths in processed_files
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM processed_files p1
            WHERE EXISTS (
                SELECT 1 FROM processed_files p2
                WHERE p2.file_path = p1.file_path
                AND p2.file_id != p1.file_id
            )
        """))
        checks['duplicate_file_paths'] = result.fetchone()[0]
    
    checks['all_passed'] = all(v == 0 for v in checks.values())
    
    return checks

