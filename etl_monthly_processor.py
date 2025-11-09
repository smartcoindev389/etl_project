"""
ETL Monthly Processor
Processes CSV files monthly with historization support
"""
import pandas as pd
import hashlib
from pathlib import Path
from datetime import datetime, date
from sqlalchemy import create_engine, text
import sys
from typing import List, Dict, Optional

from config import DatabaseConfig, ETLConfig

class ETLMonthlyProcessor:
    """Main ETL processor for monthly CSV files"""
    
    def __init__(self, use_cloud=False):
        """
        Initialize ETL processor
        Args:
            use_cloud: If True, use cloud database; if False, use local
        """
        self.use_cloud = use_cloud
        self.engine = create_engine(DatabaseConfig.get_connection_string(use_cloud))
        self.config = ETLConfig()
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def calculate_path_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file path for uniqueness"""
        return hashlib.sha256(str(file_path).encode('utf-8')).hexdigest()
    
    def is_file_processed(self, file_path: Path) -> Optional[Dict]:
        """
        Check if file has already been processed
        Returns: Dict with file info if processed, None otherwise
        """
        path_hash = self.calculate_path_hash(file_path)
        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM processed_files WHERE file_path_hash = :path_hash"),
                {"path_hash": path_hash}
            ).fetchone()
            
            if result:
                return dict(result._mapping)
        return None
    
    def register_file_processing(self, file_path: Path, file_hash: str, 
                                 source_type: str, data_month: date,
                                 file_size: int):
        """Register or update file processing record"""
        path_hash = self.calculate_path_hash(file_path)
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO processed_files 
                    (file_path, file_path_hash, file_name, file_hash, file_size_bytes, source_type, data_month)
                    VALUES (:path, :path_hash, :name, :hash, :size, :type, :month)
                    ON DUPLICATE KEY UPDATE
                        last_processed_ts = CURRENT_TIMESTAMP,
                        process_count = process_count + 1
                """),
                {
                    "path": str(file_path),
                    "path_hash": path_hash,
                    "name": file_path.name,
                    "hash": file_hash,
                    "size": file_size,
                    "type": source_type,
                    "month": data_month
                }
            )
            conn.commit()
    
    def create_load_record(self, source_file: str, source_type: str, 
                          file_path: str, data_month: date,
                          file_size: int) -> int:
        """Create audit load record and return load_id"""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO audit_loads 
                    (source_file, source_type, file_path, file_size_bytes, 
                     data_month, status)
                    VALUES (:file, :type, :path, :size, :month, 'RUNNING')
                """),
                {
                    "file": source_file,
                    "type": source_type,
                    "path": file_path,
                    "size": file_size,
                    "month": data_month
                }
            )
            conn.commit()
            return result.lastrowid
    
    def update_load_record(self, load_id: int, status: str, 
                          rows_read: int = 0, rows_valid: int = 0,
                          rows_inserted: int = 0, rows_skipped: int = 0,
                          error_message: str = None, error_details: str = None):
        """Update audit load record with results"""
        # Truncate error messages to fit in database columns
        error_msg_truncated = error_message[:500] if error_message else None
        error_details_truncated = error_details[:60000] if error_details else None
        
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    UPDATE audit_loads 
                    SET status = :status,
                        rows_read = :read,
                        rows_valid = :valid,
                        rows_inserted = :inserted,
                        rows_skipped = :skipped,
                        end_ts = CURRENT_TIMESTAMP,
                        error_message = :error_msg,
                        error_details = :error_details
                    WHERE load_id = :load_id
                """),
                {
                    "status": status,
                    "read": rows_read,
                    "valid": rows_valid,
                    "inserted": rows_inserted,
                    "skipped": rows_skipped,
                    "error_msg": error_msg_truncated,
                    "error_details": error_details_truncated,
                    "load_id": load_id
                }
            )
            conn.commit()
    
    def extract_data_month_from_path(self, file_path: Path) -> Optional[date]:
        """
        Extract data month from file path
        Expected patterns: YYYY-MM, YYYY_MM, or month names
        """
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
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        for month_name, month_num in month_names.items():
            if month_name.lower() in path_str.lower():
                # Try to extract year (24, 25, etc. -> 2024, 2025)
                year_pattern = rf'{month_name}[^\d]*(\d{{2}})'
                year_match = re.search(year_pattern, path_str, re.IGNORECASE)
                if year_match:
                    year_short = int(year_match.group(1))
                    year = 2000 + year_short if year_short < 50 else 1900 + year_short
                    return date(year, month_num, 1)
        
        return None
    
    def identify_source_type(self, file_path: Path) -> str:
        """Identify source type from filename"""
        filename_lower = file_path.name.lower()
        
        # Check for merged results with metadata and NPS (already processed)
        if 'resultados_analisis_completo' in filename_lower and 'metadata_final' in filename_lower and 'nps' in filename_lower:
            return 'resultados_analisis_completo_metadata_final_nps'
        # Check for flags files with payments ATC
        elif 'flags_resumen_total_con_pagos_atc' in filename_lower or 'flags' in filename_lower and 'pagos_atc' in filename_lower:
            return 'flags_resumen_total_con_pagos_atc'
        # Check for flags files with payments Galicia
        elif 'flags_resumen_total_con_pagos_galicia' in filename_lower or 'flags' in filename_lower and 'pagos_galicia' in filename_lower:
            return 'flags_resumen_total_con_pagos_galicia'
        # Check for flags files with morosidad (delinquency)
        elif 'flags_resumen_total_con_morosidad' in filename_lower or 'flags' in filename_lower and 'morosidad' in filename_lower:
            return 'flags_resumen_total_con_morosidad'
        # Check for original resultados files
        elif 'resultados_analisis_completo' in filename_lower or 'resultados' in filename_lower:
            return 'resultados_analisis_completo'
        elif 'metadata' in filename_lower:
            return 'metadata'
        elif 'speech_analytics' in filename_lower or 'speech' in filename_lower:
            return 'speech_analytics'
        else:
            return 'unknown'
    
    def transform_data(self, df: pd.DataFrame, source_type: str) -> pd.DataFrame:
        """
        Transform data according to source type
        Add common transformations here
        """
        # Make a copy to avoid modifying original
        df_transformed = df.copy()
        
        # Add source type column
        df_transformed['source_type'] = source_type
        
        # Convert datetime columns from ISO format to MySQL DATETIME format
        # Only convert actual datetime columns (not flags)
        datetime_column_patterns = ['fecha_inicio', 'fecha_fin', 'fecha_procesamiento', 'timestamp', 'created_at', 'updated_at']
        required_datetime_cols = []
        
        for col in df_transformed.columns:
            col_lower = col.lower()
            # Skip flag columns (flg, flag) even if they contain datetime keywords
            if 'flg' in col_lower or 'flag' in col_lower:
                continue
            # Only convert specific datetime columns
            if any(pattern in col_lower for pattern in datetime_column_patterns):
                try:
                    # Store columns that are required (fecha_inicio, fecha_fin)
                    if col_lower in ['fecha_inicio', 'fecha_fin']:
                        required_datetime_cols.append(col)
                    
                    # Try to parse ISO format datetime strings
                    df_transformed[col] = pd.to_datetime(
                        df_transformed[col], 
                        errors='coerce',
                        format='mixed'  # Try multiple formats
                    )
                    # Convert to MySQL format (remove timezone if present)
                    if pd.api.types.is_datetime64_any_dtype(df_transformed[col]):
                        # If timezone-aware, convert to naive datetime
                        if df_transformed[col].dt.tz is not None:
                            df_transformed[col] = df_transformed[col].dt.tz_localize(None)
                except Exception:
                    # If conversion fails, leave as is
                    pass
        
        # Filter out rows where required datetime columns are NULL
        if required_datetime_cols:
            initial_count = len(df_transformed)
            for col in required_datetime_cols:
                if col in df_transformed.columns:
                    # Remove rows where this datetime column is NULL/NaT
                    df_transformed = df_transformed[df_transformed[col].notna()]
            filtered_count = len(df_transformed)
            if initial_count != filtered_count:
                print(f"  Filtered out {initial_count - filtered_count} rows with NULL datetime values")
        
        # Basic data cleaning
        # Remove leading/trailing whitespace from string columns (but skip datetime columns)
        datetime_cols_set = set()
        for col in df_transformed.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in datetime_column_patterns):
                if 'flg' not in col_lower and 'flag' not in col_lower:
                    datetime_cols_set.add(col)
        
        for col in df_transformed.select_dtypes(include=['object']).columns:
            # Skip datetime columns from string conversion
            if col not in datetime_cols_set:
                df_transformed[col] = df_transformed[col].astype(str).str.strip()
        
        # Replace 'nan' strings with actual NaN
        df_transformed = df_transformed.replace('nan', pd.NA)
        df_transformed = df_transformed.replace('None', pd.NA)
        
        return df_transformed
    
    def _infer_mysql_type(self, series: pd.Series, col_name: str) -> str:
        """Infer MySQL data type from pandas Series"""
        # Check for flags (boolean-like)
        if 'flg' in col_name.lower() or 'flag' in col_name.lower():
            return 'TINYINT'
        
        # Check data type
        if series.dtype == 'bool' or series.dtype == 'boolean':
            return 'TINYINT'
        elif series.dtype in ['int64', 'int32', 'Int64', 'Int32']:
            return 'BIGINT'
        elif series.dtype in ['float64', 'float32', 'Float64', 'Float32']:
            return 'DECIMAL(18, 4)'
        elif 'datetime' in str(series.dtype).lower() or 'timestamp' in str(series.dtype).lower():
            return 'DATETIME'
        else:
            # String type - check max length
            max_len = series.astype(str).str.len().max()
            if pd.isna(max_len) or max_len <= 255:
                return 'VARCHAR(255)'
            elif max_len <= 500:
                return 'VARCHAR(500)'
            elif max_len <= 1000:
                return 'VARCHAR(1000)'
            else:
                return 'TEXT'
    
    def _clean_column_name(self, col_name: str) -> str:
        """Clean column name for MySQL compatibility"""
        safe_col = col_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        safe_col = safe_col.replace('[', '').replace(']', '').replace('.', '_')
        safe_col = safe_col.replace('{', '').replace('}', '').replace('/', '_')
        safe_col = safe_col.replace('\\', '_').replace(':', '_').replace(';', '_')
        safe_col = safe_col.replace(',', '_').replace('?', '_').replace('!', '_')
        # Remove multiple consecutive underscores
        while '__' in safe_col:
            safe_col = safe_col.replace('__', '_')
        # Remove leading/trailing underscores
        safe_col = safe_col.strip('_')
        return safe_col
    
    def _ensure_columns_exist(self, df: pd.DataFrame, conn):
        """Ensure all CSV columns exist in fact_records table, add them if missing"""
        # Get existing columns
        result = conn.execute(text("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'fact_records'
        """))
        existing_columns = {row[0] for row in result}
        
        # Metadata columns that should not be added
        metadata_cols = {'record_id', 'source_file', 'data_month', 'data_year', 
                        'data_month_num', 'load_id', 'load_ts'}
        
        # Find columns that need to be added
        columns_to_add = []
        for col in df.columns:
            # Clean column name for MySQL
            safe_col = self._clean_column_name(col)
            
            # Skip if already exists or is metadata
            if safe_col in existing_columns or safe_col in metadata_cols:
                continue
            
            # Infer MySQL type
            mysql_type = self._infer_mysql_type(df[col], col)
            
            # Check if nullable
            null_count = df[col].isna().sum()
            nullable = "NULL" if null_count > 0 else "NULL"  # Allow NULL for flexibility
            
            columns_to_add.append((col, safe_col, mysql_type, nullable))
        
        # Add missing columns
        if columns_to_add:
            print(f"  Adding {len(columns_to_add)} new columns to fact_records table...")
            for orig_col, safe_col, mysql_type, nullable in columns_to_add:
                try:
                    alter_sql = f"ALTER TABLE `fact_records` ADD COLUMN `{safe_col}` {mysql_type} {nullable}"
                    conn.execute(text(alter_sql))
                    print(f"    Added column: {safe_col} ({mysql_type}) from '{orig_col}'")
                except Exception as e:
                    # Column might already exist or other error
                    if 'Duplicate column name' not in str(e):
                        print(f"    Warning: Could not add column {safe_col}: {e}")
            conn.commit()
    
    def load_data_to_db(self, df: pd.DataFrame, load_id: int, 
                        source_file: str, data_month: date):
        """Load transformed data to database"""
        if df.empty:
            return 0
        
        # Ensure all columns exist in the database
        with self.engine.connect() as conn:
            self._ensure_columns_exist(df, conn)
            
            # Get list of columns that exist in the database and their requirements
            result = conn.execute(text("""
                SELECT COLUMN_NAME, IS_NULLABLE, DATA_TYPE, COLUMN_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'fact_records'
                AND COLUMN_NAME NOT IN ('record_id', 'data_year', 'data_month_num', 'load_ts')
            """))
            db_column_info = {row[0]: {'nullable': row[1] == 'YES', 'data_type': row[2], 'column_type': row[3]} 
                             for row in result}
            db_columns = list(db_column_info.keys())
        
        # Map CSV columns to database columns (handle name differences)
        metadata_cols = ['source_file', 'data_month', 'load_id']
        available_cols = []
        col_mapping = {}
        
        for col in df.columns:
            # Clean column name for MySQL
            safe_col = self._clean_column_name(col)
            
            if safe_col in db_columns:
                available_cols.append(col)
                col_mapping[col] = safe_col
            elif col in db_columns:
                available_cols.append(col)
                col_mapping[col] = col
        
        if not available_cols:
            print(f"Warning: No matching columns found between CSV and database")
            print(f"CSV columns: {list(df.columns)[:10]}...")
            print(f"DB columns: {db_columns[:10]}...")
            return 0
        
        # Create filtered dataframe with only matching columns
        df_filtered = df[available_cols].copy()
        
        # Rename columns to match database column names
        if col_mapping:
            df_filtered = df_filtered.rename(columns=col_mapping)
        
        # Add metadata columns
        df_filtered['source_file'] = source_file
        df_filtered['data_month'] = data_month
        df_filtered['load_id'] = load_id
        
        # Check for missing required columns and add defaults
        missing_required = []
        for col_name, col_info in db_column_info.items():
            if col_name not in df_filtered.columns and not col_info['nullable']:
                missing_required.append((col_name, col_info))
        
        if missing_required:
            print(f"  Adding {len(missing_required)} missing required columns with default values")
            for col_name, col_info in missing_required:
                data_type = col_info['data_type'].upper()
                col_type_lower = col_info['column_type'].lower()
                
                # Check for integer types (including variations)
                if ('INT' in data_type or 'INTEGER' in data_type) or ('flg' in col_name.lower() or 'flag' in col_name.lower()):
                    df_filtered[col_name] = 0
                elif 'DATETIME' in data_type or 'datetime' in col_type_lower or 'timestamp' in col_type_lower:
                    # For fecha_procesamiento, use current timestamp; for others, use data_month
                    if 'procesamiento' in col_name.lower():
                        df_filtered[col_name] = pd.Timestamp.now()
                    else:
                        df_filtered[col_name] = pd.Timestamp(data_month)
                elif data_type in ['DECIMAL', 'DOUBLE', 'FLOAT', 'NUMERIC']:
                    df_filtered[col_name] = 0.0
                elif data_type in ['VARCHAR', 'TEXT', 'CHAR']:
                    # For nombre_archivo, use source_file name
                    if 'nombre_archivo' in col_name.lower() or 'nombre' in col_name.lower():
                        df_filtered[col_name] = Path(source_file).name
                    else:
                        df_filtered[col_name] = ''
                else:
                    # Default to empty string for other types
                    df_filtered[col_name] = ''
        
        print(f"  Filtered to {len(available_cols)} matching columns (from {len(df.columns)} CSV columns)")
        if missing_required:
            print(f"  Added {len(missing_required)} required columns with defaults")
        
        try:
            # Use to_sql with chunking for large datasets
            # Process in smaller chunks to avoid SQL statement size limits
            chunk_size = min(self.config.BATCH_SIZE, 100)  # Small chunks to avoid SQL size limits
            
            total_rows = 0
            num_chunks = (len(df_filtered) + chunk_size - 1) // chunk_size
            
            for i in range(0, len(df_filtered), chunk_size):
                chunk = df_filtered.iloc[i:i+chunk_size]
                chunk_num = i // chunk_size + 1
                
                try:
                    # Use smaller chunksize without method='multi' to avoid SQL statement size limits
                    rows = chunk.to_sql(
                        'fact_records',
                        self.engine,
                        if_exists='append',
                        index=False,
                        chunksize=min(len(chunk), 50)  # Very small chunks to avoid SQL size limits
                    )
                    total_rows += len(chunk) if not isinstance(rows, int) else rows
                    print(f"  Loaded chunk {chunk_num}/{num_chunks}: {len(chunk)} rows")
                except Exception as chunk_error:
                    print(f"  Error in chunk {chunk_num}: {str(chunk_error)}")
                    # Try to reconnect
                    self.engine.dispose()
                    self.engine = create_engine(
                        DatabaseConfig.get_connection_string(self.use_cloud),
                        pool_pre_ping=True,
                        pool_recycle=3600,
                        connect_args={
                            'connect_timeout': 60,
                            'read_timeout': 600,
                            'write_timeout': 600
                        }
                    )
                    # Retry once
                    try:
                        rows = chunk.to_sql(
                            'fact_records',
                            self.engine,
                            if_exists='append',
                            index=False,
                            chunksize=min(len(chunk), 50)  # Small chunks to avoid SQL size limits
                        )
                        total_rows += len(chunk) if not isinstance(rows, int) else rows
                        print(f"  Retry successful: chunk {chunk_num} loaded")
                    except Exception as retry_error:
                        print(f"  Retry failed for chunk {chunk_num}: {str(retry_error)}")
                        raise retry_error
            
            rows_inserted = total_rows
            return rows_inserted
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise
    
    def process_single_file(self, file_path: Path, data_month: Optional[date] = None,
                           skip_duplicates: bool = True) -> Dict:
        """
        Process a single CSV file
        Returns: Dict with processing results
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
        
        # Extract metadata
        source_type = self.identify_source_type(file_path)
        
        if data_month is None:
            data_month = self.extract_data_month_from_path(file_path)
            if data_month is None:
                data_month = date.today().replace(day=1)  # Default to current month
        
        file_size = file_path.stat().st_size
        file_hash = self.calculate_file_hash(file_path)
        
        # Create load record
        load_id = self.create_load_record(
            source_file=file_path.name,
            source_type=source_type,
            file_path=str(file_path),
            data_month=data_month,
            file_size=file_size
        )
        
        try:
            # Extract
            print(f"Reading file: {file_path.name}")
            df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
            rows_read = len(df)
            
            # Transform
            print(f"Transforming data...")
            df_transformed = self.transform_data(df, source_type)
            rows_valid = len(df_transformed)
            
            # Load
            print(f"Loading data to database...")
            rows_inserted = self.load_data_to_db(
                df_transformed, load_id, file_path.name, data_month
            )
            
            # Register file
            self.register_file_processing(
                file_path, file_hash, source_type, data_month, file_size
            )
            
            # Update load record
            self.update_load_record(
                load_id, 'COMPLETED',
                rows_read=rows_read,
                rows_valid=rows_valid,
                rows_inserted=rows_inserted,
                rows_skipped=rows_read - rows_valid
            )
            
            print(f"Successfully processed: {file_path.name} ({rows_inserted} rows)")
            
            return {
                'success': True,
                'load_id': load_id,
                'rows_read': rows_read,
                'rows_inserted': rows_inserted,
                'data_month': data_month
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error processing {file_path.name}: {error_msg}")
            
            # Truncate error messages to fit in database columns
            # TEXT can store up to 65,535 bytes, but we'll limit to 60KB to be safe
            error_msg_truncated = error_msg[:500] if error_msg else None
            error_details_truncated = str(e)[:60000] if str(e) else None
            
            self.update_load_record(
                load_id, 'FAILED',
                rows_read=rows_read if 'rows_read' in locals() else 0,
                error_message=error_msg_truncated,
                error_details=error_details_truncated
            )
            
            return {
                'success': False,
                'load_id': load_id,
                'error': error_msg
            }
    
    def process_monthly_batch(self, data_month: date, base_path: Path = None) -> Dict:
        """
        Process all CSV files for a specific month
        Args:
            data_month: Date object representing the month (day=1)
            base_path: Base path to search for CSV files
        """
        if base_path is None:
            base_path = Path(self.config.CSV_BASE_PATH)
        
        base_path = Path(base_path)
        
        if not base_path.exists():
            return {
                'success': False,
                'error': f'Base path not found: {base_path}'
            }
        
        print(f"Processing month: {data_month.strftime('%Y-%m')}")
        
        # Find all CSV files in the month's directory
        month_str = data_month.strftime('%Y-%m')
        month_dir = base_path / month_str
        
        if not month_dir.exists():
            # Try alternative patterns
            month_patterns = [
                data_month.strftime('%Y_%m'),
                data_month.strftime('%Y-%m'),
                f"{data_month.strftime('%B')} {data_month.strftime('%y')}".lower()
            ]
            
            for pattern in month_patterns:
                potential_dir = base_path / pattern
                if potential_dir.exists():
                    month_dir = potential_dir
                    break
        
        results = []
        
        if month_dir.exists() and month_dir.is_dir():
            csv_files = list(month_dir.glob('*.csv'))
            print(f"Found {len(csv_files)} CSV files")
            
            for csv_file in csv_files:
                result = self.process_single_file(csv_file, data_month)
                results.append(result)
        else:
            # Search in base path
            csv_files = list(base_path.rglob('*.csv'))
            print(f"Searching in base path, found {len(csv_files)} CSV files")
            
            for csv_file in csv_files:
                # Check if file matches the month
                file_month = self.extract_data_month_from_path(csv_file)
                if file_month and file_month == data_month:
                    result = self.process_single_file(csv_file, data_month)
                    results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r.get('success'))
        failed = len(results) - successful
        
        return {
            'success': True,
            'total_files': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL Monthly Processor')
    parser.add_argument('--file', type=str, help='Process single CSV file')
    parser.add_argument('--month', type=str, help='Process month (YYYY-MM format)')
    parser.add_argument('--path', type=str, help='Base path for CSV files')
    parser.add_argument('--cloud', action='store_true', help='Use cloud database')
    parser.add_argument('--skip-duplicates', action='store_true', default=True,
                       help='Skip already processed files')
    
    args = parser.parse_args()
    
    processor = ETLMonthlyProcessor(use_cloud=args.cloud)
    
    if args.file:
        # Process single file
        result = processor.process_single_file(
            Path(args.file),
            skip_duplicates=args.skip_duplicates
        )
        print(f"\nResult: {result}")
        
    elif args.month:
        # Process month
        try:
            data_month = datetime.strptime(args.month, '%Y-%m').date().replace(day=1)
        except ValueError:
            print("Invalid month format. Use YYYY-MM")
            sys.exit(1)
        
        base_path = Path(args.path) if args.path else None
        result = processor.process_monthly_batch(data_month, base_path)
        print(f"\nBatch Result: {result}")
    else:
        print("Please specify --file or --month")

