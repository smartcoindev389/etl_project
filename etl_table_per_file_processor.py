"""
ETL Table Per File Processor
Processes CSV files by creating a separate table for each file (like Method 1)
Uses upload_reports table for tracking
"""
import pandas as pd
import hashlib
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.sql import quoted_name
from typing import Dict, Optional
from datetime import date
from time import perf_counter

from config import DatabaseConfig
from create_tables_from_csvs import (
    sanitize_table_name_from_file,
    build_column_mapping,
    generate_create_table_sql,
    _ensure_global_report_table
)
from create_tables_from_csvs import _identify_datetime_columns, _convert_datetime_columns

class ETLTablePerFileProcessor:
    """ETL processor that creates a separate table for each CSV file"""
    
    def __init__(self, use_cloud=False):
        """
        Initialize ETL processor
        Args:
            use_cloud: If True, use cloud database; if False, use local
        """
        self.use_cloud = use_cloud
        self.engine = create_engine(DatabaseConfig.get_connection_string(use_cloud))
        
    def calculate_path_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file path for uniqueness"""
        return hashlib.sha256(str(file_path).encode('utf-8')).hexdigest()
    
    def is_file_processed(self, file_path: Path) -> Optional[Dict]:
        """
        Check if file has already been processed
        Returns: None (files are not tracked)
        """
        return None
    
    def register_file_processing(self, file_path: Path, file_hash: str, 
                                 source_type: str, data_month, file_size: int):
        """Register or update file processing record (no-op, files are not tracked)"""
        pass
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def identify_source_type(self, file_path: Path) -> str:
        """Identify source type from file name"""
        filename_lower = file_path.name.lower()
        
        if 'flags_resumen_total_con_morosidad' in filename_lower:
            return 'flags_resumen_total_con_morosidad'
        elif 'flags_resumen_total_con_pagos_atc' in filename_lower:
            return 'flags_resumen_total_con_pagos_atc'
        elif 'flags_resumen_total_con_pagos_galicia' in filename_lower:
            return 'flags_resumen_total_con_pagos_galicia'
        elif 'resultados_analisis_completo_metadata_final_nps' in filename_lower:
            return 'resultados_analisis_completo_metadata_final_nps'
        elif 'nps' in filename_lower:
            return 'nps'
        elif 'flags' in filename_lower:
            return 'flags'
        elif 'resultados' in filename_lower:
            return 'resultados'
        else:
            return 'unknown'
    
    def extract_data_month_from_path(self, file_path: Path) -> Optional[date]:
        """
        Extract data month from file path
        Expected patterns: YYYY-MM, YYYY_MM, or month names
        """
        from datetime import date
        path_str = str(file_path)
        
        # Try to find date patterns in path
        import re
        
        # Pattern: YYYY-MM or YYYY_MM
        date_pattern = r'(\d{4})[-_](\d{2})'
        match = re.search(date_pattern, path_str)
        
        if match:
            year, month = match.groups()
            try:
                return date(int(year), int(month), 1)
            except ValueError:
                pass
        
        # Pattern: YYYYMM (e.g., 202508 for August 2025)
        date_pattern_compact = r'(\d{4})(\d{2})'
        matches = re.finditer(date_pattern_compact, path_str)
        for match in matches:
            year_str, month_str = match.groups()
            # Check if it looks like a date (year 2000-2099, month 01-12)
            year = int(year_str)
            month = int(month_str)
            if 2000 <= year <= 2099 and 1 <= month <= 12:
                try:
                    return date(year, month, 1)
                except ValueError:
                    pass
        
        # Pattern: month names (December 24, Agosto 25, etc.)
        month_names = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        path_lower = path_str.lower()
        for month_name, month_num in month_names.items():
            if month_name in path_lower:
                # Try to find year (2 or 4 digits)
                year_pattern = r'(\d{2,4})'
                year_matches = re.findall(year_pattern, path_str)
                for year_str in year_matches:
                    year = int(year_str)
                    if len(year_str) == 2:
                        year = 2000 + year if year < 50 else 1900 + year
                    if 2000 <= year <= 2099:
                        try:
                            return date(year, month_num, 1)
                        except ValueError:
                            pass
        
        return None
    
    def process_single_file(self, file_path: Path, data_month=None,
                           skip_duplicates: bool = True, 
                           sample_rows: int = 1000,
                           chunksize: int = 5000) -> Dict:
        """
        Process a single CSV file by creating a separate table for it
        Args:
            file_path: Path to CSV file
            data_month: Optional date object for data month
            skip_duplicates: If True, skip already processed files
            sample_rows: Rows to sample for schema inference
            chunksize: Rows per chunk for loading
        Returns:
            Dict with processing results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'success': False,
                'error': f'File not found: {file_path}'
            }
        
        # Check if already processed
        if skip_duplicates:
            processed = self.is_file_processed(file_path)
            if processed:
                return {
                    'success': True,
                    'skipped': True,
                    'message': f'File already processed: {file_path.name}'
                }
        
        source_type = self.identify_source_type(file_path)
        if data_month is None:
            # Try to extract from path or use current date
            data_month = datetime.now().date().replace(day=1)
        
        file_size = file_path.stat().st_size
        file_hash = self.calculate_file_hash(file_path)
        
        # Get table name from file name
        table_name = sanitize_table_name_from_file(file_path)
        
        # Prepare report metrics
        start = perf_counter()
        error_message = None
        total = 0
        
        try:
            print(f"Processing: {file_path.name}")
            print(f"  Table name: {table_name}")
            
            # Read sample to infer schema
            print("  Reading sample to infer schema...")
            df_sample = pd.read_csv(file_path, nrows=sample_rows, low_memory=False)
            print(f"  Sample loaded: {len(df_sample)} rows, {len(df_sample.columns)} cols")
            
            # Create table if not exists
            col_map = build_column_mapping(list(df_sample.columns))
            create_sql = generate_create_table_sql(df_sample, table_name, col_map)
            
            # Identify datetime columns for conversion
            datetime_cols = _identify_datetime_columns(df_sample, col_map)
            if datetime_cols:
                print(f"  Found {len(datetime_cols)} datetime columns to convert")
            
            # Create table and ensure report table exists
            with self.engine.begin() as conn:
                print("  Creating/recreating table to match current CSV structure...")
                conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
                conn.execute(text(create_sql))
                # Ensure global report table exists
                _ensure_global_report_table(conn)
            
            # Load full CSV in chunks
            print("  Loading full data in chunks...")
            for chunk in pd.read_csv(file_path, chunksize=chunksize, low_memory=False):
                try:
                    # Convert datetime columns to MySQL format
                    chunk = _convert_datetime_columns(chunk, datetime_cols)
                    # Use quoted_name to ensure pandas/sqlalchemy quote table with spaces/parens
                    name = quoted_name(table_name, quote=True)
                    # Rename columns to safe DB identifiers
                    chunk = chunk.rename(columns=col_map)
                    chunk.to_sql(name=name, con=self.engine, if_exists='append', index=False)
                    # Count chunk rows
                    inserted = len(chunk)
                    total += inserted
                    print(f"    +{inserted} rows (total {total})")
                except Exception as e:
                    error_message = str(e)
                    print(f"    ERROR in chunk: {error_message}")
                    raise  # Re-raise to be caught by outer try-except
            
            print(f"  Done: {total} rows inserted into `{table_name}`")
            
            # Register file as processed
            self.register_file_processing(
                file_path, file_hash, source_type, data_month, file_size
            )
            
            return {
                'success': True,
                'table_name': table_name,
                'rows_inserted': total,
                'data_month': data_month
            }
            
        except Exception as e:
            if error_message is None:
                error_message = str(e)
            print(f"  ERROR processing {file_path.name}: {error_message}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': error_message,
                'table_name': table_name if 'table_name' in locals() else None
            }
        finally:
            # Always write upload report (success or failure)
            duration = perf_counter() - start
            status = 'COMPLETED' if error_message is None else 'FAILED'
            with self.engine.begin() as conn:
                report_table = "upload_reports"
                conn.execute(
                    text(
                        f"""
                        INSERT INTO `{report_table}`
                        (table_name, source_file, file_size_bytes, rows_read, chunksize, sample_rows, status, error_message, completed_ts, duration_seconds)
                        VALUES (:table_name, :source_file, :file_size_bytes, :rows_read, :chunksize, :sample_rows, :status, :error_message, CURRENT_TIMESTAMP, :duration)
                        """
                    ),
                    {
                        "table_name": table_name if 'table_name' in locals() else 'unknown',
                        "source_file": str(file_path),
                        "file_size_bytes": int(file_size),
                        "rows_read": int(total),
                        "chunksize": int(chunksize),
                        "sample_rows": int(sample_rows),
                        "status": status,
                        "error_message": error_message[:1000] if error_message else None,  # Truncate long errors
                        "duration": float(round(duration, 2)),
                    },
                )

